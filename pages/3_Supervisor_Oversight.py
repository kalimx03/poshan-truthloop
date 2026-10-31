"""Plain-language oversight view for fictional TruthLoop cases."""
from datetime import date, datetime
import html

import pandas as pd
import streamlit as st

import config as cfg
import workflow as wf
from ui_common import (
    setup_page, page_hero, section_intro, get_conn, role_controls,
    scope_caption, synthetic_banner, evidence_plain, ticket_plain,
    recovery_plain, outcome_plain, issue_plain,
)

setup_page("Supervisor view", "oversight")
conn, today = get_conn(), date.today()
role, scope, threshold, visible_cases = role_controls(conn)

if not visible_cases:
    page_hero("Supervisor view", "No cases in this demo view.", "Change the fictional role or area in Demo controls to view sample cases.")
    synthetic_banner()
    st.info("No fictional cases are assigned to this demo view.")
    st.stop()

rows = []
for c in visible_cases:
    a = wf.assess(c, today, threshold)
    if a["closed_receipt_unverified"]:
        attention = "Closed — receipt not confirmed"
        rank = 0
    elif a["receipt_evidenced_ticket_open"]:
        attention = "Supporting record · case still open"
        rank = 1
    elif c["ticket_status"] == "OPEN" and a["overdue_days"] > 0:
        attention = "Open — review date passed"
        rank = 2
    elif a["outcome"] == "RECEIPT_EVIDENCED":
        attention = "Evidence meets demo rule"
        rank = 3
    else:
        attention = "Open — within review window"
        rank = 4
    rows.append({
        "case": c,
        "assessment": a,
        "attention": attention,
        "rank": rank,
        "issue": issue_plain(c["exception_reason"]),
        "person": {
            "Child 6m-3y": "Child aged 6 months to 3 years",
            "Pregnant woman": "Pregnant woman",
            "Lactating mother": "Lactating mother",
            "Adolescent girl": "Adolescent girl",
        }.get(c["beneficiary_group"], c["beneficiary_group"]),
    })
rows.sort(key=lambda r: (r["rank"], -r["assessment"]["overdue_days"], r["case"]["case_id"]))

closed_unverified = sum(r["assessment"]["closed_receipt_unverified"] for r in rows)
evidence_ticket_open = sum(r["assessment"]["receipt_evidenced_ticket_open"] for r in rows)
open_cases = sum(r["case"]["ticket_status"] == "OPEN" for r in rows)
open_overdue = sum(r["case"]["ticket_status"] == "OPEN" and r["assessment"]["overdue_days"] > 0 for r in rows)
needs_attention = sum(r["rank"] < 3 for r in rows)

page_hero(
    "Supervisor view · fictional demonstration",
    "Where should we look next?",
    "This view brings together cases where receipt is not confirmed, a review date has passed, or the case status does not match the record.",
    "Cases to check",
    str(needs_attention),
    "Fictional examples in the current demo view.",
    "These numbers are not real programme statistics.",
)
synthetic_banner()
st.caption(scope_caption(role, scope))

section_intro("Summary", "Cases to look at")
m1, m2, m3, m4 = st.columns(4, gap="medium")
m1.metric("Cases still open", open_cases)
m2.metric("Past proposed review date", open_overdue)
m3.metric("Closed · receipt not confirmed", closed_unverified)
m4.metric("Supporting record · case open", evidence_ticket_open)
st.caption(f"The displayed outcomes use the selected demo evidence rule: {cfg.EVIDENCE_LABELS[threshold]}. This is a design assumption, not a government standard.")

section_intro("Follow-up queue", "Start with these cases", "Cases with unclear records or overdue follow-up appear first. Every case below is fictional.")
queue = [r for r in rows if r["rank"] < 3]
if not queue:
    st.info("No cases are flagged for follow-up in this simulated role's current view.")
else:
    for r in queue:
        c, a = r["case"], r["assessment"]
        with st.container(border=True):
            left, middle, right = st.columns([.82, 3.25, 1.05], gap="medium", vertical_alignment="center")
            with left:
                st.markdown(f"**{c['case_id']}**")
                if r["rank"] == 0:
                    st.markdown('<span class="pt-case-status pt-case-status--alert">Receipt not confirmed</span>', unsafe_allow_html=True)
                elif r["rank"] == 1:
                    st.markdown('<span class="pt-case-status">Ticket still open</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pt-case-status pt-case-status--alert">Past review date</span>', unsafe_allow_html=True)
            with middle:
                st.markdown(f"**{html.escape(r['attention'])}**")
                st.write(r["issue"] + ". " + (
                    "The record is below the selected evidence rule."
                    if r["rank"] == 0 else
                    "Some supporting information is recorded, but the case is still open."
                    if r["rank"] == 1 else
                    f"The proposed review date passed {a['overdue_days']} day(s) ago."
                ))
                st.caption(f"{r['person']} · {c['district'].replace('Synthetic District ', 'Demo area ')} · Evidence on file: {evidence_plain(c['evidence_level'])}")
            with right:
                if st.button("Open case", key=f"oversight_open_{c['case_id']}", type="primary", use_container_width=True):
                    st.session_state["truthloop_case_detail_selection"] = c["case_id"]
                    st.switch_page("pages/2_Case_Detail.py")

with st.expander("See the proposed escalation pathway", expanded=False):
    st.caption("This ladder is a prototype assumption for discussion. It is not presented as an existing government rule.")
    st.markdown(
        "1. **Anganwadi worker:** records the exception and first follow-up.\n"
        "2. **Supervisor:** reviews unresolved records and supports the next step.\n"
        "3. **CDPO:** reviews cases that remain unresolved under the proposed rule.\n"
        "4. **District Programme Officer:** reviews cases reaching the final proposed level."
    )
    if role in ("Supervisor", "CDPO", "District Programme Officer"):
        if st.button("Apply proposed escalation to cases in this view", type="primary"):
            count = wf.apply_escalations(
                conn,
                today,
                datetime.now().isoformat(timespec="seconds"),
                allowed_case_ids=[r["case"]["case_id"] for r in rows],
                requested_by=role,
            )
            st.success(f"Recorded {count} proposed escalation step(s) for the fictional cases in this view.")
            st.rerun()
    else:
        st.info("This simulated role can review cases but cannot run the escalation demonstration.")

with st.expander("Technical summary for reviewers", expanded=False):
    tech = []
    for r in rows:
        c, a = r["case"], r["assessment"]
        tech.append({
            "Case": c["case_id"], "Ticket status": c["ticket_status"],
            "Recovery status": c["recovery_status"], "Evidence level": c["evidence_level"],
            "Computed outcome": a["outcome"], "Review level (proposed)": cfg.ESCALATION_LADDER[c["escalation_level"]],
            "Days past proposed review date": a["overdue_days"],
        })
    st.dataframe(pd.DataFrame(tech), width="stretch", hide_index=True)
    st.markdown(
        "- A ticket closed below the evidence threshold is shown as receipt not confirmed, not as proof of non-receipt.\n"
        "- An open ticket with evidence meeting the selected threshold is shown separately.\n"
        "- Role scope, evidence thresholds, review dates and escalation steps are proposed demo assumptions.\n"
        "- The role selector demonstrates decision rights; it is not production authentication."
    )

st.markdown('<div class="pt-footer">POSHAN TRUTHLOOP · Fictional cases only · Proposed review and escalation rules require programme-owner validation.</div>', unsafe_allow_html=True)
