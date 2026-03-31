import os
from flask import Flask
from .config import config
from .extensions import db, migrate


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    from .api import register_blueprints
    register_blueprints(app)

    return app
