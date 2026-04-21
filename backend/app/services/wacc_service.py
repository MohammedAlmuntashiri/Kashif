# wacc_service.py — Weighted Average Cost of Capital for Saudi market
#
# WACC = (E/V × Re) + (D/V × Rd × (1 - T))
#
# Where:
#   E  = shareholders_equity
#   D  = total_borrowings
#   V  = E + D (total capital)
#   Re = cost of equity (10% — Saudi market expected return)
#   Rd = cost of debt (3% — average Saudi corporate borrowing rate)
#   T  = zakat rate (2.5% — Saudi religious tax, replaces corporate tax for most firms)
#
# If no debt (D=0): WACC = Re (pure equity funded)
# If data missing: fallback to 8.6%

DEFAULT_RE = 0.10              # Cost of equity (10%)
DEFAULT_RD = 0.03              # Cost of debt (3%)
DEFAULT_TAX = 0.025            # Zakat rate (2.5%)
FALLBACK_WACC = 0.086          # Default when data is missing


def calculate_wacc(equity, debt, re=DEFAULT_RE, rd=DEFAULT_RD, tax_rate=DEFAULT_TAX):
    """Calculate WACC from equity and debt.

    Args:
        equity: Shareholders' equity (SAR)
        debt: Total borrowings (SAR)
        re: Cost of equity (default 10%)
        rd: Cost of debt (default 3%)
        tax_rate: Zakat rate (default 2.5%)

    Returns:
        WACC as a decimal (e.g. 0.086), or FALLBACK_WACC if inputs are missing.
    """
    if equity is None or equity <= 0:
        return FALLBACK_WACC

    # No debt → pure equity
    if debt is None or debt <= 0:
        return re

    v = equity + debt
    wacc = (equity / v * re) + (debt / v * rd * (1 - tax_rate))
    return wacc
