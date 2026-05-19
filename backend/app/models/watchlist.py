from datetime import datetime

from app.extensions import db


class Watchlist(db.Model):
    """A single 'star' — one user marking one stock as worth tracking.

    Composite uniqueness on (user_id, stock_id) so each user can only star
    a given stock once. The frontend toggles by hitting POST/DELETE on
    /api/watchlist/<ticker> against the current user's token.
    """

    __tablename__ = 'watchlist'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'stock_id', name='uq_watchlist_user_stock'),
    )

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    stock_id   = db.Column(db.Integer, db.ForeignKey('stocks.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
