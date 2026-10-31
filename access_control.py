"""Role-scoping helpers for the synthetic demo. Not production authentication."""
from typing import Iterable

import config as cfg

ROLE_SCOPE_FIELD = {
    "Anganwadi Worker": "awc_code",
    "Supervisor": "block",
    "CDPO": "district",
    "District Programme Officer": None,
}


def scope_options(cases: Iterable[dict], role: str) -> list[str]:
    field = ROLE_SCOPE_FIELD.get(role)
    if field is None:
        return ["All districts"]
    return sorted({str(c[field]) for c in cases if c.get(field)})


def filter_visible_cases(cases: Iterable[dict], role: str, scope: str | None) -> list[dict]:
    cases = list(cases)
    if role == "District Programme Officer":
        return sorted(cases, key=lambda c: c["case_id"])
    field = ROLE_SCOPE_FIELD.get(role)
    if not field or not scope:
        return []
    return sorted((c for c in cases if str(c.get(field)) == scope), key=lambda c: c["case_id"])


def can_view_case(case: dict, role: str, scope: str | None) -> bool:
    return case in filter_visible_cases([case], role, scope)


def allowed_fields(role: str) -> set[str]:
    return set(cfg.ROLE_ALLOWED_FIELDS.get(role, set()))


def can_change_value(role: str, field: str, value) -> bool:
    if field not in allowed_fields(role):
        return False
    if field == "evidence_level":
        if value not in cfg.EVIDENCE_RANK:
            return False
        max_level = cfg.ROLE_MAX_EVIDENCE.get(role, "E0")
        return cfg.EVIDENCE_RANK[value] <= cfg.EVIDENCE_RANK[max_level]
    if field == "escalation_level":
        try:
            return int(value) <= int(cfg.ROLE_MAX_ESCALATION.get(role, -1))
        except (TypeError, ValueError):
            return False
    return True


def allowed_action_fields(case: dict, role: str) -> list[str]:
    """Return only fields with at least one permitted next value for this role."""
    fields = []
    for field in ("recovery_status", "evidence_level", "ticket_status", "escalation_level"):
        if field not in allowed_fields(role):
            continue
        if field == "recovery_status":
            values = {"NOT_STARTED": ["IN_PROGRESS"], "IN_PROGRESS": ["COMPLETED"], "COMPLETED": []}.get(case[field], [])
        elif field == "ticket_status":
            values = {"OPEN": ["CLOSED"], "CLOSED": ["OPEN"]}.get(case[field], [])
        elif field == "evidence_level":
            max_rank = cfg.EVIDENCE_RANK[cfg.ROLE_MAX_EVIDENCE.get(role, "E0")]
            values = [v for v, rank in cfg.EVIDENCE_RANK.items() if cfg.EVIDENCE_RANK[case[field]] < rank <= max_rank]
        else:
            cur = int(case["escalation_level"])
            candidate = cur + 1
            values = [candidate] if candidate in cfg.ESCALATION_LADDER and candidate <= cfg.ROLE_MAX_ESCALATION.get(role, -1) else []
        if values:
            fields.append(field)
    return fields
