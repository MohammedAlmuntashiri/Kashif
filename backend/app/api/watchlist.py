"""
watchlist.py — Per-user stock watchlist.

URL prefix: /api/watchlist

Endpoints (all require Authorization: Bearer <jwt>):
    GET    /             list the current user's watchlisted stocks
    POST   /<ticker>     add a stock to the watchlist (idempotent)
    DELETE /<ticker>     remove a stock from the watchlist (idempotent)
"""
from flask import Blueprint, g, jsonify

from app.api.auth import token_required
from app.extensions import db
from app.models.stock import Stock
from app.models.watchlist import Watchlist
from app.models.financial_data import FinancialData


watchlist_bp = Blueprint('watchlist', __name__)


def _stock_summary(stock):
    """Same shape as GET /api/stocks/ rows, so the frontend WatchlistPage
    can reuse StockCard without translation."""
    latest_fd = (
        FinancialData.query
        .filter_by(stock_id=stock.id)
        .order_by(FinancialData.period.desc())
        .first()
    )
    return {
        'symbol':        stock.symbol,
        'name_en':       stock.name_en,
        'name_ar':       stock.name_ar,
        'sector':        stock.sector.name_en,
        'market_price':  stock.market_price,
        'latest_period': latest_fd.period      if latest_fd else None,
        'revenue':       latest_fd.revenue     if latest_fd else None,
        'net_income':    latest_fd.net_income  if latest_fd else None,
        'eps':           latest_fd.eps         if latest_fd else None,
    }


@watchlist_bp.route('/', methods=['GET'])
@token_required
def list_watchlist():
    rows = (
        Watchlist.query
        .filter_by(user_id=g.current_user.id)
        .order_by(Watchlist.created_at.desc())
        .all()
    )
    # Bulk-fetch the stocks in one query to avoid an N+1 walk.
    stock_ids = [r.stock_id for r in rows]
    stocks = {s.id: s for s in Stock.query.filter(Stock.id.in_(stock_ids)).all()} if stock_ids else {}
    return jsonify([
        _stock_summary(stocks[r.stock_id])
        for r in rows if r.stock_id in stocks
    ])


@watchlist_bp.route('/<ticker>', methods=['POST'])
@token_required
def add_watchlist(ticker):
    stock = Stock.query.filter_by(symbol=ticker.strip()).first()
    if stock is None:
        return jsonify({'error': f'Stock {ticker} not found'}), 404
    # Idempotent: if it's already starred, just return the existing state.
    existing = Watchlist.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).first()
    if existing is None:
        db.session.add(Watchlist(user_id=g.current_user.id, stock_id=stock.id))
        db.session.commit()
    return jsonify({'symbol': stock.symbol, 'watching': True}), 201


@watchlist_bp.route('/<ticker>', methods=['DELETE'])
@token_required
def remove_watchlist(ticker):
    stock = Stock.query.filter_by(symbol=ticker.strip()).first()
    if stock is None:
        return jsonify({'error': f'Stock {ticker} not found'}), 404
    Watchlist.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).delete()
    db.session.commit()
    return jsonify({'symbol': stock.symbol, 'watching': False})
