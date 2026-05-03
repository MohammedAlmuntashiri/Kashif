# PDF test fixtures

The PDFs themselves are gitignored — large binaries don't belong in the repo
and they're publicly available from each company's investor relations page.

## What goes here

14 files: 2024 annual reports for 7 Tadawul-listed companies, English + Arabic.

| Ticker | Company                                  | English file                          | Arabic file                           |
|--------|------------------------------------------|---------------------------------------|---------------------------------------|
| 2222   | Saudi Arabian Oil Company (Aramco)       | `2222_aramco_2024_annual_en.pdf`      | `2222_aramco_2024_annual_ar.pdf`      |
| 1120   | Al Rajhi Banking and Investment Corp.    | `1120_alrajhi_2024_annual_en.pdf`     | `1120_alrajhi_2024_annual_ar.pdf`     |
| 2010   | Saudi Basic Industries Corp. (SABIC)     | `2010_sabic_2024_annual_en.pdf`       | `2010_sabic_2024_annual_ar.pdf`       |
| 4190   | Jarir Marketing Company                  | `4190_jarir_2024_annual_en.pdf`       | `4190_jarir_2024_annual_ar.pdf`       |
| 7010   | Saudi Telecom Company (STC)              | `7010_stc_2024_annual_en.pdf`         | `7010_stc_2024_annual_ar.pdf`         |
| 2280   | Almarai Company (out-of-sample anchor)   | `2280_almarai_2024_annual_en.pdf`     | `2280_almarai_2024_annual_ar.pdf`     |
| 7030   | Mobile Telecom. Co. Saudi Arabia (Zain)  | `7030_zain_2024_annual_en.pdf`        | `7030_zain_2024_annual_ar.pdf`        |

## Naming convention

`<ticker>_<short_name>_<year>_annual_<lang>.pdf`
- `<lang>` is `en` or `ar`
- `<year>` matches the report's fiscal year, used by `test_extractor.py`
  to look up the corresponding `financial_data.period` (e.g. `2024-annual`)

## Where to download

Each company publishes annual reports on its investor relations page, and the
Saudi Exchange (Tadawul) issuer disclosure pages link to them as well. Search:

> "<company name> 2024 annual report"

…and grab the official English and Arabic versions.

## Why these 7 companies

One per major sector to cover the breadth the extractor needs to handle,
plus two out-of-sample anchors we deliberately did *not* use to tune the
keyword lists. If a fix only ever lands the out-of-sample anchors correctly
when we tweaked the code with the other 5 in mind, that's our signal that
it generalised.

- 2222 — Energy
- 1120 — Banks
- 2010 — Materials
- 4190 — Consumer Discretionary Distribution & Retail
- 7010 — Telecommunication Services
- 2280 — Consumer Staples (Food & Beverages)  *(out-of-sample)*
- 7030 — Telecommunication Services (second telecom for cross-checking)  *(out-of-sample)*
