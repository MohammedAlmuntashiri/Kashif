# Kashif — Tadawul Financial Analysis Platform

Kashif (Arabic: كاشف, "the one that reveals") is a full-stack analyst tool for
the Saudi Stock Exchange (Tadawul). It extracts financial values from annual
report PDFs, computes a blended fair value per stock using three valuation
models, and lets users browse, compare, and follow listed companies — all in a
bilingual English / Arabic interface.

---

## What it does

- **Auto-extracts 10 financial values** (Revenue, Net Income, EPS, Total Assets,
  Total Borrowings, Shareholders Equity, Cash & Equivalents, Free Cash Flow,
  DPS, Shares Outstanding) from uploaded annual-report PDFs.
- **Blended fair-value engine** combining Discounted Cash Flow, P/E multiple,
  and P/B multiple — weights per sector, conflict resolution toward the DB
  (Tadawul filings are treated as source of truth).
- **Live price feed** during market hours: a scheduler container refreshes
  prices via yfinance every 10 minutes during 10:00–15:00 Asia/Riyadh,
  Sunday–Thursday, then recomputes valuations and sector comparisons.
- **Bilingual UI + bilingual PDF reports** (EN / AR), full RTL support,
  Tajawal Arabic font + Inter/Space Grotesk Latin.
- **Per-user features** behind JWT auth: watchlist, freeform notes per stock,
  recently-viewed strip (browser-local), sign-in / sign-up.
- **Sector peer browsing**, 7-ratio comparison table, valuation gauge,
  4-year historical financial table on every stock page.
- **PDF upload preview**: extracts a PDF in dry-run mode, shows diff vs DB
  with color-coded accuracy %, exports CSV / JSON / styled PDF report
  (English or Arabic).

---

## Extractor accuracy

The PDF extractor in `backend/app/services/pdf_extractor.py` (~2,840 lines) is
a keyword-based parser tuned over six iterations on real Tadawul annual
reports. It runs three passes (standard pdfplumber text, row-clustered word
coordinates for columnar layouts, OCR fallback via pytesseract for
image-heavy PDFs), then picks the highest-confidence value per field and
cross-validates EPS against `net_income / shares_outstanding`.

**Current accuracy on the full 49-stock corpus** (49 × 4 years × 10 fields
= 1,920 cells, measured against the Tadawul-verified database):

| Metric | Result |
|---|---|
| Overall | **72.3%** (1,345 / 1,920 cells correct within 1% tolerance) |

Per-field accuracy varies because some line items are reported far more
consistently than others:

| Field | Accuracy |
|---|---|
| Total Assets | 87.5% |
| Cash & Equivalents | 87.5% |
| EPS | 84.9% |
| Shares Outstanding | 83.3% |
| Shareholders Equity | 74.5% |
| Revenue | 70.8% |
| Net Income | 67.7% |
| Total Borrowings | 62.0% |
| Dividends Per Share | 54.2% |
| Free Cash Flow | 49.0% |

Notes on methodology:

- **English-only.** Arabic shaping/regex was stripped in Phase 5.12.5 since
  the corpus is `_En.pdf` only; this added +0.16pp and removed 113 lines of
  dead-weight code.
- **Tadawul is the source of truth**, not the database. When uploading via
  the UI, the dry-run preview compares extracted values to the DB but you
  should sanity-check against the actual Tadawul filing.
- **A separate, curated 10-stock test corpus** (one annual per company)
  scores 99/100 — see `ACCURACY_REPORT.md` for the per-stock breakdown.
- **Known limitations**: 5 of 49 stocks have unvaluable cells because the
  underlying companies are loss-making (3), insolvent (1 — negative book
  equity), or sole-listed in their sector (1). The stock detail page shows
  an explanation banner instead of a fake fair value.

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Flask + SQLAlchemy + Flask-Migrate + Flask-Cors |
| Database | PostgreSQL 16 |
| Auth | bcrypt + PyJWT (HS256, 7-day token expiry) |
| PDF extraction | pdfplumber + pytesseract + pdf2image |
| PDF reports | ReportLab + arabic-reshaper + python-bidi + Noto Sans Arabic |
| Market data | yfinance (Tadawul tickers as `<ticker>.SR`) |
| Scheduler | Lightweight Python loop in its own container |
| Frontend | React 18 + React Router 6 + Tailwind 3 + axios |
| Build tool | Create React App (`react-scripts` 5.0.1) |
| Animation | framer-motion |
| Charts | Recharts (lazy-mounted via IntersectionObserver) |
| Toasts | sonner |
| Tests | pytest |
| DevOps | Docker Compose (4 services: db, backend, scheduler, pgAdmin) |

---

## Repository layout

```
Kashif/
├── backend/
│   ├── app/
│   │   ├── api/              Flask blueprints (stocks, sectors, valuations,
│   │   │                      comparisons, pdf, auth, watchlist, notes, …)
│   │   ├── models/           SQLAlchemy models
│   │   ├── services/         Business logic (DCF, PE, PB, valuation_engine,
│   │   │                      report_service, pdf_extractor, …)
│   │   └── config.py
│   ├── migrations/           Alembic
│   ├── tests/                pytest unit tests
│   ├── seed.py               Initial sector + sector-weight seeds
│   ├── seed_stocks.py        Bulk-create 49 Tadawul stocks via yfinance
│   ├── update_prices.py      One-shot: refresh all market prices
│   ├── run_valuations.py     One-shot: recompute valuations
│   ├── run_comparisons.py    One-shot: recompute sector comparisons
│   ├── scheduler.py          Long-running loop wired into docker-compose
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   └── src/
│       ├── pages/            HomePage, StockDetailPage, ComparePage,
│       │                      WatchlistPage, SignIn/Up, About, Sector
│       ├── components/       common/, stocks/, news/
│       ├── services/         api.js (axios + JWT), finnhub.js
│       ├── hooks/            usePolling
│       ├── auth/             AuthContext (JWT in localStorage)
│       ├── i18n/             LanguageContext + translations.js (EN + AR)
│       └── utils/            format, logos, market, time
├── docker-compose.yml
└── README.md                 (you are here)
```

---

## Quick start (Docker — recommended)

```bash
git clone <repo-url>
cd Kashif

# 1. Create your .env at the repo root (see "Environment variables" below)

# 2. Boot all 4 services (db, backend, pgAdmin, scheduler)
docker-compose up -d --build

# 3. Seed the database (one time)
docker exec kashif-backend-1 python seed.py          # sectors + weights
docker exec kashif-backend-1 python seed_stocks.py   # 49 Tadawul stocks via yfinance
docker exec kashif-backend-1 python run_valuations.py
docker exec kashif-backend-1 python run_comparisons.py

# 4. Start the frontend dev server
cd frontend
npm install
npm start
```

| URL | What |
|---|---|
| http://localhost:3000 | The app |
| http://localhost:5000/api/stocks/ | Backend API |
| http://localhost:5050 | pgAdmin (login defined in `docker-compose.yml`) |
| `localhost:5433` | PostgreSQL (user/pass from your `.env`) |

> ⚠️ **Before any deployment**: change the pgAdmin login in `docker-compose.yml`,
> rotate `POSTGRES_PASSWORD`, and generate a strong `SECRET_KEY`. The defaults
> in this repo are local-dev only.

---

## Environment variables

Create `.env` in the repo root (the file is gitignored, never committed).
Pick your own values — these are required:

```dotenv
POSTGRES_DB=<your-db-name>
POSTGRES_USER=<your-db-user>
POSTGRES_PASSWORD=<choose-a-strong-password>

DATABASE_URL=postgresql://<your-db-user>:<your-db-password>@localhost:5432/<your-db-name>
SECRET_KEY=<long-random-string-for-jwt-signing>
FLASK_ENV=development
```

Generate a `SECRET_KEY` with `python -c "import secrets; print(secrets.token_hex(32))"`.

Optional — create `frontend/.env.local` for live market news on the homepage:

```dotenv
REACT_APP_FINNHUB_KEY=your_finnhub_key_here
```

Without the Finnhub key the homepage news block falls back to bundled mocks.
The rest of the app works fully without it.

---

## API surface

All endpoints are JSON. Authenticated routes require
`Authorization: Bearer <jwt>` (returned by `/api/auth/signin`).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/stocks/` | All stocks with snapshot fields |
| `GET` | `/api/stocks/<ticker>` | Stock detail + financials + valuation |
| `POST` | `/api/stocks/` | Add a new stock |
| `GET` | `/api/sectors/` | Sectors with weights |
| `GET` | `/api/valuations/<ticker>` | On-demand DCF/PE/PB recompute |
| `GET` | `/api/comparisons/` | 7-ratio peer comparison table (`?sector=` filter) |
| `POST` | `/api/pdf/upload` | Upload a financial PDF (use `?dry_run=true` for preview) |
| `POST` | `/api/pdf/upload_batch` | Multi-file upload, parallel extraction |
| `POST` | `/api/pdf/report/<ticker>?lang=en\|ar` | Render a styled PDF report |
| `POST` | `/api/auth/signup` | Create account, returns JWT |
| `POST` | `/api/auth/signin` | Authenticate, returns JWT |
| `GET` | `/api/auth/me` | Current user (requires JWT) |
| `GET/POST/DELETE` | `/api/watchlist/[<ticker>]` | Per-user starred stocks (JWT) |
| `GET/PUT/DELETE` | `/api/notes/<ticker>` | Per-user note (JWT) |

---

## Tadawul market hours and the scheduler

Tadawul trades **Sunday – Thursday, 10:00–15:00 Asia/Riyadh**. The
`scheduler` container runs `backend/scheduler.py`, which checks every 30
seconds and — on every 10-minute boundary during the trading window —
runs in sequence:

1. `update_prices.py` — yfinance for all 49 stocks.
2. `run_valuations.py` — recomputes DCF / PE / PB / blended fair value.
3. `run_comparisons.py` — refreshes the 7-ratio sector comparison rows.

Force a refresh outside the schedule:

```bash
docker exec kashif-scheduler-1 python -c "from scheduler import run_pipeline; run_pipeline()"
```

---

## Testing

```bash
docker exec kashif-backend-1 pytest tests/ -v
```

Current suite: 39 unit tests on the two highest-impact pure functions
(`valuation_engine.compute_status` and `pdf._values_match`). Runs in
under 5 seconds.

---

## Updating after `git pull`

```bash
git status                          # confirm clean tree, on main
git pull origin main
docker-compose up -d --build        # safety: rebuild if Dockerfile / requirements changed
cd frontend && npm install          # only if package.json changed
```

A `.gitattributes` file forces `*.sh` and `Dockerfile` to LF on checkout
so Windows clones can't accidentally introduce CRLF endings inside
Linux containers.

---

## Internationalization

The UI supports English (LTR) and Arabic (RTL). Toggle via the language
button in the navbar. All static strings live in
`frontend/src/i18n/translations.js`. Tajawal is loaded for Arabic glyphs;
the browser picks per character so Latin numbers stay in Inter.

PDF reports are rendered separately by `backend/app/services/report_service.py`
with Noto Sans Arabic + python-bidi + arabic-reshaper to handle script
shaping and bidirectional layout.

---

## Production checklist (not yet hardened)

- [ ] Strong `POSTGRES_PASSWORD` in `.env` (not the dev default)
- [ ] Strong `SECRET_KEY` in `.env` (generated, not the dev default)
- [ ] Change pgAdmin login in `docker-compose.yml`, or remove the pgAdmin
      service from production compose entirely
- [ ] Switch backend from `flask run` to `gunicorn` (already in `requirements.txt`)
- [ ] Move JWT from `localStorage` to httpOnly cookies + CSRF
- [ ] HTTPS / real domain
- [ ] Consider WAL backups for PostgreSQL
- [ ] Rotate the borrowed Finnhub key (if you reused someone else's)

---

## License

Internal project. All rights reserved.
