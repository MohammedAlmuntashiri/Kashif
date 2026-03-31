# Import all models here so Alembic (migration tool) can detect them
# Without these imports, "flask db migrate" won't know the tables exist
from .sector import Sector
from .stock import Stock
from .financial_data import FinancialData
from .valuation import Valuation
