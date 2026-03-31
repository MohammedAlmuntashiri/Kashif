from datetime import datetime
from app.extensions import db


class Valuation(db.Model):
    __tablename__ = 'valuations'

    id = db.Column(db.Integer, primary_key=True)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)  # When this valuation was computed

    # Foreign key: which stock was valued
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)

    # Fair value from each of the 3 models (in SAR)
    dcf_value = db.Column(db.Float)   # Discounted Cash Flow result
    pe_value = db.Column(db.Float)    # Price-to-Earnings result
    pb_value = db.Column(db.Float)    # Price-to-Book result

    # Blended fair value = (dcf × dcf_weight) + (pe × pe_weight) + (pb × pb_weight)
    fair_value = db.Column(db.Float)

    # Market price at the time of calculation (snapshot, not live)
    market_price = db.Column(db.Float)

    # Final verdict: "undervalued", "fair", or "overvalued"
    # undervalued = market_price < fair_value (green)
    # fair        = market_price ≈ fair_value (yellow)
    # overvalued  = market_price > fair_value (red)
    status = db.Column(db.String(20))

    def __repr__(self):
        return f'<Valuation Stock:{self.stock_id} Status:{self.status}>'
