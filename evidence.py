from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"
NATIONAL = {"eligible": 43732621, "matched": 42800299, "reported_pct": 97.87, "as_of": "June 2026"}
TREND = [("Jul 2025", 70.82), ("Jun 2026", 97.87)]


def national():
    n = dict(NATIONAL)
    n["unmatched"] = n["eligible"] - n["matched"]
    n["rate_calc"] = round(100 * n["matched"] / n["eligible"], 2)
    return n


def load_states():
    df = pd.read_csv(DATA / "annexure_states_june2026.csv")
    df["unmatched"] = df["eligible"] - df["matched"]
    df["rate_calc"] = (100 * df["matched"] / df["eligible"]).round(2)
    return df


def load_ledger():
    return pd.read_csv(DATA / "source_ledger.csv")


def reconcile(df):
    n = national()
    s_el, s_ma = int(df["eligible"].sum()), int(df["matched"].sum())
    el_diff, ma_diff = s_el - n["eligible"], s_ma - n["matched"]
    bad_rows = df[(df["rate_calc"] - df["reported_pct"]).abs() > 0.011]["state"].tolist()
    ok = (s_el == n["eligible"]) and (s_ma == n["matched"])
    return {
        "ok": ok, "state_sum_eligible": s_el, "state_sum_matched": s_ma,
        "eligible_diff": el_diff, "matched_diff": ma_diff,
        "state_sum_unmatched": s_el - s_ma, "national_unmatched": n["unmatched"],
        "rows_with_rate_mismatch": bad_rows,
    }


def aggregate_claims_allowed(rec):
    return bool(rec["ok"])
