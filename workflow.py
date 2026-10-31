import hashlib
import json
import sqlite3
from datetime import date, timedelta

import config as cfg

GENESIS = "0" * 64
SCHEMA = """
CREATE TABLE IF NOT EXISTS cases(
 case_id TEXT PRIMARY KEY, district TEXT, block TEXT, awc_code TEXT, beneficiary_group TEXT, exception_reason TEXT,
 recovery_route TEXT, opened_on TEXT, due_on TEXT, ticket_status TEXT, recovery_status TEXT,
 evidence_level TEXT, escalation_level INTEGER);
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, case_id TEXT, actor_role TEXT, action TEXT,
 reason TEXT, field TEXT, old_value TEXT, new_value TEXT, prev_hash TEXT, hash TEXT);
"""
ALLOWED = {
    "ticket_status": {"OPEN": {"CLOSED"}, "CLOSED": {"OPEN"}},
    "recovery_status": {"NOT_STARTED": {"IN_PROGRESS"}, "IN_PROGRESS": {"COMPLETED"}, "COMPLETED": set()},
}


def connect():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _hash(prev, e):
    return hashlib.sha256((prev + json.dumps(e, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()


def _event_dict(r):
    return {k: r[k] for k in ("ts", "case_id", "actor_role", "action", "reason", "field", "old_value", "new_value")}


def _log(conn, ts, case_id, actor, action, reason, field, old, new):
    last = conn.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    prev = last["hash"] if last else GENESIS
    e = dict(ts=ts, case_id=case_id, actor_role=actor, action=action, reason=reason,
             field=field, old_value=str(old), new_value=str(new))
    conn.execute("INSERT INTO events(ts,case_id,actor_role,action,reason,field,old_value,new_value,prev_hash,hash) "
                 "VALUES(?,?,?,?,?,?,?,?,?,?)",
                 (e["ts"], case_id, actor, action, reason, field, e["old_value"], e["new_value"], prev, _hash(prev, e)))


def verify_chain(conn):
    prev = GENESIS
    for r in conn.execute("SELECT * FROM events ORDER BY id"):
        if r["prev_hash"] != prev or _hash(prev, _event_dict(r)) != r["hash"]:
            return False, r["id"]
        prev = r["hash"]
    return True, None


def create_case(conn, case_id, district, group, reason, route, opened_on, ts,
                actor="Anganwadi Worker", block=None, awc_code=None):
    due = (date.fromisoformat(opened_on) + timedelta(days=cfg.SLA_DAYS)).isoformat()
    # Organizational labels are fictional and exist only to demonstrate proposed scope rules.
    block = block or "Synthetic Block 1"
    awc_code = awc_code or "SYN-AWC-01"
    conn.execute("INSERT INTO cases VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (case_id, district, block, awc_code, group, reason, route, opened_on, due,
                  "OPEN", "NOT_STARTED", "E0", 0))
    _log(conn, ts, case_id, actor, "CASE_OPENED", f"Synthetic exception: {reason}", "ticket_status", "-", "OPEN")


def get_case(conn, case_id):
    return dict(conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone())


def list_cases(conn):
    return [dict(r) for r in conn.execute("SELECT * FROM cases ORDER BY case_id")]


def update_case(conn, case_id, field, new, actor, reason, ts):
    if not reason or not reason.strip():
        raise ValueError("A reason is required for every change.")
    if actor not in cfg.ROLES:
        raise ValueError("Unknown actor role.")
    old = get_case(conn, case_id)[field] if field in ALLOWED or field in ("evidence_level", "escalation_level") else None
    permitted_fields = cfg.ROLE_ALLOWED_FIELDS.get(actor, set())
    if field not in permitted_fields:
        raise ValueError(f"Role '{actor}' is not permitted to change {field} under the proposed demo rules.")
    if field in ALLOWED:
        if new not in ALLOWED[field].get(old, set()):
            raise ValueError(f"{field}: {old} -> {new} is not an allowed transition.")
    elif field == "evidence_level":
        if new not in cfg.EVIDENCE_RANK or cfg.EVIDENCE_RANK[new] <= cfg.EVIDENCE_RANK[old]:
            raise ValueError("Evidence level can only increase.")
        max_level = cfg.ROLE_MAX_EVIDENCE.get(actor, "E0")
        if cfg.EVIDENCE_RANK[new] > cfg.EVIDENCE_RANK[max_level]:
            raise ValueError(f"Role '{actor}' cannot record evidence above {max_level} under the proposed demo rules.")
    elif field == "escalation_level":
        if int(new) != int(old) + 1 or int(new) not in cfg.ESCALATION_LADDER:
            raise ValueError("Escalation moves up one level at a time, up to the top of the ladder.")
        if int(new) > cfg.ROLE_MAX_ESCALATION.get(actor, -1):
            raise ValueError(f"Role '{actor}' cannot escalate above {cfg.ESCALATION_LADDER[cfg.ROLE_MAX_ESCALATION.get(actor, 0)]} under the proposed demo rules.")
    else:
        raise ValueError("This field cannot be edited.")
    conn.execute(f"UPDATE cases SET {field}=? WHERE case_id=?", (new, case_id))
    _log(conn, ts, case_id, actor, f"SET_{field.upper()}", reason, field, old, new)


def assess(case, today=None, threshold=None):
    """Compute receipt outcome from evidence independently of ticket status.

    RECEIPT_EVIDENCED can coexist with an OPEN ticket; that mirror case is deliberately
    surfaced because administrative tracking may lag the recorded evidence.
    """
    thr = threshold or cfg.EVIDENCE_THRESHOLD
    closed = case["ticket_status"] == "CLOSED"
    enough = cfg.EVIDENCE_RANK[case["evidence_level"]] >= cfg.EVIDENCE_RANK[thr]
    if enough:
        outcome = "RECEIPT_EVIDENCED"
    elif closed:
        outcome = "OUTCOME_UNKNOWN"
    else:
        outcome = "STILL_OPEN"
    overdue = 0
    if today and not closed:
        overdue = max(0, (today - date.fromisoformat(case["due_on"])).days)
    return {
        "outcome": outcome,
        "closed_receipt_unverified": closed and not enough,
        "receipt_evidenced_ticket_open": (not closed) and enough,
        "overdue_days": overdue,
    }


def apply_escalations(conn, today, ts, allowed_case_ids=None, requested_by=None):
    """Apply proposed escalation rules globally or only to explicitly scoped cases."""
    n = 0
    allowed = set(allowed_case_ids) if allowed_case_ids is not None else None
    for c in list_cases(conn):
        if allowed is not None and c["case_id"] not in allowed:
            continue
        a = assess(c, today)
        if c["ticket_status"] != "OPEN":
            continue
        target = max([lvl for lvl, d in cfg.ESCALATION_TRIGGER_OVERDUE_DAYS.items() if a["overdue_days"] >= d] or [0])
        while c["escalation_level"] < target:
            reason = f"Overdue {a['overdue_days']} days; proposed escalation ladder"
            if requested_by:
                reason += f"; triggered from {requested_by} view"
            update_case(conn, c["case_id"], "escalation_level", c["escalation_level"] + 1,
                        cfg.SYSTEM_ROLE, reason, ts)
            c["escalation_level"] += 1
            n += 1
    return n


SEED = [  # group, reason, route, days_ago, recovery, evidence, close
    ("Pregnant woman", "Face match failed", "Offline match", 20, "COMPLETED", "E0", True),
    ("Lactating mother", "OTP failed", "Helpline ticket", 18, "COMPLETED", "E1", True),
    ("Pregnant woman", "Face match failed", "Nominee", 15, "COMPLETED", "E2", True),
    ("Child 6m-3y", "Mother's match failed", "Offline match", 14, "COMPLETED", "E3", True),
    ("Lactating mother", "No connectivity", "Offline match", 3, "IN_PROGRESS", "E0", False),
    ("Pregnant woman", "Face match failed", "Nominee", 9, "IN_PROGRESS", "E0", False),
    ("Child 6m-3y", "Mother's match failed", "Helpline ticket", 12, "NOT_STARTED", "E0", False),
    ("Lactating mother", "OTP failed", "Re-registration", 17, "NOT_STARTED", "E0", False),
    ("Adolescent girl", "Face match failed", "Nominee", 2, "NOT_STARTED", "E0", False),
    ("Pregnant woman", "No connectivity", "Helpline ticket", 11, "COMPLETED", "E0", True),
    ("Lactating mother", "Face match failed", "Nominee", 10, "COMPLETED", "E2", True),
    ("Child 6m-3y", "OTP failed", "Offline match", 10, "COMPLETED", "E3", False),
]
DISTRICTS = ["Synthetic District A", "Synthetic District B", "Synthetic District C"]


def seed(conn, today):
    for i, (grp, reason, route, ago, rec, ev, close) in enumerate(SEED, start=1):
        cid = f"SYN-{i:03d}"
        opened = today - timedelta(days=ago)
        t0 = f"{opened.isoformat()}T09:00:00"
        t1 = f"{(opened + timedelta(days=1)).isoformat()}T10:00:00"
        t2 = f"{(opened + timedelta(days=3)).isoformat()}T11:00:00"
        # Six fictional centres, two cases per centre; two centres per fictional district.
        centre_ix = (i - 1) // 2
        district_ix = centre_ix // 2
        district = DISTRICTS[district_ix]
        block = f"Synthetic Block {chr(65 + district_ix)}{(centre_ix % 2) + 1}"
        awc_code = f"SYN-AWC-{chr(65 + district_ix)}{(centre_ix % 2) + 1}"
        create_case(conn, cid, district, grp, reason, route, opened.isoformat(), t0,
                    block=block, awc_code=awc_code)
        if rec in ("IN_PROGRESS", "COMPLETED"):
            update_case(conn, cid, "recovery_status", "IN_PROGRESS", "Anganwadi Worker", f"Started recovery via {route}", t1)
        if rec == "COMPLETED":
            update_case(conn, cid, "recovery_status", "COMPLETED", "Anganwadi Worker", "Recovery action recorded as completed", t2)
        if ev != "E0":
            evidence_actor = "CDPO" if ev == "E3" else "Supervisor"
            update_case(conn, cid, "evidence_level", ev, evidence_actor,
                        f"Evidence recorded: {cfg.EVIDENCE_LABELS[ev]}", t2)
        if close:
            update_case(conn, cid, "ticket_status", "CLOSED", "Anganwadi Worker", "Ticket closed by worker", t2)
    apply_escalations(conn, today, f"{today.isoformat()}T08:00:00")
