import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import evidence as ev


def test_national_unmatched():
    assert ev.national()["unmatched"] == 932322


def test_national_rate_matches_reported():
    n = ev.national()
    assert n["rate_calc"] == n["reported_pct"]


def test_each_state_rate_recomputes():
    assert ev.reconcile(ev.load_states())["rows_with_rate_mismatch"] == []


def test_state_rows_do_not_reconcile_and_gate_closes():
    rec = ev.reconcile(ev.load_states())
    assert rec["ok"] is False
    assert rec["eligible_diff"] == 4015925
    assert ev.aggregate_claims_allowed(rec) is False


def test_row_count():
    assert len(ev.load_states()) == 36


def test_reconciliation_gate_requires_exact_integer_totals():
    df = ev.load_states().copy()
    # Change a single count by one: integer totals no longer match and the gate must close.
    df.loc[0, "eligible"] += 1
    rec = ev.reconcile(df)
    assert rec["ok"] is False
