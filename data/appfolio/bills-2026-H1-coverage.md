# AppFolio vendor bills, 2026-01-01 to 2026-06-30: pull coverage

Source: AppFolio Realm-X (read-only). Every question used: "List vendor bills created from <date> through <date>, excluding bills where the payee is Rosenbaum Realty Group, with payee, bill reference, description, property, GL account, amount, paid status and created date."
Output: `bills-2026-H1.csv` has 749 rows and $339,564.62 total. 2 rows are Unpaid. The 749 rows are the sum of the ranges listed below; the June 11-17 figure counts only its 52 non-owner-draw rows.

## WARNING: this pull is NOT complete
Realm-X returned false "no bills" answers. The same date was empty in one question and full in another:
- Jan 15-21 returned 41 rows, but a single-day question for Jan 16 said "none".
- Weekly Feb 19-25 said "none", but Feb 19-20 returned 25 rows and Feb 27-28 returned 6.
- Weekly Apr 23-29 said "none", but Apr 27-29 returned 109 rows.
- Weekly May 14-20 said "none", but May 14-15 returned 43 rows and May 19-20 returned 37.
- Weekly Apr 9-15 said "none", but Apr 11-12 returned 1 row.
- Weekly Jun 18-24 said "none", but Jun 18-19 returned 10.
- Jan 1-31, Apr 1-30 and May 1-31 month-wide questions all said "none" although data exists.

So every range below marked "none returned" is UNCONFIRMED, not proven empty. A person must re-check those days in AppFolio (Bill Detail report, created date). Positive results were reconciled: for every file the row count and total matched the figure Realm-X stated, except where noted.

## Ranges that returned rows (all counts and totals matched Realm-X's stated figures)
| Range asked | Rows | Total |
|---|---|---|
| 2026-01-15 to 01-21 | 41 | $18,408.14 |
| 2026-01-22 to 01-28 | 49 | $60,944.60 |
| 2026-01-29 to 02-04 | 55 | $30,310.44 |
| 2026-02-05 to 02-11 | 31 | $29,918.41 |
| 2026-02-12 to 02-18 | 18 | $6,487.98 (Realm-X gave no total; rows run only to 02-17) |
| 2026-02-19 to 02-20 | 25 | $6,741.82 |
| 2026-02-27 to 02-28 | 6 | $712.85 |
| 2026-03-01 to 03-31 (month question) | 93 | $38,361.11 (latest date returned 03-26) |
| 2026-04-02 to 04-08 | 37 | $10,872.04 |
| 2026-04-11 to 04-12 | 1 | $200.00 (payee blank, GL 6210 Placement Fee, P19-003) |
| 2026-04-16 to 04-22 | 81 | $22,196.34 |
| 2026-04-27 to 04-29 | 109 | $34,739.94 |
| 2026-04-30 to 05-06 | 26 | $10,717.31 |
| 2026-05-14 to 05-15 | 43 | $13,042.11 |
| 2026-05-19 to 05-20 | 37 | $9,727.60 |
| 2026-05-21 to 05-27 | 12 | $4,384.84 |
| 2026-06-11 to 06-17 | 52 kept of 323 | $30,479.80 (see below) |
| 2026-06-18 to 06-19 | 10 | $684.35 |
| 2026-06-25 to 06-30 | 23 | $10,634.94 |

## Ranges that returned "none" (UNCONFIRMED, treat as a gap)
- 2026-01-01 to 01-14 (asked as weekly, Jan 1-2, 3-4, 5-6, 7-8, 9-10, 9-12, 11-12, 13-14, and Jan 2 and Jan 1-31)
- 2026-02-21 to 02-26 (Feb 21-22, 23-24, 24-25, 25-26) and 2026-02-18 (not asked on its own)
- 2026-03-05 to 03-11, 03-12 to 03-18, 03-19 to 03-25, 03-26 to 04-01 weekly all said "none" even though the March month question returned 93 rows for those dates. 2026-03-27 to 03-31 and 04-01 returned no rows (month question and Mar 31-Apr 1).
- 2026-04-09 to 04-10 (Realm-X said both bills were for Rosenbaum, so this one is probably genuine), 04-13 to 04-15, 04-23 to 04-26
- 2026-05-07 to 05-13 (May 7-8, 9-10, 11-13), 05-16 to 05-18, 05-28 to 05-31
- 2026-06-01 to 06-10 (weekly, Jun 1-10, Jun 1-2, 3, 4-5, 6-7, 8-10), 2026-06-20 to 06-24

## Failed / timed out
- 2026-05-18 to 05-20 (one question) timed out at 60s. It was split into May 18 (none) and May 19-20 (37 rows).

## Rows that are not vendor bills (kept as returned, except where noted)
- Realm-X also returns owner payments (GL 3250 Owner Draw), tenant move-out refunds (GL 2200 Clearing Account), one application-fee refund (GL 42031) and one -$10.00 refund adjustment. These appear as payees that are owners or former tenants. In the CSV there are 38 such rows, $51,361.85 together. Filter on gl_account if you want vendor bills only.
- June 11-17: Realm-X returned 323 rows, about 271 of them GL 3250 "Owner payment for 06/2026" lines created 2026-06-12. Those owner-draw lines were NOT written to the CSV (not vendor bills, too long to copy by hand). The other 52 rows are in the CSV. The omitted count is derived as 323 minus 52 and the omitted total is unknown. The 12 move-out refunds (GL 2200) for that week are included.
- Bill references that were returned as numbers with ".0" were cleaned to plain numbers. Created dates are exactly as returned (some are date only, some have a time).
- Rows are line-level: a bill with several GL accounts appears on several rows with the same reference. Do not count rows as bills.
- Inline results were copied into the CSV by hand from the tool output (Realm-X did not save them to disk). Row counts and totals were re-checked against Realm-X's stated figures for every file, but unusual characters in descriptions (such as bullets) were copied as seen.
