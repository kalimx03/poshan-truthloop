import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import config as cfg
import workflow as wf

TODAY = date(2026, 11, 2)
TS = "2026-11-02T09:00:00"


def fresh():
    conn = wf.connect()
    wf.seed(conn, TODAY)
    return conn


def one_case():
    conn = wf.connect()
    wf.create_case(conn, "SYN-X", "Synthetic District A", "Pregnant woman", "Face match failed", "Nominee", "2026-11-01", TS)
    return conn


def test_closing_ticket_does_not_change_evidence():
    conn = one_case()
    wf.update_case(conn, "SYN-X", "ticket_status", "CLOSED", "Anganwadi Worker", "closed", TS)
    c = wf.get_case(conn, "SYN-X")
    assert c["ticket_status"] == "CLOSED" and c["evidence_level"] == "E0"
    assert wf.assess(c)["closed_receipt_unverified"] is True


def test_evidence_threshold_controls_outcome():
    conn = one_case()
    wf.update_case(conn, "SYN-X", "evidence_level", "E2", "Supervisor", "corroborated", TS)
    wf.update_case(conn, "SYN-X", "ticket_status", "CLOSED", "Anganwadi Worker", "closed", TS)
    c = wf.get_case(conn, "SYN-X")
    assert wf.assess(c, threshold="E2")["outcome"] == "RECEIPT_EVIDENCED"
    assert wf.assess(c, threshold="E3")["outcome"] == "OUTCOME_UNKNOWN"


def test_invalid_transitions_and_missing_reason_rejected():
    conn = one_case()
    with pytest.raises(ValueError):
        wf.update_case(conn, "SYN-X", "recovery_status", "COMPLETED", "Anganwadi Worker", "skip", TS)
    with pytest.raises(ValueError):
        wf.update_case(conn, "SYN-X", "ticket_status", "CLOSED", "Anganwadi Worker", "  ", TS)
    with pytest.raises(ValueError):
        wf.update_case(conn, "SYN-X", "evidence_level", "E0", "Supervisor", "downgrade", TS)


def test_seed_contains_flagship_case():
    cases = wf.list_cases(fresh())
    flagged = [c for c in cases if wf.assess(c, TODAY)["closed_receipt_unverified"]]
    assert len(cases) == 12 and any(c["evidence_level"] == "E0" and c["ticket_status"] == "CLOSED" for c in flagged)


def test_escalation_follows_configured_ladder():
    conn = fresh()
    for c in wf.list_cases(conn):
        a = wf.assess(c, TODAY)
        if c["ticket_status"] == "OPEN":
            expect = max([l for l, d in cfg.ESCALATION_TRIGGER_OVERDUE_DAYS.items() if a["overdue_days"] >= d] or [0])
            assert c["escalation_level"] == expect
        else:
            assert c["escalation_level"] == 0


def test_audit_chain_ok_then_tamper_detected():
    conn = fresh()
    assert wf.verify_chain(conn) == (True, None)
    conn.execute("UPDATE events SET reason='edited' WHERE id=3")
    ok, bad = wf.verify_chain(conn)
    assert ok is False and bad == 3


def test_schema_has_no_sensitive_fields():
    conn = wf.connect()
    cols = [r[1].lower() for t in ("cases", "events") for r in conn.execute(f"PRAGMA table_info({t})")]
    for banned in ("aadhaar", "biometric", "face", "photo", "phone", "name", "image"):
        assert not any(banned in c for c in cols)
