# AppFolio (Realm-X connector)

AppFolio Realm-X returns fee settings AND vendor bills, tenants and unit records. Gmail is not needed. (An earlier version of these instructions wrongly said AppFolio could only return fee settings.)

## Fee settings (Phase 1)
Ask: "List every property with its owner and management fee percentage or flat fee, and flag any where the management fee is not 8% or 10%." Apply Check 2 to the result. Realm-X returns a CSV artifact (about 680 properties).

## Bills
Realm-X times out after 60 seconds on large questions. Rules that worked on 2026-10-01:
- One day to one week at a time. Use: "List vendor bills created from <date> through <date>, excluding bills where the payee is Rosenbaum Realty Group, with payee, bill reference, description, property, GL account, amount, paid status and created date." Month-start weeks are huge (about 770 lines of Rosenbaum fees); the exclusion keeps them small.
- If a range times out, split it (single days worked).
- Results over about 25,000 tokens are saved to a file by the tool; smaller ones come back inline.
- Pairs of an "Uploaded Invoice" (random 7-character reference like TV7NNIDB) and a work-order bill (reference like 1236322) for the same vendor, property and amount are duplicates. Repair Masters LLC bills with "-EX-" in the reference equal vendor bill plus markup; confirm what creates them.
- Aggregate questions ("find duplicates", "units with a tenant") time out. Ask per property.

## Tenants and who pays
- "Is there a current tenant at property P22-023?" works (one property at a time).
- "For property P22-023, is the tenant or the owner responsible for electric utilities?" works. Answers on 2026-10-01 said owner/company for P22-023, P05-081 and P13-031 A (default may apply when the field is blank).

## Status of coverage
Audited 2026-10-01: September 1 to October 1. NOT yet audited: January to August, and AppFolio renewals. Cover January to today on every Monday full audit (one week at a time per request); light days cover current + previous month.

## 2026-11-23 finding: Realm-X bills cannot be saved to disk
Realm-X returns every result inline in the chat ("[Resource ... .csv]" text); nothing lands on disk, so weekly pulls cannot be assembled into a dataset by script (subagent attempt: Jul 22 to Aug 18 only, with suspicious empty weeks). Also add exclusions for Owner Draw, Clearing Account, Rent Income and Move Out Refund lines. Fee settings work (CSV, 688 properties). AppFolio bills remain UNAUDITED until a file-based export route exists.

2026-11-23 (Jan-Jun agent): Realm-X also gave FALSE "no bills" answers (e.g. Jan 16, Apr 27-29 had 109 rows, May 14-15 had 43, Feb 19-20 had 25 when re-asked narrower). Every empty answer is unreliable. The hand-copied partial CSV (749 rows, $339,564.62) is NOT a complete dataset and was not used in the audit. Coverage notes: data/appfolio/bills-2026-H1-coverage.md.
