from datetime import datetime

from app.extensions import db


class User(db.Model):
    """Application user — created via /api/auth/signup, authenticated via JWT.

    Passwords are hashed with bcrypt before being stored (set_password helper).
    Never store the plaintext password and never return password_hash from any
    API response — see to_public_dict() for the safe serializer.
    """

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name          = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_public_dict(self):
        return {
            'id':         self.id,
            'email':      self.email,
            'name':       self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.email}>'
