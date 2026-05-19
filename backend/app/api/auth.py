# auth.py — Authentication endpoints.
#
# URL prefix (registered in api/__init__.py): /api/auth
#
# Endpoints:
#   POST /api/auth/signup  — create a new account, return JWT + user
#   POST /api/auth/signin  — authenticate existing account, return JWT + user
#   GET  /api/auth/me      — return the current user from a Bearer token
#
# Password storage: bcrypt with cost factor 12 (the bcrypt default).
# Session: stateless JWT (HS256) signed with app.config['SECRET_KEY'].
# Token lifetime: 7 days. Frontend stores the token in localStorage and
# attaches it to each request via the Authorization header.

import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, jsonify, request, current_app, g

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

TOKEN_LIFETIME = timedelta(days=7)
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _hash_password(plaintext: str) -> str:
    return bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _check_password(plaintext: str, stored_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plaintext.encode('utf-8'), stored_hash.encode('utf-8'))
    except (ValueError, AttributeError):
        return False


def _issue_token(user: User) -> str:
    payload = {
        'sub':   str(user.id),
        'email': user.email,
        'iat':   datetime.now(tz=timezone.utc),
        'exp':   datetime.now(tz=timezone.utc) + TOKEN_LIFETIME,
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def _decode_token(token: str):
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])


def _err(code: str, status: int = 400):
    """Uniform error shape. The `code` matches the legacy frontend error
    strings (NO_ACCOUNT, WRONG_PASSWORD, etc.) so existing i18n keeps working.
    """
    return jsonify({'error': code}), status


# Decorator: protect a route with a valid JWT. The user is stashed on
# flask.g.current_user for the handler to read.
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return _err('NO_TOKEN', 401)
        token = header[len('Bearer '):].strip()
        try:
            payload = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return _err('TOKEN_EXPIRED', 401)
        except jwt.InvalidTokenError:
            return _err('INVALID_TOKEN', 401)
        user = User.query.get(int(payload['sub']))
        if not user:
            return _err('NO_ACCOUNT', 401)
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


# ─── Routes ──────────────────────────────────────────────────────────────────

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    name     = (data.get('name')     or '').strip()
    email    = (data.get('email')    or '').strip().lower()
    password = data.get('password')  or ''

    if not name:                      return _err('NAME_REQUIRED')
    if not EMAIL_RE.match(email):     return _err('INVALID_EMAIL')
    if len(password) < 6:             return _err('PASSWORD_TOO_SHORT')

    if User.query.filter_by(email=email).first():
        return _err('EMAIL_TAKEN', 409)

    user = User(email=email, name=name, password_hash=_hash_password(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'token': _issue_token(user),
        'user':  user.to_public_dict(),
    }), 201


@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json(silent=True) or {}
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user:                                  return _err('NO_ACCOUNT', 401)
    if not _check_password(password, user.password_hash):
        return _err('WRONG_PASSWORD', 401)

    return jsonify({
        'token': _issue_token(user),
        'user':  user.to_public_dict(),
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def me():
    return jsonify({'user': g.current_user.to_public_dict()})
