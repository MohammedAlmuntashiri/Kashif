# Kashif - AI-Powered Financial Analysis for Tadawul

Kashif helps individual investors analyze Saudi stock market (Tadawul) companies by:

- Extracting 10 key financial values from company reports
- Calculating fair value using 3 models (DCF, P/E, P/B) with sector-adjusted weights
- Comparing companies against sector peers
- Showing valuation status: undervalued, fairly valued, or overvalued

## Tech Stack

- **Backend:** Flask + SQLAlchemy + Flask-Migrate + PostgreSQL
- **Frontend:** React + Tailwind CSS

## Quick Start (Docker)

```bash
git clone <repo>
cd Kashif
docker-compose up
```

That's it. Open http://localhost:5000

## Local Development (without Docker)

```bash
# Start PostgreSQL (install it first)
# Create a database and user

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example .env   # then edit .env with your DB credentials
flask db upgrade
flask run

# Frontend
cd frontend
npm install
npm start
```
