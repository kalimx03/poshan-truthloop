# Poshan TruthLoop — Poshan Tracker-inspired interface (Day 3 MVP)

**Competition:** Techfest IIT Bombay 2026–27 · India @ 71/100 · Theme 1: Maternal & Early Childhood Nutrition

## Design decision

The interface takes cues from the public-service design language in the official Poshan Tracker website: navy, white, saffron/orange accents, clear section hierarchy, compact navigation and accessible contrast. It does **not** use the Government of India emblem or official Poshan Tracker logo and is visibly labelled as an independent student prototype. It must not be represented as a government website or integration.

## Run locally on Windows

Open PowerShell in this folder. If the virtual environment has already been created, activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If this is a fresh extraction, create the environment and install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Launch the app:

```powershell
python -m streamlit run app.py
```

Open the local URL that Streamlit prints, usually `http://localhost:8501`. Keep the terminal running while using the app.

## Run tests

```powershell
python -m pytest -q
```

## What is implemented

- **Evidence Room:** national AU1121 figures, two unconnected reported matching-rate observations, source ledger, state/UT table in annexure order and exact-integer reconciliation gate.
- **Case Workbench:** 12 synthetic cases, computed outcomes, scope-aware filtering, flags for closed/unverified and evidence-met/open-ticket cases.
- **Case Detail & Audit Timeline:** action recording with required reason, hash-chained tamper-evident events, chain verification, threshold selector, restricted demo tampering/reset controls.
- **Supervisor Oversight:** scope-level indicators, follow-up queue, computed-outcome chart, proposed escalation levels and scope-limited escalation actions.
- **Simulated role scoping:** Anganwadi Worker sees one fictional centre; Supervisor sees one fictional block; CDPO sees one fictional district; District Programme Officer sees all synthetic districts. Action fields and evidence/escalation levels follow proposed demonstration rules.

## Evidence discipline and limitations

- This is a student prototype and is not connected to government systems.
- All individual cases and organizational codes are synthetic.
- The role selector demonstrates proposed decision rights; it is not authentication or production authorization.
- Evidence levels, the default E2 threshold, review deadline and escalation ladder are design assumptions—not government rules.
- The state-level values in the annexure do not reconcile with the national row. The app displays them in source order but suppresses derived rankings and aggregate comparisons while the gate fails.
- The derived unmatched number is not a count of beneficiaries denied THR.
- The audit chain is tamper-evident, not immutable. Someone with database access could rewrite records and recompute hashes.
- No Aadhaar number, biometric, real beneficiary name, phone, photo or other direct personal identifier is collected in the synthetic case schema.

## Primary source

Lok Sabha Unstarred Question 1121, answered 24 July 2026:
https://sansad.in/getFile/lsapps/loksabhaquestions/annex/188/AU1121_dedvSL.pdf?source=lsapps

The unmatched count is derived from the reported national row. The two published matching-rate endpoints are shown as separate observations; intermediate monthly values are not fabricated.
