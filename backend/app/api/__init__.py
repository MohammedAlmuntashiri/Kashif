from .stocks import stocks_bp
from .sectors import sectors_bp
from .valuations import valuations_bp
from .comparisons import comparisons_bp


def register_blueprints(app):
    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(sectors_bp, url_prefix='/api/sectors')
    app.register_blueprint(valuations_bp, url_prefix='/api/valuations')
    app.register_blueprint(comparisons_bp, url_prefix='/api/comparisons')
