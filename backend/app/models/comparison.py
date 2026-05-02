# comparison.py — Peer-comparison snapshot for one stock within its sector
#
# Wide schema: for each of the 7 ratios we store the stock's own value,
# the sector average, and the stock's rank within its sector. One row per
# stock per run (same wipe-and-rebuild pattern as valuations).
#
# Ranks are 1-based with rank=1 always meaning "best":
#   lower-is-better:  pe_ratio, pb_ratio, debt_to_equity
#   higher-is-better: roe, roa, profit_margin, dividend_yield

from datetime import datetime
from app.extensions import db


class Comparison(db.Model):
    __tablename__ = 'comparisons'

    id = db.Column(db.Integer, primary_key=True)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)

    # ── Stock's own ratios ──
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    roe = db.Column(db.Float)               # %
    roa = db.Column(db.Float)               # %
    debt_to_equity = db.Column(db.Float)
    profit_margin = db.Column(db.Float)     # %
    dividend_yield = db.Column(db.Float)    # %

    # ── Sector averages (denormalized snapshot for fast reads) ──
    sector_avg_pe = db.Column(db.Float)
    sector_avg_pb = db.Column(db.Float)
    sector_avg_roe = db.Column(db.Float)
    sector_avg_roa = db.Column(db.Float)
    sector_avg_debt_to_equity = db.Column(db.Float)
    sector_avg_profit_margin = db.Column(db.Float)
    sector_avg_dividend_yield = db.Column(db.Float)

    # ── Ranks within sector (1 = best) ──
    pe_rank = db.Column(db.Integer)
    pb_rank = db.Column(db.Integer)
    roe_rank = db.Column(db.Integer)
    roa_rank = db.Column(db.Integer)
    debt_to_equity_rank = db.Column(db.Integer)
    profit_margin_rank = db.Column(db.Integer)
    dividend_yield_rank = db.Column(db.Integer)

    # Sector size for this run (stocks with a financial_data row).
    # Ranks are 1..peer_count but a metric's rank may be None when the
    # stock lacks a valid value for that specific ratio.
    peer_count = db.Column(db.Integer)

    def __repr__(self):
        return f'<Comparison Stock:{self.stock_id} PeerCount:{self.peer_count}>'
