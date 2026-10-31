"""Plain-language case queue for the Poshan TruthLoop prototype."""
from datetime import date
import html

import pandas as pd
import streamlit as st

import config as cfg
import workflow as wf
from ui_common import (
    setup_page, page_hero, section_intro, get_conn, role_controls,
    scope_caption, synthetic_banner, evidence_plain, ticket_plain,
    recovery_plain, issue_plain,
)


setup_page("Case Workbench", "cases")
conn, today = get_conn(), date.today()
role, scope, threshold, visible_cases = role_controls(conn)

if not visible_cases:
    page_hero(
        "Case workbench · fictional demonstration",
        "No cases in this demo view yet.",
        "Change the fictional role or area in Demo controls to view the sample cases.",
    )
    synthetic_banner()
    st.stop()

records = []
for c in visible_cases:
    a = wf.assess(c, today, threshold)
    if a["closed_receipt_unverified"]:
        flag = "Closed · receipt not confirmed"
        rank = 0
        short = (
            "The case is marked closed, but there is no supporting record to confirm that "
            "the family received ration. This does not prove ration was not received."
        )
    elif a["receipt_evidenced_ticket_open"]:
        flag = "Supporting record · case still open"
        rank = 1
        short = (
            "Some supporting information is recorded, but the case is still open. "
            "A reviewer may need to update its status."
        )
    elif c["ticket_status"] == "OPEN" and a["overdue_days"] > 0:
        flag = "Open · review date passed"
        rank = 2
        short = (
            "The case is still open and its proposed review date has passed. "
            "The date is a prototype assumption, not an official deadline."
        )
    elif a["outcome"] == "RECEIPT_EVIDENCED":
        flag = "Record meets demo rule"
        rank = 3
        short = (
            "The record meets the selected demo rule. This is not an independent "
            "check of a real family's receipt."
        )
    else:
        flag = "Open · within review period"
        rank = 4
        short = "The case is still open and within the proposed review period."

    person = {
        "Child 6m-3y": "Child aged 6 months to 3 years",
        "Pregnant woman": "Pregnant woman",
        "Lactating mother": "Lactating mother",
        "Adolescent girl": "Adolescent girl",
    }.get(c["beneficiary_group"], c["beneficiary_group"])
    district = c["district"].replace("Synthetic District ", "Demo area ")
    block = c["block"].replace("Synthetic Block ", "Block ")

    records.append({
        "case": c,
        "assessment": a,
        "flag": flag,
        "rank": rank,
        "short": short,
        "issue": issue_plain(c["exception_reason"]),
        "person": person,
        "area": f"{district} · {block} (fictional)",
        "ticket": ticket_plain(c["ticket_status"]),
        "recovery": recovery_plain(c["recovery_status"]),
        "evidence": evidence_plain(c["evidence_level"]),
    })

records.sort(key=lambda r: (r["rank"], -r["assessment"]["overdue_days"], r["case"]["case_id"]))
closed_unverified = [r for r in records if r["assessment"]["closed_receipt_unverified"]]
evidence_ticket_open = [r for r in records if r["assessment"]["receipt_evidenced_ticket_open"]]
open_cases = [r for r in records if r["case"]["ticket_status"] == "OPEN"]
open_overdue = [r for r in open_cases if r["assessment"]["overdue_days"] > 0]
priority_cases = [r for r in records if r["rank"] < 3]

page_hero(
    "Case workbench · fictional demonstration",
    "Find cases that need a closer look.",
    "A case can be marked complete before we know whether the family received ration. TruthLoop keeps those records visible for review.",
    "Cases to review first",
    str(len(closed_unverified)),
    "Fictional cases where receipt is not confirmed.",
    "These are demo examples, not real families.",
)
synthetic_banner()
st.caption(scope_caption(role, scope))

section_intro(
    "Case summary",
    "Where should we look first?",
    "Start with cases marked closed when there is no record to confirm receipt. Other cases may need follow-up for a different reason.",
)

m1, m2, m3, m4 = st.columns(4, gap="medium")
m1.metric("Fictional cases", len(records))
m2.metric("Closed · receipt not confirmed", len(closed_unverified))
m3.metric("Supporting record · case open", len(evidence_ticket_open))
m4.metric("Cases still open", len(open_cases))


def render_case(r, suffix=""):
    c, a = r["case"], r["assessment"]
    with st.container(border=True):
        left, middle, right = st.columns([0.85, 3.4, 1.05], gap="medium", vertical_alignment="center")
        with left:
            st.markdown(f"**{html.escape(c['case_id'])}**")
            if r["rank"] == 0:
                st.markdown('<span class="pt-case-status pt-case-status--alert">Needs review</span>', unsafe_allow_html=True)
            elif r["rank"] in (1, 2):
                st.markdown('<span class="pt-case-status">Follow-up</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pt-case-status pt-case-status--ok">Demo rule met</span>', unsafe_allow_html=True)
        with middle:
            st.markdown(f"**{html.escape(r['person'])} · {html.escape(c['district'].replace('Synthetic District ', 'Demo area '))}**")
            st.write(r["short"])
            st.caption(f"{r['issue']} · {r['area']}")
        with right:
            if st.button("Review case", type="primary", key=f"review_{c['case_id']}_{suffix}", use_container_width=True):
                st.session_state["truthloop_case_detail_selection"] = c["case_id"]
                st.switch_page("pages/2_Case_Detail.py")
            st.caption("See record and history")


tab_priority, tab_closed, tab_open, tab_mismatch = st.tabs([
    f"Priority cases ({len(priority_cases)})",
    f"Closed · not confirmed ({len(closed_unverified)})",
    f"Still open ({len(open_cases)})",
    f"Case status mismatch ({len(evidence_ticket_open)})",
])

with tab_priority:
    st.caption("These cases appear first because the record is unclear, a proposed review date has passed, or the case status does not match the recorded evidence.")
    if not priority_cases:
        st.info("No priority cases in this simulated view.")
    else:
        for r in priority_cases:
            render_case(r, "priority")

with tab_closed:
    st.caption("The case is marked closed, but the selected demo rule is not met. This does not prove ration was not received.")
    if not closed_unverified:
        st.info("No closed-but-unconfirmed cases in this simulated view.")
    else:
        for r in closed_unverified:
            render_case(r, "closed")

with tab_open:
    st.caption("These cases have not been marked closed. Review dates and escalation rules shown in this demo are assumptions, not official deadlines.")
    if not open_cases:
        st.info("No open cases in this simulated view.")
    else:
        for r in open_cases:
            render_case(r, "open")

with tab_mismatch:
    st.caption("This is the mirror case: the record meets the selected demo rule, but the case is still open.")
    if not evidence_ticket_open:
        st.info("No record-and-case mismatches in this simulated view.")
    else:
        for r in evidence_ticket_open:
            render_case(r, "mismatch")

with st.expander(f"View all {len(records)} fictional cases · technical table", expanded=False):
    st.caption("This table is for detailed review. The main cards above use plain language; the full event history is available on each case detail page.")
    all_rows = []
    for r in records:
        c, a = r["case"], r["assessment"]
        all_rows.append({
            "Case": c["case_id"],
            "Area (fictional)": c["district"].replace("Synthetic District ", "Demo area "),
            "Person or group": r["person"],
            "Issue": r["issue"],
            "Ticket": r["ticket"],
            "Recovery step": r["recovery"],
            "Evidence on file": r["evidence"],
            "What the record says": r["flag"],
            "Days past proposed review date": a["overdue_days"],
        })
    all_df = pd.DataFrame(all_rows)
    selected_filter = st.selectbox(
        "Show cases",
        ["All cases", "Closed · receipt not confirmed", "Supporting record · case still open", "Open · review date passed", "Record meets demo rule"],
        key="workbench_plain_filter",
    )
    filter_map = {
        "Closed · receipt not confirmed": "Closed · receipt not confirmed",
        "Supporting record · case still open": "Supporting record · case still open",
        "Open · review date passed": "Open · review date passed",
        "Record meets demo rule": "Record meets demo rule",
    }
    if selected_filter != "All cases":
        all_df = all_df[all_df["What the record says"] == filter_map[selected_filter]]
    query = st.text_input("Search technical records", placeholder="For example: SYN-010 or no internet connection")
    if query.strip():
        mask = all_df.astype(str).apply(lambda col: col.str.contains(query.strip(), case=False, regex=False)).any(axis=1)
        all_df = all_df[mask]
    st.dataframe(all_df, width="stretch", hide_index=True)
    st.caption(f"Showing {len(all_df)} case(s). All are fictional; counts are not real programme statistics.")

with st.expander("What the labels mean", expanded=False):
    st.markdown(
        "- **Closed · receipt not confirmed:** the case is closed, but information is not enough to confirm receipt. This does not prove non-receipt.\n"
        "- **Supporting record · case still open:** the demo record contains supporting information, but the case status remains open.\n"
        "- **Open · review date passed:** the proposed demo review date has passed; this is not an official deadline.\n"
        "- **Record meets demo rule:** the recorded information meets the selected prototype rule; it is not independent verification of a real family."
    )

with st.expander("Technical details for reviewers", expanded=False):
    st.caption(f"Evidence threshold currently selected: {threshold} — {cfg.EVIDENCE_LABELS[threshold]}. The outcome is computed from the threshold; it is never stored as evidence.")
    raw = []
    for r in records:
        c, a = r["case"], r["assessment"]
        raw.append({
            "Case": c["case_id"], "Ticket status": c["ticket_status"],
            "Recovery status": c["recovery_status"], "Evidence level": c["evidence_level"],
            "Computed outcome": a["outcome"], "Escalation level (proposed)": cfg.ESCALATION_LADDER[c["escalation_level"]],
        })
    st.dataframe(pd.DataFrame(raw), width="stretch", hide_index=True)

st.markdown('<div class="pt-footer">POSHAN TRUTHLOOP · Independent student prototype · Public evidence and fictional case records are kept separate.</div>', unsafe_allow_html=True)
