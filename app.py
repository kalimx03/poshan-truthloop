import pandas as pd
import plotly.express as px
import streamlit as st

import evidence as ev
from ui_common import setup_page, page_hero, section_intro, style_plotly

setup_page("Evidence Room", "evidence")
n = ev.national()

page_hero(
    "Maternal & early childhood nutrition",
    "Did the ration reach the <span>family?</span>",
    "Some records are marked complete, but they do not show whether the family received the ration. TruthLoop keeps those cases visible for follow-up.",
    "National matching status · June 2026",
    f"{n['rate_calc']:.2f}%",
    "The identity-matching step was marked complete in the national figures.",
    "Matching status does not tell us whether the family received ration.",
)

st.markdown(
    '<div class="pt-notice"><strong>PUBLIC EVIDENCE VIEW</strong> &nbsp; This page uses reported national figures from Lok Sabha Unstarred Question 1121, answered 24 July 2026. No synthetic case data appears in this view.</div>',
    unsafe_allow_html=True,
)

# Put the integrity decision above the fold: the UI must not bury the key limitation.
states = ev.load_states()
rec = ev.reconcile(states)
if not rec["ok"]:
    integrity_html = (
        '<div class="pt-notice pt-notice--warning" '
        'style="display:flex;gap:1rem;align-items:flex-start;flex-wrap:wrap;">'
        '<div style="min-width:190px;max-width:245px;">'
        '<div style="font-size:.72rem;font-weight:850;letter-spacing:.10em;color:#b42318;">DATA CHECK</div>'
        '<div style="font-size:1.05rem;font-weight:800;color:#8f1d18;margin-top:.25rem;">The state totals do not match</div>'
        '<div style="font-size:.82rem;color:#8f1d18;margin-top:.2rem;">We have paused state comparisons.</div>'
        '</div>'
        '<div style="flex:1;min-width:260px;color:#17243a;line-height:1.5;">'
        f"The 36 state/UT rows in our transcription sum to <strong>{rec['state_sum_eligible']:,}</strong> active eligible records, "
        f"compared with <strong>{n['eligible']:,}</strong> in the national row—a difference of <strong>{rec['eligible_diff']:,}</strong>. "
        'The source does not establish why these counts differ.'
        '</div></div>'
    )
    st.markdown(integrity_html, unsafe_allow_html=True)

section_intro(
    "National figures",
    "What the published numbers tell us",
    "These figures describe identity matching, not whether any individual family received ration. The unmatched count is calculated from the two reported counts; it is not a count of people denied THR.",
)
c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("People listed as eligible for THR", f"{n['eligible']:,}")
c2.metric("Records with matching completed", f"{n['matched']:,}")
c3.metric("Not matched · calculated", f"{n['unmatched']:,}")
c4.metric("Matching rate · calculated", f"{n['rate_calc']:.2f}%")

st.markdown(
    '<div class="pt-notice pt-notice--warning"><strong>What this answer does not tell us.</strong> The question asked how many eligible people had not received ration and why. The reply gives identity-matching counts and rates, but not the requested non-receipt counts or reasons. That is a gap in this published answer—not proof that ration was denied or that no other records exist.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 1.2], gap="large")
with left:
    section_intro("Reported matching rates", "Two points, not a fabricated trend")
    trend_df = pd.DataFrame(ev.TREND, columns=["Reported period", "Matching rate (%)"])
    fig = px.scatter(
        trend_df,
        x="Reported period",
        y="Matching rate (%)",
        labels={"Reported period": "Reported period", "Matching rate (%)": "Matching rate (%)"},
    )
    fig.update_traces(marker=dict(size=15, color="#2864dc", line=dict(color="#08275f", width=1.5)))
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig.update_xaxes(type="category")
    style_plotly(fig, height=300)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("The two reported endpoints are not connected. The cited answer does not provide the July 2025 absolute denominator, and intermediate monthly values are not fabricated.")
with right:
    section_intro("State data quality", "State counts do not match")
    if rec["ok"]:
        st.markdown('<div class="pt-notice pt-notice--success"><strong>PASS</strong> &nbsp; State rows reconcile exactly to the national counts. Derived aggregate comparisons are enabled.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pt-notice pt-notice--warning"><strong>STATE COMPARISONS PAUSED</strong><br>State/UT rows are shown as reported only. We will not rank states until the totals match.</div>', unsafe_allow_html=True)
    recon = pd.DataFrame({
        "Measure": ["Active eligible", "Matched", "Unmatched · derived"],
        "Sum of 36 state rows": [rec["state_sum_eligible"], rec["state_sum_matched"], rec["state_sum_unmatched"]],
        "National row": [n["eligible"], n["matched"], n["unmatched"]],
        "Difference": [rec["eligible_diff"], rec["matched_diff"], rec["state_sum_unmatched"] - rec["national_unmatched"]],
    })
    for col in ["Sum of 36 state rows", "National row", "Difference"]:
        recon[col] = recon[col].map(lambda x: f"{x:,}")
    st.dataframe(recon, hide_index=True, width="stretch")
    st.caption("Individual state percentages recompute from each row's counts. The source does not establish the cause of the aggregate mismatch; clarification is needed before state comparisons are used.")

with st.expander("View state/UT rows as reported in the annexure", expanded=False):
    states = ev.load_states()
    view = states[["state", "eligible", "matched", "reported_pct"]].rename(columns={
        "state": "State / UT",
        "eligible": "Active eligible · as reported",
        "matched": "e-KYC + face matched · as reported",
        "reported_pct": "Matching rate % · as reported",
    })
    st.dataframe(view, width="stretch", hide_index=True)
    st.caption("Rows remain in source-annexure order. No state ranking or aggregated state-level claim is made while the exact-count gate is closed.")

with st.expander("What this evidence cannot establish", expanded=False):
    st.markdown(
        "- Whether any unmatched beneficiary received THR through an offline matching or nominee process.\n"
        "- Why an individual was unmatched.\n"
        "- Any individual authentication event or actual receipt outcome.\n"
        "- The cause of the state-to-national count mismatch.\n"
        "- The reasons for the change between the two reported matching-rate observations."
    )

with st.expander("Source ledger and provenance", expanded=False):
    st.dataframe(ev.load_ledger(), width="stretch", hide_index=True)
    st.markdown("Primary source: [Lok Sabha Unstarred Question 1121, answered 24 July 2026](https://sansad.in/getFile/lsapps/loksabhaquestions/annex/188/AU1121_dedvSL.pdf?source=lsapps)")

st.markdown('<div class="pt-footer">POSHAN TRUTHLOOP · Independent student prototype · Public-source figures and synthetic case workflows are kept separate.</div>', unsafe_allow_html=True)
