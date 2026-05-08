# Phase 5 PDF Extractor — Accuracy Report

**Generated:** 2026-05-08  
**Scope:** 10 Saudi-listed companies × 10 financial values × 2024 annual reports (English PDFs)  
**Test harness:** `backend/test_extractor.py`  
**Extractor:** `backend/app/services/pdf_extractor.py`

---

## Summary

| Value | Match | Disagree | Fail | Accuracy |
|---|---|---|---|---|
| revenue | 10/10 | 0 | 0 | **100%** |
| net_income | 10/10 | 0 | 0 | **100%** |
| eps | 10/10 | 0 | 0 | **100%** |
| total_assets | 10/10 | 0 | 0 | **100%** |
| shareholders_equity | 10/10 | 0 | 0 | **100%** |
| total_borrowings | 10/10 | 0 | 0 | **100%** |
| cash_and_equivalents | 10/10 | 0 | 0 | **100%** |
| free_cash_flow | 10/10 | 0 | 0 | **100%** |
| shares_outstanding | 10/10 | 0 | 0 | **100%** |
| dividends_per_share | 9/10 | 1 | 0 | **90%** |
| **OVERALL** | **99/100** | | | **99%** |

Tolerances: ±5% for currency values; ±0.1% (effectively exact) for EPS, DPS, and shares.

---

## Extraction Matrix

`✓` = MATCH &nbsp; `✗` = DISAGREE &nbsp; `—` = FAIL &nbsp; `·` = N/A

| Company | Rev | NI | EPS | TA | SE | Borr | Cash | FCF | Shr | DPS |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 2222 Aramco | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1120 Al Rajhi | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2010 SABIC | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4190 Jarir | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7010 STC | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2280 Almarai *(out-of-sample)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7030 Zain *(out-of-sample)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1180 SNB *(out-of-sample)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4013 Habib *(out-of-sample)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** |
| 8210 Bupa *(out-of-sample)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Column headers: Rev = revenue, NI = net\_income, TA = total\_assets, SE = shareholders\_equity,  
Borr = total\_borrowings, Cash = cash\_and\_equivalents, FCF = free\_cash\_flow,  
Shr = shares\_outstanding, DPS = dividends\_per\_share.

---

## Extracted Values vs. Expected (Detail)

All values in SAR unless noted.

### Revenue

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 1,801,674,000,000 | 1,801,674,000,000 | MATCH |
| 1120 Al Rajhi | 32,055,303,000 | 32,055,303,000 | MATCH |
| 2010 SABIC | 139,980,500,000 | 139,980,000,000 | MATCH |
| 4190 Jarir | 10,830,921,000 | 10,830,921,000 | MATCH |
| 7010 STC | 75,893,413,000 | 75,893,413,000 | MATCH |
| 2280 Almarai | 20,979,512,000 | 20,979,512,000 | MATCH |
| 7030 Zain | 10,365,461,000 | 10,365,461,000 | MATCH |
| 1180 SNB | 36,038,363,000 | 36,038,363,000 | MATCH |
| 4013 Habib | 11,200,434,264 | 11,200,000,000 | MATCH |
| 8210 Bupa | 18,101,517,000 | 18,101,517,000 | MATCH |

### Net Income (attributable to shareholders of parent)

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 398,422,000,000 | 393,891,000,000 | MATCH |
| 1120 Al Rajhi | 19,722,206,000 | 19,722,206,000 | MATCH |
| 2010 SABIC | 1,538,542,000 | 1,538,542,000 | MATCH |
| 4190 Jarir | 973,955,000 | 973,955,000 | MATCH |
| 7010 STC | 24,688,652,000 | 24,688,652,000 | MATCH |
| 2280 Almarai | 2,313,100,000 | 2,313,100,000 | MATCH |
| 7030 Zain | 596,369,000 | 596,369,000 | MATCH |
| 1180 SNB | 21,192,995,000 | 21,192,995,000 | MATCH |
| 4013 Habib | 2,315,290,800 | 2,315,000,000 | MATCH |
| 8210 Bupa | 1,166,002,000 | 1,166,002,000 | MATCH |

### EPS (SAR per share)

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 1.6300 | 1.6300 | MATCH |
| 1120 Al Rajhi | 4.6700 | 4.6700 | MATCH |
| 2010 SABIC | 0.5100 | 0.5100 | MATCH |
| 4190 Jarir | 0.8100 | 0.8100 | MATCH |
| 7010 STC | 4.9500 | 4.9500 | MATCH |
| 2280 Almarai | 2.3400 | 2.3400 | MATCH |
| 7030 Zain | 0.6600 | 0.6600 | MATCH |
| 1180 SNB | 3.4400 | 3.4400 | MATCH |
| 4013 Habib | 6.6200 | 6.6200 | MATCH |
| 8210 Bupa | 7.7900 | 7.7900 | MATCH |

### Total Assets

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 2,423,630,000,000 | 2,423,630,000,000 | MATCH |
| 1120 Al Rajhi | 974,386,656,000 | 972,444,354,000 | MATCH |
| 2010 SABIC | 278,018,793,000 | 277,543,843,000 | MATCH |
| 4190 Jarir | 4,272,604,000 | 4,272,694,000 | MATCH |
| 7010 STC | 160,638,143,000 | 160,638,143,000 | MATCH |
| 2280 Almarai | 35,567,960,000 | 35,567,960,000 | MATCH |
| 7030 Zain | 28,135,461,000 | 28,135,461,000 | MATCH |
| 1180 SNB | 1,104,154,640,000 | 1,104,154,640,000 | MATCH |
| 4013 Habib | 20,557,929,072 | 20,558,000,000 | MATCH |
| 8210 Bupa | 15,575,080,000 | 15,575,080,000 | MATCH |

### Shareholders' Equity (attributable to shareholders of parent)

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 1,458,229,000,000 | 1,458,229,000,000 | MATCH |
| 1120 Al Rajhi | 123,032,830,000 | 123,032,830,000 | MATCH |
| 2010 SABIC | 156,833,133,000 | 156,358,183,000 | MATCH |
| 4190 Jarir | 1,744,852,000 | 1,744,852,000 | MATCH |
| 7010 STC | 89,416,542,000 | 89,416,542,000 | MATCH |
| 2280 Almarai | 18,790,736,000 | 18,790,736,000 | MATCH |
| 7030 Zain | 10,706,837,000 | 10,706,837,000 | MATCH |
| 1180 SNB | 192,565,439,000 | 192,565,439,000 | MATCH |
| 4013 Habib | 7,175,142,519 | 7,175,000,000 | MATCH |
| 8210 Bupa | 5,117,997,000 | 5,117,997,000 | MATCH |

### Total Borrowings (debt + lease obligations)

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 319,290,000,000 | 319,290,000,000 | MATCH |
| 1120 Al Rajhi | 8,450,753,000 | 8,450,000,000 | MATCH |
| 2010 SABIC | 35,198,069,000 | 35,198,069,000 | MATCH |
| 4190 Jarir | 782,756,000 | 791,756,000 | MATCH |
| 7010 STC | 17,295,824,000 | 17,295,824,000 | MATCH |
| 2280 Almarai | 10,615,191,000 | 10,667,789,000 | MATCH |
| 7030 Zain | 9,687,756,000 | 9,687,756,000 | MATCH |
| 1180 SNB | 95,305,371,000 | 96,445,481,000 | MATCH |
| 4013 Habib | 8,165,469,568 | 8,165,000,000 | MATCH |
| 8210 Bupa | 144,817,000 | 144,817,000 | MATCH |

### Cash and Equivalents

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 216,642,000,000 | 216,642,000,000 | MATCH |
| 1120 Al Rajhi | 72,774,437,000 | 73,400,855,000 | MATCH |
| 2010 SABIC | 30,539,668,000 | 29,413,668,000 | MATCH |
| 4190 Jarir | 32,835,000 | 32,835,000 | MATCH |
| 7010 STC | 15,543,441,000 | 15,543,441,000 | MATCH |
| 2280 Almarai | 528,214,000 | 528,214,000 | MATCH |
| 7030 Zain | 840,201,000 | 839,133,000 | MATCH |
| 1180 SNB | 63,208,121,000 | 62,343,921,000 | MATCH |
| 4013 Habib | 2,890,702,697 | 2,891,000,000 | MATCH |
| 8210 Bupa | 925,190,000 | 925,190,000 | MATCH |

### Free Cash Flow

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 319,998,000,000 | 319,998,000,000 | MATCH |
| 1120 Al Rajhi | 49,559,511,000 | 49,559,511,000 | MATCH |
| 2010 SABIC | 6,244,276,000 | 6,158,367,000 | MATCH |
| 4190 Jarir | 1,051,090,000 | 1,051,090,000 | MATCH |
| 7010 STC | 8,122,419,000 | 7,958,561,000 | MATCH |
| 2280 Almarai | 1,133,573,000 | 1,133,573,000 | MATCH |
| 7030 Zain | 1,456,292,000 | 1,456,292,000 | MATCH |
| 1180 SNB | -44,040,456,000 | -44,040,456,000 | MATCH |
| 4013 Habib | -858,191,855 | -858,190,000 | MATCH |
| 8210 Bupa | 1,321,226,000 | 1,321,226,000 | MATCH |

### Shares Outstanding

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 241,894,000,000 | 241,854,700,000 | MATCH |
| 1120 Al Rajhi | 4,000,000,000 | 4,000,000,000 | MATCH |
| 2010 SABIC | 3,000,000,000 | 3,000,000,000 | MATCH |
| 4190 Jarir | 1,200,000,000 | 1,200,000,000 | MATCH |
| 7010 STC | 4,986,916,000 | 4,986,916,000 | MATCH |
| 2280 Almarai | 988,191,000 | 988,191,000 | MATCH |
| 7030 Zain | 898,729,000 | 898,729,175 | MATCH |
| 1180 SNB | 5,944,649,000 | 5,945,000,000 | MATCH |
| 4013 Habib | 350,000,000 | 350,000,000 | MATCH |
| 8210 Bupa | 150,000,000 | 150,000,000 | MATCH |

### Dividends per Share (SAR per share)

| Company | Extracted | Expected | Status |
|---|---:|---:|:---:|
| 2222 Aramco | 1.9260 | 1.9260 | MATCH |
| 1120 Al Rajhi | 2.4000 | 2.4000 | MATCH |
| 2010 SABIC | 3.4000 | 3.4000 | MATCH |
| 4190 Jarir | 0.8300 | 0.8300 | MATCH |
| 7010 STC | 2.6000 | 2.6000 | MATCH |
| 2280 Almarai | 1.0000 | 1.0000 | MATCH |
| 7030 Zain | 0.5000 | 0.5000 | MATCH |
| 1180 SNB | 1.8000 | 1.8000 | MATCH |
| 4013 Habib | **3.5400** | **4.7700** | **DISAGREE** |
| 8210 Bupa | 4.0000 | 4.0000 | MATCH |

---

## Known Limitations

### Habib (4013) DPS: 3.54 vs 4.77 — by design

The extractor returns **SAR 3.54**, which is the Q1–Q3 2024 subtotal explicitly stated in Habib's 2024 annual report PDF. The full-year figure of **SAR 4.77** (per Argaam/yfinance) includes Q4 2024 (SAR 1.23/share), which was declared in February 2025 — after the annual report was approved and published. The "Subsequent Events" note in the PDF states "no significant events." This value is not recoverable from the 2024 annual report body alone and is counted as a known limitation, not a bug.

### Arabic PDFs — deferred to Part 13

All 10 companies have Arabic-language annual reports. OCR cannot reliably read image-rendered Arabic financial-statement pages with the current pdfplumber + pytesseract pipeline. Arabic extraction is deferred to Phase 5 Part 13, which will introduce a Mistral-based fallback. The test harness marks Arabic PDFs as N/A by default (`--with-ar` flag required to attempt them).

---

## Design Decisions (Conventions, Not Bugs)

These explain cases where the extractor's value differs from a third-party aggregator (Argaam, yfinance) but is correct per the Tadawul official filing:

| Company | Field | Convention |
|---|---|---|
| Al Rajhi / SNB | revenue | PDF "Total Revenue (Operating)" — Argaam sometimes shows post-provisions "Net operating income", which is lower |
| Al Rajhi / SNB | cash\_and\_equivalents | Two-component bank sum: Cash with Central Bank + Due from banks |
| Al Rajhi / SNB | total\_borrowings | Sukuk Issued / Debt securities only — excludes customer deposits and AT1 hybrids |
| Banks (general) | free\_cash\_flow | PDF-reported OCF is the Tadawul source of truth |
| Almarai | shares\_outstanding | 988,191,000 (PDF EPS-note weighted average) — yfinance shows 993,991,250 (issued count) |
| Aramco | shares\_outstanding | 241,894,000,000 (EPS-note weighted average, inline "(in millions)" overrides page SAR'000 unit) |
| Al Rajhi | dividends\_per\_share | 2.40 = H2 2023 (SAR 1.15, paid Apr 2024) + H1 2024 (SAR 1.25, paid Aug 2024) — "paid during calendar year 2024" basis |
| STC | dividends\_per\_share | 2.60 = 4 quarters × SAR 0.40 (Q4'23 + Q1–Q3'24) + SAR 1.00 extra (2023 GA) |
| SABIC | dividends\_per\_share | 3.40 = SAR 1.70 H1 + SAR 1.70 H2 — DB was incorrectly seeded as 3.30 (corrected) |

---

## Scope

- **Period:** 2024 annual reports only. Quarterly support is Phase 6 (planned, not started).
- **Language:** English PDFs only. Arabic deferred to Part 13.
- **Companies tested:** 10 of 48 seeded, spanning energy, banks, materials, retail, telecom, consumer staples, healthcare, and insurance — designed to cover the main structural variants found in Tadawul filings.
- **PDF source:** Tadawul official disclosures (PDFs are gitignored — see `backend/test_pdfs/SOURCES.md`).
- **Ground truth:** Tadawul official disclosures. Where DB seeds disagree with Tadawul, Tadawul is correct and the DB seed is updated.
