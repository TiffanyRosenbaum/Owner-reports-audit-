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
Audited 2026-10-01: September 1 to October 1. NOT yet audited: January to August, and AppFolio renewals. Do one month per run until caught up.
