# How to pull Rentvine data

Output from the tools is cut off at about 30,000 characters, so pull in pieces.

## Bill lines (the main source)
Use the Expense Distribution report. Pull ONE MONTH at a time. Fastest method that was verified on 2026-10-01:
1. `run_report(route="expense-distribution", display_columns=["propertyName","unitName","payee","account","reference","description","amount","billDate","isPaid"], filters=[{"name":"datePosted","comparator":"betweenDate","startDate":"YYYY-MM-01","endDate":"YYYY-MM-DD"}], page_size=1)`
2. Take the CSV link from the result and read it with `ReadMcpResourceTool` (server `Rent-Vine`, URI `rentvine://reports/expense-distribution.csv?q=...`). The full month is saved to a file, which can be parsed with a script. Copy the `q=` value exactly; a single wrong character gives a decompress error.
3. Tie out every month: rows and the Amount total must equal the report header. The 2026-10-01 run: 40,598 rows YTD, all months matched.

Columns: `payee` is the vendor. `account` is the GL account, e.g. `59506: Water Utility Expense`. Utility accounts: 59501 electric, 59502 gas, 59503 sewer, 59504 trash, 59506 water, 59513/59514/59516/59517/59518 the matching taxes and fees. 59511 is the utility facilitation fee (not a utility bill).

A blank `propertyName` does NOT always mean no property. Pull the blank lines with `ledger` and `property` columns and filter `propertyName isEmpty`: they belong to owner/company ledgers (Thatcher Gym, Casa Grande Homes LLC, Rosenbaum Enterprises) or tenant ledgers.

Voided bills do not appear in this report.

## Other pulls
- Properties, who-pays, fee setting, status, contract dates: `run_report(route="property", display_columns=["propertyID","propertyName","isActive","dateContractBegins","dateContractEnds","managementFeeSetting","contacts","portfolio","unitCount","property_text_43".."property_text_47"], filters=[{"name":"isActive","comparator":"booleanAny"}])`, then read the CSV link.
- Leases and occupancy: `run_report(route="lease", display_columns=["propertyName","unitName","tenants","moveInDate","startDate","endDate","occupancyEndDate","primaryLeaseStatusID","leaseStatusID","rentAmount"])`, then read the CSV link.
- Renewals: `list_lease_renewals(lease_id)`; leases by address: `list_leases(search=...)`.
- Bill IDs, vendor and links: `list_bills(search=<reference>, start_date, end_date)`; details with `get_bill(bill_id, includes="contact,charges")`.
- Fee settings: `list_management_fee_settings(is_active=true)`.
- Non-standard fee properties: property report grouped by `managementFeeSetting`, filtered `managementFeeSettingID notIn` the standard IDs.
- Standard fee setting IDs. 10%: 8,14,15,16,30,35,37,45. 8%: 1,22,23,24,25,26,27,28,29,32,34,36,41,51. Classify new settings by their configured rate, not their name.
- The unit-management-fee report errors because a fee income account is not set in accounting settings. Skip it and say so once.
