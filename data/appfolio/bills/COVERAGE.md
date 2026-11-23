# AppFolio bill cache coverage (2026-11-23)

Source: Realm-X bill-line exports, one month each, saved to files by the tool. Realm-X is NOT deterministic: the same month returns different line counts depending on wording ("bill date" vs "posted"), and some runs return only lines that have a vendor. Treat counts as UNCONFIRMED until a second source (AppFolio export) is available.

| Month | Lines | Amount | Lines with vendor name | Date field |
|---|---|---|---|---|
| 2026-01 | 941 | 517,805.06 | 158 | INVOICE_DATE |
| 2026-02 | 986 | 518,390.67 | 153 | INVOICE_DATE |
| 2026-03 | 975 | 481,625.29 | 100 | INVOICE_DATE |
| 2026-04 | 1188 | 531,470.43 | 237 | POSTING_DATE |
| 2026-05 | 1123 | 483,691.86 | 154 | INVOICE_DATE |
| 2026-06 | 276 | 124,058.68 | 276 | INVOICE_DATE |
| 2026-07 | 1241 | 499,713.77 | 192 | INVOICE_DATE |
| 2026-08 | 1347 | 575,314.72 | 236 | INVOICE_DATE |
| 2026-09 | 1447 | 533,137.30 | 290 | INVOICE_DATE |
| 2026-10 | 1599 | 539,541.40 | 311 | INVOICE_DATE |
| 2026-11 | 1331 | 517,619.80 | 141 | INVOICE_DATE |

Suspicious: June (276 lines, all with a vendor) looks like the vendor-only subset, while May, Sep and Oct had 1,100-1,600 lines. Compare each month with an AppFolio export before relying on it.