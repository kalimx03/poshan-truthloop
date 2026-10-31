"""Plain-language detail page for one fictional TruthLoop case."""
import html
from datetime import date, datetime

import pandas as pd
import streamlit as st

import access_control as ac
import config as cfg
import workflow as wf
from ui_common import (
    setup_page, page_hero, section_intro, get_conn, role_controls,
    scope_caption, synthetic_banner, evidence_plain, ticket_plain,
    recovery_plain, outcome_plain, action_plain, value_plain,
)

setup_page("Case detail", "detail")
conn, today = get_conn(), date.today()
role, scope, threshold, visible_cases = role_controls(conn)

if not visible_cases:
    page_hero("Case detail", "No cases in this demo view.", "Change the fictional role or area in Demo controls to view sample cases.")
    synthetic_banner()
    st.info("No fictional cases are assigned to this demo view.")
    st.stop()

ids = [c["case_id"] for c in visible_cases]
selection_key = "truthloop_case_detail_selection"
if st.session_state.get(selection_key) not in ids:
    st.session_state[selection_key] = ids[0]

selection_col, scope_col = st.columns([1.0, 1.65], gap="large")
with selection_col:
    cid = st.selectbox("Choose a fictional case", ids, key=selection_key)
with scope_col:
    st.caption(scope_caption(role, scope))

c = wf.get_case(conn, cid)
a = wf.assess(c, today, threshold)

if a["closed_receipt_unverified"]:
    hero_title = "The case is closed. We cannot confirm the family received ration."
    hero_note = "The record does not show enough to confirm that the family received ration. This does not mean ration was not received."
    receipt_label = "Not confirmed"
    box_class = "pt-outcome"
    box_title = "We do not have enough information to confirm receipt."
    box_body = "There is not enough supporting information to confirm receipt under the selected demo rule. The outcome remains unknown—not success and not proof of non-receipt."
elif a["receipt_evidenced_ticket_open"]:
    hero_title = "The record has support, but the case is still open."
    hero_note = "The record meets the selected demo rule, but the case status has not been updated."
    receipt_label = "Evidence rule met"
    box_class = "pt-outcome pt-outcome--warning"
    box_title = "The record and case status do not match yet."
    box_body = "The record meets the proposed demo rule, but the case is still open and may need an update."
elif a["outcome"] == "RECEIPT_EVIDENCED":
    hero_title = "The record meets the demo rule."
    hero_note = "This is a result from the demo rule, not an independent check of a real family's receipt."
    receipt_label = "Rule met"
    box_class = "pt-outcome pt-outcome--success"
    box_title = "The record meets the selected demo rule."
    box_body = "This result follows a rule chosen for the prototype. It is not an official standard and does not independently confirm receipt for a real family."
else:
    hero_title = "This case still needs a closer look."
    hero_note = "The case remains open. The page keeps ticket status, recovery progress and evidence separate."
    receipt_label = "Still open"
    box_class = "pt-outcome pt-outcome--warning"
    box_title = "Follow-up is still needed."
    if a["overdue_days"]:
        box_body = f"The proposed review date has passed by {a['overdue_days']} day(s). The deadline is a prototype assumption, not an official rule."
    else:
        box_body = "The case is still within the proposed review window."

page_hero(
    f"FICTIONAL CASE · {cid}",
    hero_title,
    hero_note,
    "Receipt status",
    receipt_label,
    f"Demo evidence rule: {cfg.EVIDENCE_LABELS[threshold]}",
    "This is a fictional case.",
)
synthetic_banner()

st.markdown(
    f'<div class="{box_class}"><div class="pt-outcome-title">{html.escape(box_title)}</div>'
    f'<div class="pt-outcome-body">{html.escape(box_body)}</div></div>',
    unsafe_allow_html=True,
)

section_intro("Case summary", "What the record shows")
c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("Case ticket", ticket_plain(c["ticket_status"]))
c2.metric("Recovery step", recovery_plain(c["recovery_status"]))
c3.metric("Receipt record", evidence_plain(c["evidence_level"]))
c4.metric("Review level · proposed", cfg.ESCALATION_LADDER[c["escalation_level"]])

person = {
    "Child 6m-3y": "Child aged 6 months to 3 years",
    "Pregnant woman": "Pregnant woman",
    "Lactating mother": "Lactating mother",
    "Adolescent girl": "Adolescent girl",
}.get(c["beneficiary_group"], c["beneficiary_group"])
issue = {
    "Face match failed": "Face match did not work",
    "Mother's match failed": "Mother's face match did not work",
    "No connectivity": "No internet connection",
    "OTP failed": "One-time code did not work",
}.get(c["exception_reason"], c["exception_reason"])
area = c["district"].replace("Synthetic District ", "Demo area ")
block = c["block"].replace("Synthetic Block ", "Block ")
st.markdown(
    f'<div class="pt-notice"><strong>Fictional case details</strong> &nbsp; {html.escape(person)} · {html.escape(issue)} · '
    f'{html.escape(area)}, {html.escape(block)} · All names and locations are fictional.</div>',
    unsafe_allow_html=True,
)
st.caption(
    f"Recovery route in this example: {c['recovery_route']} · Opened {c['opened_on']} · "
    f"Proposed review date {c['due_on']} · A review date is a demo assumption."
)

with st.expander("Record a follow-up action · demo controls", expanded=False):
    st.caption("These controls demonstrate a proposed workflow. The selected role is simulated and does not authenticate a real person.")
    actor = role
    fields = ac.allowed_action_fields(c, actor)
    if not fields:
        st.info("This demo role has no permitted next action on the selected case.")
    else:
        field_labels = {
            "ticket_status": "Ticket status",
            "recovery_status": "Recovery step",
            "evidence_level": "Evidence on file",
            "escalation_level": "Review level",
        }
        field = st.selectbox(
            "What do you want to update?",
            fields,
            format_func=lambda x: field_labels.get(x, x.replace("_", " ").title()),
            key="case_field",
        )
        if field in ("recovery_status", "ticket_status"):
            options = sorted(wf.ALLOWED[field].get(c[field], set()))
        elif field == "evidence_level":
            max_rank = cfg.EVIDENCE_RANK[cfg.ROLE_MAX_EVIDENCE[actor]]
            options = [k for k, v in cfg.EVIDENCE_RANK.items() if cfg.EVIDENCE_RANK[c[field]] < v <= max_rank]
        else:
            candidate = int(c["escalation_level"]) + 1
            options = [str(candidate)] if candidate in cfg.ESCALATION_LADDER and candidate <= cfg.ROLE_MAX_ESCALATION[actor] else []
        new = st.selectbox(
            "New value",
            options,
            format_func=lambda x: value_plain(field, x),
            key="case_new_value",
        ) if options else None
        reason = st.text_input("Why is this change being made? (required)", key="case_action_reason")
        if st.button("Save change", type="primary", disabled=(new is None), key="case_apply_action"):
            try:
                wf.update_case(
                    conn, cid, field, int(new) if field == "escalation_level" else new,
                    actor, reason, datetime.now().isoformat(timespec="seconds"),
                )
                st.session_state.pop("case_action_reason", None)
                st.rerun()
            except ValueError as e:
                st.error(str(e))

section_intro("Case history", "What happened and when", "Each accepted change is recorded with a time, role and reason.")
event_rows = [dict(r) for r in conn.execute("SELECT * FROM events WHERE case_id=? ORDER BY id", (cid,))]
if event_rows:
    pretty = []
    role_labels = {
        "Anganwadi Worker": "Anganwadi worker",
        "System (proposed rule)": "Proposed system rule",
    }
    for event in event_rows:
        field = event["field"]
        pretty.append({
            "When": event["ts"].replace("T", " "),
            "Who": role_labels.get(event["actor_role"], event["actor_role"]),
            "What changed": {
                "CASE_OPENED": "Case created",
                "SET_TICKET_STATUS": "Ticket status changed",
                "SET_RECOVERY_STATUS": "Recovery step updated",
                "SET_EVIDENCE_LEVEL": "Evidence record updated",
                "SET_ESCALATION_LEVEL": "Review level raised",
            }.get(event["action"], event["action"].replace("_", " ").title()),
            "Before": value_plain(field, event["old_value"]),
            "After": value_plain(field, event["new_value"]),
            "Why": event["reason"],
        })
    st.dataframe(pd.DataFrame(pretty), width="stretch", hide_index=True)
else:
    st.info("No changes are recorded for this fictional case yet.")

with st.expander("Technical checks · for reviewers", expanded=False):
    st.caption("This SHA-256 chain can reveal changes that break the recorded chain. It is tamper-evident, not immutable.")
    b1, b2, b3 = st.columns(3)
    if b1.button("Verify audit chain", key="verify_audit_chain"):
        ok, bad = wf.verify_chain(conn)
        if ok:
            st.success("Audit chain intact.")
        else:
            st.error(f"Chain broken at event #{bad}. A stored record was altered.")
    if role == "District Programme Officer":
        if b2.button("Demo: edit a stored event", key="tamper_audit_chain"):
            conn.execute(
                "UPDATE events SET reason='(edited outside the app)' WHERE id=(SELECT MIN(id) FROM events WHERE case_id=?)",
                (cid,),
            )
            st.warning("A fictional event was edited directly in the database. Click Verify audit chain to detect it.")
        if b3.button("Reset demo cases", key="reset_demo_data"):
            get_conn(reset=True)
            st.rerun()
    else:
        b2.caption("Edit demonstration is available only in the simulated District Programme Officer view.")
        b3.caption("Reset is available only in the simulated District Programme Officer view.")
    with st.expander("Raw technical event records", expanded=False):
        st.dataframe(pd.DataFrame(event_rows)[["ts", "actor_role", "action", "field", "old_value", "new_value", "reason", "prev_hash", "hash"]], width="stretch", hide_index=True)

st.markdown('<div class="pt-footer">POSHAN TRUTHLOOP · Independent student prototype · This case is fictional.</div>', unsafe_allow_html=True)
