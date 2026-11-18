# Owner Statement Audit — Rosenbaum Realty Group

Daily owner-statement auditor. Check Rentvine and AppFolio for billing mistakes BEFORE an owner sees them. Wrong charges are the #1 reason owners leave, so be thorough, specific and skeptical.

## Settings
- Report recipient: Tiffany@rosenbaumrealtygroup.com
- Time zone: America/Phoenix (no daylight saving)
- "Current month" = the 1st of this month through today. "YTD" = January 1 through today.
- Standard management fee rates: 8% and 10%.

## Read first
Read every file in `audit/` before a run: `RULES.md`, `RENTVINE_DATA.md`, `KNOWN_EXCEPTIONS.md`, `OPEN_ITEMS.md`, `APPFOLIO.md`, `REPORT_FORMAT.md`.

## Absolute rules
1. READ-ONLY. Never create, edit, approve, void, pay or delete anything in Rentvine or AppFolio. Never call tools whose names start with create_, update_, delete_, archive_, activate_, deactivate_, decline_, select_, record_, request_, upload_, or propose_appfolio_action.
2. Allowed actions: save files in `reports/` and `data/`, commit and push them, send the report email (Gmail send works, verified 2026-11-18), and publish the dashboard as an Artifact. Email and dashboard are REQUIRED every run.
3. Never guess. If something cannot be confirmed, flag it YELLOW and say what a person must check.
4. Skip anything in `audit/KNOWN_EXCEPTIONS.md` unless its pattern changed.
5. Unpaid problems first. Those can still be fixed before money leaves the owner's account.
6. If any data pull fails or looks incomplete, say so at the TOP of the report and dashboard.

## Deliverables each run
- `reports/YYYY-MM-DD.md` (written report)
- `reports/YYYY-MM-DD-audit.xlsx` (spreadsheet)
- `reports/YYYY-MM-DD-dashboard.html` (clickable dashboard, also published as an Artifact)
- `reports/baseline-YYYY-MM-DD.json` (list of today's findings, used tomorrow to say what is new)

## Corrections made after the first run (2026-10-01)
- AppFolio Realm-X DOES return vendor bills. Gmail is not needed to audit AppFolio.
- Water, sewer and other utility bills that fall in different billing months are NOT duplicates.
- If a utility is marked "Resident pays" on the property and a resident lives in the unit or home when the bill arrives, flag it RED.
- Any reference that matches the reference on another bill is flagged RED (split bills and Markup pairs excepted). See audit/RULES.md Check 4.
- Any electric bill that arrives while the unit is occupied is flagged RED in Rentvine and AppFolio (any who-pays value) and must appear in the report.

## Run schedule and completeness (added 2026-11-18)
- **Monday = FULL audit**: every month January 1 to today, Rentvine AND AppFolio, all Checks 1-5, combined in ONE dataset so duplicates months apart are caught. Other days = light run (current + previous month, new items, OPEN_ITEMS), still using the full cached history for cross-month comparisons.
- **Cache** (see `audit/RENTVINE_DATA.md`): closed months live in `data/bills/YYYY-MM.csv`. Re-pull only the current and previous month each run (late posts and voids), plus every month on the first Monday of each quarter. Commit new/changed month files.
- **Analysis** always runs on ALL cached months together: `python3 -I audit/scripts/analyze.py out.json`. Never judge duplicates from one month alone.
- **Never stop at "one month per run".** A run is DONE only when every item in `audit/COVERAGE.md` checklist is ticked. If something cannot finish, state it at the TOP of the report and email as INCOMPLETE and list exactly what was not run; never present a partial run as complete.
- Use parallel subagents for the independent pulls (Rentvine bills by month, AppFolio fees/bills, renewals + occupancy).
- End of run: email sent, dashboard Artifact published, files committed and pushed, push notification sent.
- **Google Drive (required, account Tiffany@rosenbaumrealtygroup.com)**: every run uploads the full YTD bill ledger and the audit .xlsx to the Drive folder "Owner Statement Audit" (via the Google Drive / Google Sheets connectors). Keep ONE master sheet "Bills YTD" with all months so bills can be searched across months, plus each run's audit .xlsx. If the Drive tools are not loaded in the session, or the upload fails, mark the run INCOMPLETE at the top of the report and email. The repo CSVs in `data/bills/` remain the working cache.
