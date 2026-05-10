# api/__init__.py — Blueprint registry
#
# All Flask blueprints are imported here and registered onto the app instance
# inside register_blueprints(). Each blueprint handles one group of related
# endpoints, all mounted under the /api prefix.
#
# URL map:
#   /api/stocks/           → stocks.py    (list, detail, create stocks)
#   /api/sectors/          → sectors.py   (sector metadata + weights)
#   /api/valuations/       → valuations.py (DCF/P/E/P/B fair value per stock)
#   /api/comparisons/      → comparisons.py (7-ratio peer comparison table)
#   /api/pdf/              → pdf.py        (upload PDF → extract → save)

from .stocks      import stocks_bp
from .sectors     import sectors_bp
from .valuations  import valuations_bp
from .comparisons import comparisons_bp
from .pdf         import pdf_bp


def register_blueprints(app):
    """Attach all API blueprints to the Flask application.

    Called once from create_app() in app/__init__.py during startup.
    Adding a new blueprint: import it above and add one line here.
    """
    app.register_blueprint(stocks_bp,      url_prefix='/api/stocks')
    app.register_blueprint(sectors_bp,     url_prefix='/api/sectors')
    app.register_blueprint(valuations_bp,  url_prefix='/api/valuations')
    app.register_blueprint(comparisons_bp, url_prefix='/api/comparisons')
    app.register_blueprint(pdf_bp,         url_prefix='/api/pdf')
