from datetime import datetime

from app.extensions import db


class StockNote(db.Model):
    """Per-user freeform note attached to one stock.

    One row per (user, stock). The handler upserts on PUT — overwrites
    the content + updated_at when the same user posts again for the same
    stock. Empty content is allowed but the frontend deletes the row
    instead of saving an empty string.
    """

    __tablename__ = 'stock_notes'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'stock_id', name='uq_stock_notes_user_stock'),
    )

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    stock_id   = db.Column(db.Integer, db.ForeignKey('stocks.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    content    = db.Column(db.Text, nullable=False, default='')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
