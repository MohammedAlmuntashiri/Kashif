from app.extensions import db


class Sector(db.Model):
    __tablename__ = 'sectors'

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)     # Arabic name — "البنوك"
    name_en = db.Column(db.String(100), nullable=False)     # English name — "Banks"

    # How much to trust each valuation model for this sector (must sum to 1.0)
    # Example for Banks: dcf=0.20, pe=0.40, pb=0.40 (banks are asset-heavy, so P/B matters more)
    dcf_weight = db.Column(db.Float, nullable=False)
    pe_weight = db.Column(db.Float, nullable=False)
    pb_weight = db.Column(db.Float, nullable=False)

    # Relationship: one sector has many stocks
    # backref='sector' means each Stock object can access its sector via stock.sector
    stocks = db.relationship('Stock', backref='sector', lazy=True)

    def __repr__(self):
        return f'<Sector {self.name_en}>'
