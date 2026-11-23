# Coverage checklist (a run is complete only when all boxes are ticked)

## Cached Rentvine months (data/bills/)
- [x] 2026-01  [x] 2026-02  [x] 2026-03  [x] 2026-04  [x] 2026-05  [x] 2026-06  [x] 2026-07  [x] 2026-08 (all tied 2026-11-23)
- [x] 2026-09 (tied 4,054 rows)  [x] 2026-10 (re-pulled, tied 4,613 rows)  [x] 2026-11 (re-pulled to 11-23, tied 3,527 rows; re-pull again next run)
All Jan-Nov cached as of 2026-11-23.

## Every full audit
- [x] Row counts and totals tie to report header for every month
- [x] analyze_full.py run (audit/scripts/analyze_full.py + build_findings.py + build_outputs.py; inputs: property and lease report CSVs) on all months combined
- [~] Check 1 renewals: 4 of 8 suspect units verified + OI-010; unpaid renewals not individually verified; AppFolio fees not linkable
- [x] Check 2 fee settings name-vs-config + AppFolio Phase 1 (effective-rate review NOT run)
- [x] Check 3 account map (first-time vendor >$500 NOT run) across all months
- [x] Check 4 duplicates (Rentvine) across all months (reference, account+service month, vendor/property/amount)
- [~] Check 5 utilities: occupancy for ALL bills done; spikes vs trailing 3 months only (last-year baseline NOT pulled)
- [~] AppFolio bills Jan-Nov cached in data/appfolio/bills/ (completeness UNCONFIRMED; AppFolio occupancy/electric/spike checks not run)
- [x] Every OPEN_ITEMS row re-checked
- [x] Report .md, .xlsx, dashboard .html, baseline .json saved; committed and pushed
- [~] Drive: 11 monthly ledger sheets "Bills YTD 2026-MM" + audit xlsx uploaded (split approved; no single combined master sheet)
- [x] Dashboard Artifact published (https://claude.ai/artifact/SfXdUHfCdH3RbLf3uTghdA)  - [x] Email sent  - [x] Push notification sent
