"""Prototype assumptions. These are proposed design choices, not government rules."""
EVIDENCE_RANK = {"E0": 0, "E1": 1, "E2": 2, "E3": 3}
EVIDENCE_LABELS = {
    "E0": "No evidence",
    "E1": "Distribution recorded",
    "E2": "Distribution corroborated",
    "E3": "Beneficiary-side confirmation (proposed sampled check)",
}
EVIDENCE_THRESHOLD = "E2"
THRESHOLD_OPTIONS = ["E2", "E3"]
SLA_DAYS = 7
ESCALATION_LADDER = {0: "Anganwadi Worker", 1: "Supervisor", 2: "CDPO", 3: "District Programme Officer"}
ESCALATION_TRIGGER_OVERDUE_DAYS = {1: 1, 2: 4, 3: 8}
USER_ROLES = ["Anganwadi Worker", "Supervisor", "CDPO", "District Programme Officer"]
SYSTEM_ROLE = "System (proposed rule)"
ROLES = USER_ROLES + [SYSTEM_ROLE]

# Proposed demo permissions. These simulate decision rights; they are not authentication.
ROLE_MAX_EVIDENCE = {
    "Anganwadi Worker": "E1",
    "Supervisor": "E2",
    "CDPO": "E3",
    "District Programme Officer": "E3",
    SYSTEM_ROLE: "E3",
}
ROLE_MAX_ESCALATION = {
    "Anganwadi Worker": 0,
    "Supervisor": 1,
    "CDPO": 2,
    "District Programme Officer": 3,
    SYSTEM_ROLE: 3,
}
ROLE_ALLOWED_FIELDS = {
    "Anganwadi Worker": {"ticket_status", "recovery_status", "evidence_level"},
    "Supervisor": {"ticket_status", "recovery_status", "evidence_level", "escalation_level"},
    "CDPO": {"ticket_status", "recovery_status", "evidence_level", "escalation_level"},
    "District Programme Officer": {"ticket_status", "recovery_status", "evidence_level", "escalation_level"},
    SYSTEM_ROLE: {"escalation_level"},
}
