from app.extensions import db


class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)  # Tadawul ticker — "1120"
    name_ar = db.Column(db.String(200), nullable=False)              # "مصرف الراجحي"
    name_en = db.Column(db.String(200), nullable=False)              # "Al Rajhi Bank"
    market_price = db.Column(db.Float, nullable=True)                # Current price in SAR

    # Foreign key: links this stock to its sector
    sector_id = db.Column(db.Integer, db.ForeignKey('sectors.id'), nullable=False)

    # Relationships: one stock has many financial data rows and many valuations
    financial_data = db.relationship('FinancialData', backref='stock', lazy=True)
    valuations = db.relationship('Valuation', backref='stock', lazy=True)

    def __repr__(self):
        return f'<Stock {self.symbol} - {self.name_en}>'
