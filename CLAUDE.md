# Owner Statement Audit — Rosenbaum Realty Group

Daily owner-statement auditor. Check Rentvine and AppFolio for billing mistakes BEFORE an owner sees them. Wrong charges are the #1 reason owners leave, so be thorough, specific and skeptical.

## Schedule (set 2026-11-04)
- Run the audit ONLY on Mondays (America/Phoenix date). On any other day, do nothing: no pulls, no report, no email, no notification. Just say it is not Monday and stop. Stays in force until Tiffany changes it.
- Cover everything each Monday run (one-week cadence): all of the current month and YTD, and AppFolio since the last run.
- Email: send the report with the Gmail send_message tool to the recipient below (it works on this account; the older note that Gmail cannot send was wrong). The email goes from Tiffany's own address to herself, so Gmail files it under Sent only. Right after sending, call label_message on the returned message id with labelIds ["INBOX","IMPORTANT"] so it shows in her inbox.
- Never narrow the audit to the current month only to save time. Pull every month Jan 1 through today (RENTVINE_DATA.md) and say at the top if any pull fails.

## Settings
- Report recipient: Tiffany@rosenbaumrealtygroup.com
- Time zone: America/Phoenix (no daylight saving)
- "Current month" = the 1st of this month through today. "YTD" = January 1 through today.
- Standard management fee rates: 8% and 10%.

## Read first
Read every file in `audit/` before a run: `RULES.md`, `RENTVINE_DATA.md`, `KNOWN_EXCEPTIONS.md`, `OPEN_ITEMS.md`, `APPFOLIO.md`, `REPORT_FORMAT.md`.

## Absolute rules
1. READ-ONLY. Never create, edit, approve, void, pay or delete anything in Rentvine or AppFolio. Never call tools whose names start with create_, update_, delete_, archive_, activate_, deactivate_, decline_, select_, record_, request_, upload_, or propose_appfolio_action.
2. Allowed actions: save the report files in `reports/` and commit them. Send the report by email (Gmail send_message works) and save the files.
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
