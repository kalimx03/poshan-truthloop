"""Shared public-service-style UI shell for Poshan TruthLoop.

Independent student prototype. Inspired by the broad layout and restrained
navy/white/orange palette of public nutrition-service websites; not an official
Government of India service and not using government emblems.
"""
from datetime import date
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
import access_control as ac  # noqa: E402
import config as cfg  # noqa: E402
import workflow as wf  # noqa: E402


APP_CSS = r"""
<style>
:root {
  --pt-navy: #08275f;
  --pt-navy-2: #123b83;
  --pt-orange: #f58220;
  --pt-blue-pale: #edf3ff;
  --pt-ink: #18243a;
  --pt-muted: #657286;
  --pt-line: #d9e1ed;
  --pt-canvas: #ffffff;
  --pt-white: #ffffff;
  --pt-green: #16734a;
  --pt-green-pale: #eaf6ef;
  --pt-red: #b42318;
  --pt-red-pale: #fff1f0;
  --pt-amber: #8a4b08;
  --pt-amber-pale: #fff7e6;
}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--pt-canvas) !important;
  color: var(--pt-ink) !important;
  color-scheme: light !important;
}
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stAppViewContainer"] > .main { margin-left: 0 !important; }
[data-testid="stMainBlockContainer"], section.main > div.block-container {
  max-width: 1510px !important;
  padding: 0 2.1rem 3rem !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"], #MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; height: 0 !important; }
body, p, li, label, span, div { font-family: Arial, Helvetica, sans-serif; }
h1, h2, h3 { color: var(--pt-navy) !important; letter-spacing: -0.018em; }
h1 { font-size: 2.25rem !important; line-height: 1.12 !important; font-weight: 750 !important; }
h2 { font-size: 1.55rem !important; font-weight: 720 !important; }
h3 { font-size: 1.13rem !important; font-weight: 700 !important; }
p, li, [data-testid="stMarkdownContainer"] { color: var(--pt-ink); }
[data-testid="stMetric"] {
  background: var(--pt-white) !important;
  border: 1px solid var(--pt-line) !important;
  border-radius: 7px !important;
  padding: .85rem 1rem .8rem !important;
  box-shadow: none !important;
  min-height: 98px;
}
[data-testid="stMetricLabel"] { color: #46566f !important; font-size: .84rem !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: var(--pt-navy) !important; font-size: 1.62rem !important; font-weight: 750 !important; }
[data-testid="stMetricDelta"] { font-size: .78rem !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--pt-line) !important; border-radius: 7px !important; overflow: hidden !important;
  background: var(--pt-white) !important;
}
[data-testid="stExpander"] {
  background: var(--pt-white) !important; border: 1px solid var(--pt-line) !important;
  border-radius: 7px !important; overflow: hidden !important;
}
[data-testid="stExpander"] summary { color: var(--pt-navy) !important; font-weight: 650 !important; }
[data-testid="stAlert"] { border-radius: 7px !important; }
.stButton > button, [data-testid="stFormSubmitButton"] button {
  border-radius: 5px !important; border: 1px solid #c8d4e5 !important;
  color: var(--pt-navy) !important; background: #fff !important; font-weight: 650 !important;
  min-height: 2.4rem !important; box-shadow: none !important;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
  background: #2864dc !important; color: white !important; border-color: #2864dc !important;
}
.stButton > button:hover { border-color: var(--pt-navy-2) !important; color: var(--pt-navy) !important; }
.stButton > button[kind="primary"]:hover { color: white !important; background: var(--pt-navy) !important; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
  border-color: #cdd8e8 !important; border-radius: 5px !important; background: white !important;
}
[data-testid="stPageLink-NavLink"] {
  border-radius: 4px !important; padding: .48rem .55rem !important; text-decoration: none !important;
  color: var(--pt-navy) !important; font-weight: 600 !important; font-size: .91rem !important;
}
[data-testid="stPageLink-NavLink"]:hover { background: var(--pt-blue-pale) !important; }
[data-testid="stPageLink-NavLink"][aria-current="page"] { background: #edf3ff !important; border-bottom: 2px solid var(--pt-navy-2) !important; border-radius: 4px 4px 0 0 !important; }
hr { border-color: var(--pt-line) !important; }
.pt-govstrip {
  margin: 0 -2.1rem; padding: .52rem 2.1rem;
  background: var(--pt-navy); color: #fff; font-size: .75rem; letter-spacing: .015em;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.pt-govstrip strong { color: #fff; font-weight: 700; }
.pt-govstrip .pt-tagline { color: #e2eaf8; }
.pt-nav {
  margin: 0 -2.1rem 1rem; padding: .7rem 2.1rem .65rem;
  background: white; border-bottom: 1px solid var(--pt-line);
}
.pt-brand { display: flex; align-items: center; gap: .7rem; min-height: 2.6rem; padding-left: .1rem; }
.pt-brand-mark { width: 36px; height: 36px; border-radius: 4px; background: var(--pt-orange); color: #fff; display:flex; align-items:center; justify-content:center; font-size: .88rem; font-weight:800; letter-spacing:-.03em; flex:0 0 36px; }
.pt-brand-main { display: block; color: var(--pt-orange); font-size: 1.12rem; line-height: 1; font-weight: 800; letter-spacing: .015em; }
.pt-brand-sub { display: block; color: var(--pt-navy); font-size: .98rem; line-height: 1.08; font-weight: 780; letter-spacing: .02em; }
.pt-hero {
  display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(230px, .85fr); gap: 1.2rem;
  padding: 1.7rem 1.65rem 2.55rem; border-radius: 0; background: var(--pt-navy); color: white;
  box-shadow: none; margin: .3rem 0 1.15rem; border-bottom: 0; border-radius: 0;
}
.pt-hero .pt-eyebrow { color: #e8edf7; text-transform: uppercase; font-size: .74rem; font-weight: 700; letter-spacing: .10em; margin: 0 0 .72rem; }
.pt-hero h1 { color: var(--pt-orange) !important; margin: 0 0 .75rem !important; font-size: 2.25rem !important; }
.pt-hero h1 span { color: var(--pt-orange) !important; }
.pt-hero p { color: #f3f6fb; margin: 0; line-height: 1.55; max-width: 800px; }
.pt-hero-panel { align-self: stretch; border-radius: 4px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.22); padding: 1rem 1.15rem; display: flex; flex-direction: column; justify-content: center; }
.pt-hero-panel .pt-panel-label { color: #f0f4fb; font-size: .72rem; font-weight: 750; letter-spacing: .055em; text-transform: uppercase; }
.pt-hero-panel .pt-big-number { color: white; font-size: 2.12rem; line-height: 1.18; font-weight: 800; margin: .2rem 0 .25rem; }
.pt-hero-panel .pt-panel-note { color: #eff3fa; font-size: .85rem; line-height: 1.4; }
.pt-hero-panel .pt-panel-warning { margin-top: .7rem; padding: .5rem .6rem; border-radius: 4px; color: #fff; background: rgba(8,39,95,.65); border-left: 2px solid #cbd8ed; font-size: .78rem; }
.pt-section-eyebrow { color: var(--pt-navy-2); font-size: .72rem; font-weight: 750; letter-spacing: .085em; text-transform: uppercase; margin: .15rem 0 .32rem; }
.pt-section-intro { color: var(--pt-muted); margin-top: -.25rem; margin-bottom: .95rem; }
.pt-notice { background: #fff; border: 1px solid var(--pt-line); border-left: 3px solid var(--pt-navy-2); border-radius: 5px; padding: .8rem .95rem; margin: .6rem 0 .95rem; color: var(--pt-ink); }
.pt-notice strong { color: var(--pt-navy); }
.pt-notice--synthetic { border-left-color: var(--pt-navy-2); background: #f7f9fd; }
.pt-notice--warning { border-left-color: #a64b24; background: #fff8ef; }
.pt-notice--success { border-left-color: var(--pt-green); background: #f1f8f3; }
.pt-chip { display: inline-block; border-radius: 4px; padding: .22rem .45rem; font-size: .72rem; font-weight: 750; letter-spacing: .01em; }
.pt-chip--red { color: #9f1d18; background: #fff0ee; border: 1px solid #f2c5c0; }
.pt-chip--green { color: #136b42; background: #e9f7ef; border: 1px solid #b9e6ca; }
.pt-chip--amber { color: #81400a; background: #fff4dc; border: 1px solid #eed9ab; }
.pt-outcome { padding: 1rem 1.1rem; background: white; border: 1px solid #e8bdb8; border-left: 4px solid var(--pt-red); border-radius: 5px; margin: .65rem 0 .95rem; }
.pt-outcome--warning { border-color: #e5d8b3; border-left-color: #97702c; background: #fffdf7; }
.pt-outcome--success { border-color: #b9e6ca; border-left-color: var(--pt-green); background: #f4faf6; }
.pt-outcome .pt-outcome-title { font-size: .9rem; font-weight: 800; margin-bottom: .35rem; color: #9f1d18; letter-spacing: 0; }
.pt-outcome--warning .pt-outcome-title { color: #725617; }
.pt-outcome--success .pt-outcome-title { color: #16734a; }
.pt-outcome .pt-outcome-body { color: #34445b; font-size: .94rem; line-height: 1.5; }
.pt-case-card { border: 1px solid var(--pt-line); border-radius: 6px; background: white; padding: .95rem 1rem; margin: .55rem 0; }
.pt-case-card h4 { color: var(--pt-navy); margin: 0 0 .35rem; font-size: 1rem; }
.pt-case-meta { color: var(--pt-muted); font-size: .86rem; line-height: 1.45; }
.pt-case-status { font-size: .78rem; font-weight: 750; display: inline-block; padding: .18rem .42rem; border-radius: 4px; background: #f4f6f9; color: #2f3f58; border: 1px solid #d9e1ed; }
.pt-case-status--alert { color: #9f1d18; background: #fff1f0; border-color: #f0c4c0; }
.pt-case-status--ok { color: #136b42; background: #eaf6ef; border-color: #b9e6ca; }
.pt-footer { border-top: 1px solid var(--pt-line); color: var(--pt-muted); margin-top: 2rem; padding-top: .8rem; font-size: .76rem; }
@media (max-width: 900px) {
  .pt-hero { grid-template-columns: 1fr; clip-path: none; padding-bottom: 1.5rem; }
  .pt-govstrip { display: block; }
  .pt-govstrip .pt-tagline { display: block; margin-top: .2rem; }
  [data-testid="stMainBlockContainer"], section.main > div.block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
</style>
"""


def setup_page(page_title: str, active_page: str):
    """Configure page and render a consistent public-service header."""
    st.set_page_config(
        page_title=f"{page_title} | Poshan TruthLoop",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """<div class="pt-govstrip">
          <span><strong>MISSION POSHAN 2.0</strong> &nbsp; · &nbsp; <span class="pt-tagline">Nutrition service assurance concept</span></span>
          <span class="pt-tagline">INDEPENDENT STUDENT PROTOTYPE · NOT AN OFFICIAL GOVERNMENT SERVICE</span>
        </div>""",
        unsafe_allow_html=True,
    )
    nav_cols = st.columns([1.25, 1.0, 1.2, 1.0, 1.35], gap="small", vertical_alignment="center")
    with nav_cols[0]:
        st.markdown(
            """<div class="pt-brand">
              <div class="pt-brand-mark">PT</div>
              <div><span class="pt-brand-main">POSHAN</span><span class="pt-brand-sub">TRUTHLOOP</span></div>
            </div>""",
            unsafe_allow_html=True,
        )
    links = [
        ("Evidence Room", "app.py", "evidence"),
        ("Case Workbench", "pages/1_Case_Workbench.py", "cases"),
        ("Case Detail", "pages/2_Case_Detail.py", "detail"),
        ("Supervisor Oversight", "pages/3_Supervisor_Oversight.py", "oversight"),
    ]
    for col, (label, path, key) in zip(nav_cols[1:], links):
        with col:
            st.page_link(path, label=label, icon=None)
    st.markdown(
        '<div style="height:1px;background:#d9e1ed;margin:.2rem 0 1rem"></div>',
        unsafe_allow_html=True,
    )


def page_hero(eyebrow: str, title: str, subtitle: str, side_label: str | None = None,
              side_value: str | None = None, side_note: str | None = None,
              side_warning: str | None = None):
    """Render a restrained navy hero with one orange headline, matching the reference language."""
    panel = ""
    if side_label and side_value:
        panel = f"""<div class="pt-hero-panel">
          <div class="pt-panel-label">{side_label}</div>
          <div class="pt-big-number">{side_value}</div>
          <div class="pt-panel-note">{side_note or ''}</div>
          {f'<div class="pt-panel-warning">{side_warning}</div>' if side_warning else ''}
        </div>"""
    st.markdown(
        f"""<section class="pt-hero">
          <div>
            <p class="pt-eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          {panel}
        </section>""",
        unsafe_allow_html=True,
    )


def section_intro(eyebrow: str, title: str, subtitle: str | None = None):
    # Eyebrows are kept short and navy, not decorated with numbered orange labels.
    if eyebrow:
        st.markdown(f'<div class="pt-section-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.subheader(title)
    if subtitle:
        st.markdown(f'<div class="pt-section-intro">{subtitle}</div>', unsafe_allow_html=True)


def get_conn(reset=False):
    if reset or "conn" not in st.session_state:
        conn = wf.connect()
        wf.seed(conn, date.today())
        st.session_state.conn = conn
    return st.session_state.conn


def synthetic_banner():
    st.markdown(
        """<div class="pt-notice pt-notice--synthetic">
          <strong>DEMO DATA</strong> &nbsp; These are fictional cases and locations, not real families or delivery events.
          Counts here are examples, not programme statistics. Review dates and role rules are proposed assumptions.
        </div>""",
        unsafe_allow_html=True,
    )


def role_controls(conn):
    """Show optional prototype controls; the selector does not authenticate users."""
    all_cases = wf.list_cases(conn)
    role_names = {
        "Anganwadi Worker": "Anganwadi worker",
        "Supervisor": "Supervisor",
        "CDPO": "CDPO (Child Development Project Officer)",
        "District Programme Officer": "District Programme Officer",
    }
    with st.expander("Demo controls · change role or evidence rule", expanded=False):
        cols = st.columns([1.25, 1.45, 1.5], gap="medium")
        role = cols[0].selectbox(
            "Who is using this demo?",
            cfg.USER_ROLES,
            index=3,
            key="truthloop_active_role",
            format_func=lambda x: role_names.get(x, x),
            help="Demonstrates proposed decision rights only; it does not authenticate a user.",
        )
        options = ac.scope_options(all_cases, role)
        scope = None
        if role != "District Programme Officer":
            key = f"truthloop_scope_{role}"
            scope = cols[1].selectbox("Fictional area", options, key=key)
        else:
            cols[1].text_input("Fictional area", value="All demo districts", disabled=True)
        threshold = cols[2].selectbox(
            "What counts as enough evidence? (proposed)",
            cfg.THRESHOLD_OPTIONS,
            index=cfg.THRESHOLD_OPTIONS.index(cfg.EVIDENCE_THRESHOLD),
            key="truthloop_evidence_threshold",
            format_func=lambda x: f"{cfg.EVIDENCE_LABELS[x]} ({x})",
        )
        st.caption("Changing the evidence rule recalculates the result; it does not change recorded evidence. Role selection is a demonstration, not sign-in security.")
    visible = ac.filter_visible_cases(all_cases, role, scope)
    return role, scope, threshold, visible


def scope_caption(role, scope):
    role_names = {
        "Anganwadi Worker": "Anganwadi worker",
        "Supervisor": "Supervisor",
        "CDPO": "CDPO",
        "District Programme Officer": "District Programme Officer",
    }
    label = role_names.get(role, role)
    if role == "Anganwadi Worker":
        return f"Demo view: assigned fictional centre — {scope}"
    if role == "Supervisor":
        return f"Demo view: assigned fictional block — {scope}"
    if role == "CDPO":
        return f"Demo view: assigned fictional district — {scope}"
    return "Demo view: all fictional districts"


def evidence_plain(level: str, include_code: bool = False) -> str:
    labels = {
        "E0": "None recorded",
        "E1": "Delivery record only",
        "E2": "Another record supports it",
        "E3": "Family confirmation (simulated)",
    }
    text = labels.get(level, "Unknown evidence level")
    return f"{text} ({level})" if include_code else text


def ticket_plain(status: str) -> str:
    return {"OPEN": "Open", "CLOSED": "Closed"}.get(status, status.replace("_", " ").title())


def recovery_plain(status: str) -> str:
    return {
        "NOT_STARTED": "Not started",
        "IN_PROGRESS": "In progress",
        "COMPLETED": "Marked complete",
    }.get(status, status.replace("_", " ").title())


def outcome_plain(outcome: str) -> str:
    return {
        "STILL_OPEN": "Still needs follow-up",
        "OUTCOME_UNKNOWN": "Receipt not confirmed",
        "RECEIPT_EVIDENCED": "Evidence meets demo rule",
    }.get(outcome, outcome.replace("_", " ").title())


def issue_plain(reason: str) -> str:
    return {
        "Face match failed": "Face check did not work",
        "Mother's match failed": "Mother's face check did not work",
        "No connectivity": "No internet connection",
        "OTP failed": "One-time code did not work",
    }.get(reason, reason)


def action_plain(action: str) -> str:
    labels = {
        "CASE_OPENED": "Case created",
        "SET_TICKET_STATUS": "Ticket status changed",
        "SET_RECOVERY_STATUS": "Recovery step updated",
        "SET_EVIDENCE_LEVEL": "Evidence record updated",
        "SET_ESCALATION_LEVEL": "Review level raised",
    }
    return labels.get(action, action.replace("_", " ").title())


def value_plain(field: str, value):
    if value is None:
        return "—"
    value = str(value)
    if field == "ticket_status":
        return ticket_plain(value)
    if field == "recovery_status":
        return recovery_plain(value)
    if field == "evidence_level":
        return evidence_plain(value)
    if field == "escalation_level":
        try:
            return cfg.ESCALATION_LADDER[int(value)]
        except (ValueError, KeyError):
            return value
    if value in ("-", "None", "none", ""):
        return "—"
    return value.replace("_", " ").title()


def style_plotly(fig, height=None):
    """Apply a simple navy/blue public-service chart theme."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial, Helvetica, sans-serif", color="#18243a", size=12),
        margin=dict(l=12, r=14, t=24, b=12),
        legend=dict(bgcolor="rgba(255,255,255,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(showgrid=False, linecolor="#d9e1ed", tickfont=dict(color="#46566f"))
    fig.update_yaxes(gridcolor="#e9eef6", zerolinecolor="#d9e1ed", tickfont=dict(color="#46566f"))
    return fig
