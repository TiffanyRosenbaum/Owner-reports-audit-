# The checks

Run each check for the current month AND for current month vs. YTD. RED = likely error costing an owner money. YELLOW = a person must confirm. Every flag lists: owner, property, unit, vendor, reference, amount, bill date, paid/unpaid, what was checked, and the suggested action.

## Check 1 — Lease renewal fees (renewals are done on the UNIT)
Find renewal fee lines (description contains "renewal") with the unit. Pull leases and their renewals for the property.
- RED: a unit charged more than one renewal fee for the same renewal term.
- RED: a property with more renewal fees YTD than completed renewals.
- RED: a renewal fee charged when the unit's renewal is not marked Complete (for example "In Progress").
- RED: the same lease with two renewals starting in the same year.
- YELLOW: fee amount does not match the property's fee setting. Percentage fees should equal the stated % of rent, within $1.

## Check 2 — Management fee rates
- RED: a setting whose NAME says one amount but is CONFIGURED for another (monthly, lease or renewal fee).
- RED: the same owner or the same building on different rates.
- RED: effective fee rate more than 0.5 percentage points off the setting, or a flat fee that does not match (estimate using scheduled rent; fees also apply to late fees and other receipts, so treat as a review list).
- YELLOW: active records named TEST, or with a blank property or owner.
- WATCH LIST: every property not on 8% or 10%, grouped by owner. In the email/dashboard show only new or changed since yesterday. Put the full list in the saved report.

## Check 3 — Bills on the wrong building (unit -> building -> owner)
Build an account map from YTD bills: normalized account number -> property/unit each month.
- RED: an account billed to more than one property in the same month (unless a known split).
- RED: an account that moves to a different property than in prior months.
- RED: any bill on a TEST property.
- YELLOW: a bill with no property code (resolve the ledger; it may be an owner or company ledger).
- YELLOW: a description or reference with an address that does not match the property it is posted to.
- YELLOW: a bill on an inactive property or one outside its management contract dates.
- YELLOW: a vendor billing a property for the first time this year, over $500.

## Check 4 — Duplicate bills (all types)
Normalize account numbers before comparing: remove month tags (9/26, 09/26, Sep-26, "(2nd Half)"), "Acct #", "#", leading date stamps like "20230825-", spaces and dashes. Add up all lines of a bill (same reference + bill date + property) before comparing.
- RED: same account + property billed twice for the same service month, totals within $1.
- RED: the same invoice/reference posted twice on a property, even if one copy has a unit and the other does not.
- RED: maintenance bill with the same vendor + same property/unit + same amount (within $1) within 30 days.
- RED (AppFolio): an "Uploaded Invoice" bill and a work-order bill for the same vendor, property and amount.
- YELLOW: same vendor + same unit + same kind of work within 30 days at different amounts.
- YELLOW: a utility account with two bills in one month at different amounts (compare service dates).
- YELLOW: a "Markup:" manager bill (payee Rosenbaum Realty Group) without a matching vendor bill, or not equal to 10%.
- DO NOT flag utility/water/sewer bills that fall in different billing months. Utilities repeat monthly.
- Do not flag duplicates that were already voided. Count them as "caught and voided".

## Check 5 — Utilities
5a. Cross-reference who pays and who lives there (Rentvine property fields property_text_43 electric, _44 water, _45 gas, _46 sewer, _47 trash; AppFolio unit record).
- RED: a utility bill where that utility is "Resident pays" AND a resident lives in the unit/home when the bill arrives (lease dates). Multi-unit properties where the unit is not on the bill are YELLOW.
- YELLOW: Resident pays but no resident found (vacant), a resident moved in or out within 30 days, or who-pays is blank.
5b. Water/sewer spikes. Compare each account's bill total to its trailing 3-month average AND the same month last year.
- RED: 50%+ above both baselines ("possible leak — send maintenance").
- YELLOW: 25–50% above both, or 3 months of increases in a row.
- YELLOW: sewer up 30%+ while water is flat.
- Skip accounts with fewer than 3 months of history and list them as "not enough history".
5c. Report utility duplicates (from Check 4) in their own section.
