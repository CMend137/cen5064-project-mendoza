# MacroMetric — Monday, November 9 (two-minute demonstration)

## Pre-demo setup

From project root: `python -m pytest -q`, then `python -m streamlit run app.py`.
Keep Streamlit and the repository's GitHub PR/ADR pages ready.
Use **fake** weight/calorie test data for demonstration, not real personal data.

## Two-minute walkthrough

- **0:00–0:20**: "At midterm, MacroMetric had a single Streamlit form and overwrote the last result in JSON. My action items were a fuller graphical workflow and a real database."
- **0:20–0:50**: Open Calculator, calculate targets twice using different goals. Move to Calculation History and point out both saved records.
- **0:50–1:15**: Edit one calculation and show targets recalculate; delete the other with confirmation. Mention SQLite's `calculations` table and service/repository separation.
- **1:15–1:40**: In Daily Log, enter two dated weight/calorie records; open Weekly Trends and show the graphs and averages, then Recommendations.
- **1:40–2:00**: Show `docs/adr/adr-003.md` and GitHub PR, explain automated tests and the database storage abstraction.

## Anticipated questions

- **Why SQLite?** A relational, durable database with no server or secrets, behind the existing repository layer; see ADR-003.
- **How do edits retain correct macros?** `TargetService.edit_calculation()` calls the unchanged domain calculator, then updates the selected SQL row.
- **How does SOLID apply?** `TargetService` uses a `TargetStore` protocol; Streamlit receives the concrete SQLite repository through dependency injection.
- **What's not yet production ready?** No accounts/authentication; progress recommendation rules are simplistic; backup/migrations are not implemented. These are clearly documented limitations.

## Peer review reminders

- Round 1 on partner's repo **before 1:45 PM November 9**.
- Round 2 on partner's repo **before 1:45 PM November 16**.
- Titles: `Peer Review - final round 1 - @CMend137` / `Peer Review - final round 2 - @CMend137`.
- Start each with `Changed since my last review: ...` and complete the **five sections** from the professor's attached guide. The sections are not reproduced here because the guide was not supplied.
