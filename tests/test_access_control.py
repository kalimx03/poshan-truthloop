from datetime import date
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import access_control as ac
import config as cfg
import workflow as wf


def demo_cases():
    conn = wf.connect()
    wf.seed(conn, date(2026, 11, 2))
    return wf.list_cases(conn)


def test_role_scope_counts_and_boundaries():
    cases = demo_cases()
    awc_options = ac.scope_options(cases, "Anganwadi Worker")
    block_options = ac.scope_options(cases, "Supervisor")
    district_options = ac.scope_options(cases, "CDPO")
    assert len(awc_options) == 6
    assert len(block_options) == 6
    assert len(district_options) == 3
    assert len(ac.filter_visible_cases(cases, "Anganwadi Worker", awc_options[0])) == 2
    assert len(ac.filter_visible_cases(cases, "Supervisor", block_options[0])) == 2
    assert len(ac.filter_visible_cases(cases, "CDPO", district_options[0])) == 4
    assert len(ac.filter_visible_cases(cases, "District Programme Officer", None)) == 12


def test_worker_cannot_record_above_e1_and_cannot_escalate():
    conn = wf.connect()
    today = date(2026, 11, 2)
    wf.create_case(conn, "SYN-PERM", "Synthetic District A", "Pregnant woman", "Exception", "Offline match", today.isoformat(), "2026-11-02T09:00:00")
    with pytest.raises(ValueError, match="cannot record evidence above E1"):
        wf.update_case(conn, "SYN-PERM", "evidence_level", "E2", "Anganwadi Worker", "attempt", "2026-11-02T10:00:00")
    with pytest.raises(ValueError, match="not permitted"):
        wf.update_case(conn, "SYN-PERM", "escalation_level", 1, "Anganwadi Worker", "attempt", "2026-11-02T10:00:00")


def test_open_ticket_can_have_evidence_met_and_stays_separately_visible():
    cases = {c["case_id"]: c for c in demo_cases()}
    case = cases["SYN-012"]
    assert case["ticket_status"] == "OPEN"
    assert case["evidence_level"] == "E3"
    assessed = wf.assess(case, date(2026, 11, 2), threshold="E2")
    assert assessed["outcome"] == "RECEIPT_EVIDENCED"
    assert assessed["receipt_evidenced_ticket_open"] is True
    assert assessed["closed_receipt_unverified"] is False


def test_scoped_escalation_does_not_mutate_other_centres():
    conn = wf.connect()
    today = date(2026, 11, 2)
    wf.seed(conn, today)
    before = {c["case_id"]: c["escalation_level"] for c in wf.list_cases(conn)}
    one_case = wf.get_case(conn, "SYN-008")
    allowed = [one_case["case_id"]]
    wf.apply_escalations(conn, today, "2026-11-02T12:00:00", allowed_case_ids=allowed, requested_by="Supervisor")
    after = {c["case_id"]: c["escalation_level"] for c in wf.list_cases(conn)}
    assert after["SYN-008"] >= before["SYN-008"]
    assert all(after[cid] == before[cid] for cid in before if cid != "SYN-008")

