# Coverage checklist (a run is complete only when all boxes are ticked)

## Cached Rentvine months (data/bills/)
- [ ] 2026-01  [ ] 2026-02  [ ] 2026-03  [ ] 2026-04  [ ] 2026-05  [ ] 2026-06  [ ] 2026-07  [ ] 2026-08
- [x] 2026-09 (tied 4,054 rows)  [x] 2026-10 (tied 4,562 rows)  [~] 2026-11 (partial to 11-16; re-pull)
Backfill order: 08, 07, ... 01. Each Monday run keeps going until all are cached; do not stop after one.

## Every full audit
- [ ] Row counts and totals tie to report header for every month
- [ ] analyze.py run on all months combined
- [ ] Check 1 renewals: status verified for every renewal fee (unpaid first)
- [ ] Check 2 fee settings: Rentvine + AppFolio Phase 1
- [ ] Check 3 account map across all months
- [ ] Check 4 duplicates across all months (reference, account+service month, vendor/property/amount)
- [ ] Check 5 utilities: occupancy for ALL electric bills (all months), water/sewer spikes vs trailing 3 months + last year
- [ ] AppFolio bills Jan to today (week by week); Phase 2 if report emails exist
- [ ] Every OPEN_ITEMS row re-checked
- [ ] Report .md, .xlsx, dashboard .html, baseline .json saved; committed and pushed
- [ ] Drive: master "Bills YTD" sheet updated and audit .xlsx uploaded to folder "Owner Statement Audit" (Tiffany@rosenbaumrealtygroup.com)
- [ ] Email sent; Dashboard Artifact published; push notification sent
