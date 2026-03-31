from app.extensions import db


class FinancialData(db.Model):
    __tablename__ = 'financial_data'

    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(20), nullable=False)  # Reporting period — "2024-Q4" or "2024-annual"

    # Foreign key: which stock this data belongs to
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)

    # The 10 key financial values extracted from company reports (all in SAR)

    # Revenue / الإيرادات — Total money the company earned from sales
    revenue = db.Column(db.Float)

    # Net Income / صافي الدخل — Profit left after all expenses and taxes
    net_income = db.Column(db.Float)

    # Earnings Per Share / ربحية السهم — Net income divided by number of shares
    eps = db.Column(db.Float)

    # Total Assets / إجمالي الأصول — Everything the company owns (cash, property, equipment)
    total_assets = db.Column(db.Float)

    # Total Borrowings / إجمالي القروض — Loans and debt obligations only (not all liabilities)
    total_borrowings = db.Column(db.Float)

    # Shareholders' Equity / حقوق المساهمين — Assets minus liabilities (what belongs to shareholders)
    shareholders_equity = db.Column(db.Float)

    # Cash and Equivalents / النقد وما يعادله — Cash on hand and short-term liquid assets
    cash_and_equivalents = db.Column(db.Float)

    # Free Cash Flow / التدفق النقدي الحر — Cash left after spending on equipment and maintenance
    free_cash_flow = db.Column(db.Float)

    # Dividends Per Share / توزيعات الأرباح لكل سهم — Cash paid to each shareholder per share
    dividends_per_share = db.Column(db.Float)

    # Shares Outstanding / عدد الأسهم المصدرة — Total number of shares issued by the company
    shares_outstanding = db.Column(db.Float)

    def __repr__(self):
        return f'<FinancialData Stock:{self.stock_id} Period:{self.period}>'
