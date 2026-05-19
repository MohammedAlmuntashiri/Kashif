"""
notes.py — Per-user freeform note attached to one stock.

URL prefix: /api/notes

Endpoints (all require Authorization: Bearer <jwt>):
    GET    /<ticker>     fetch this user's note for the stock (content="" if none)
    PUT    /<ticker>     create or overwrite the note (body: {"content": "..."})
    DELETE /<ticker>     delete the note (idempotent)
"""
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from app.api.auth import token_required
from app.extensions import db
from app.models.stock import Stock
from app.models.stock_note import StockNote


notes_bp = Blueprint('notes', __name__)


# Defensive cap so a runaway client can't push enormous blobs into the DB.
MAX_NOTE_CHARS = 8000


def _serialize(note, stock):
    # `stock` is passed in explicitly so we don't depend on an ORM
    # relationship that wasn't declared on the model.
    return {
        'symbol':     stock.symbol,
        'content':    note.content,
        'updated_at': note.updated_at.isoformat() if note.updated_at else None,
    }


def _resolve_stock(ticker):
    stock = Stock.query.filter_by(symbol=ticker.strip()).first()
    if stock is None:
        return None, (jsonify({'error': f'Stock {ticker} not found'}), 404)
    return stock, None


@notes_bp.route('/<ticker>', methods=['GET'])
@token_required
def get_note(ticker):
    stock, err = _resolve_stock(ticker)
    if err:
        return err
    note = StockNote.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).first()
    if note is None:
        # Return an empty placeholder so the frontend doesn't have to special-case 404.
        return jsonify({'symbol': stock.symbol, 'content': '', 'updated_at': None})
    return jsonify(_serialize(note, stock))


@notes_bp.route('/<ticker>', methods=['PUT'])
@token_required
def upsert_note(ticker):
    stock, err = _resolve_stock(ticker)
    if err:
        return err

    payload = request.get_json(silent=True) or {}
    content = (payload.get('content') or '').strip()
    if len(content) > MAX_NOTE_CHARS:
        return jsonify({'error': f'note too long (max {MAX_NOTE_CHARS} chars)'}), 400

    # Empty content → delete the row entirely (frontend never wants a blank note).
    if not content:
        StockNote.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).delete()
        db.session.commit()
        return jsonify({'symbol': stock.symbol, 'content': '', 'updated_at': None})

    note = StockNote.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).first()
    if note is None:
        note = StockNote(user_id=g.current_user.id, stock_id=stock.id, content=content)
        db.session.add(note)
    else:
        note.content = content
        note.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize(note, stock))


@notes_bp.route('/<ticker>', methods=['DELETE'])
@token_required
def delete_note(ticker):
    stock, err = _resolve_stock(ticker)
    if err:
        return err
    StockNote.query.filter_by(user_id=g.current_user.id, stock_id=stock.id).delete()
    db.session.commit()
    return jsonify({'symbol': stock.symbol, 'content': '', 'updated_at': None})
