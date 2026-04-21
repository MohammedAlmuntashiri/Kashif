# dcf_service.py — Discounted Cash Flow valuation (simple + advanced)
#
# Two methods:
#   simple_dcf()   — Gordon Growth Model, uses latest FCF only
#   advanced_dcf() — Multi-stage projection from historical FCF growth
#
# Both return fair value per share in SAR, or None if inputs are insufficient.

# Default assumptions for Saudi market
from app.services.wacc_service import FALLBACK_WACC
DEFAULT_WACC = FALLBACK_WACC    # Used only when no calculated WACC is provided
DEFAULT_GROWTH = 0.025          # Long-term perpetual growth rate (2.5%)
PROJECTION_YEARS = 5            # Number of years to project FCF forward
MAX_GROWTH_RATE = 0.25          # Cap historical growth at 25%
MIN_GROWTH_RATE = -0.05         # Floor historical growth at -5%


def simple_dcf(fcf, shares_outstanding, growth_rate=DEFAULT_GROWTH, wacc=DEFAULT_WACC):
    """Gordon Growth Model: fair_value = FCF × (1 + g) / (WACC - g) / shares

    Args:
        fcf: Most recent annual free cash flow (SAR)
        shares_outstanding: Total shares issued
        growth_rate: Perpetual growth rate (default 2.5%)
        wacc: Discount rate (default 8.6%)

    Returns:
        Fair value per share (SAR), or None if inputs are invalid.
    """
    if fcf is None or shares_outstanding is None:
        return None
    if shares_outstanding <= 0 or fcf <= 0:
        return None
    if wacc <= growth_rate:
        return None

    intrinsic_value = fcf * (1 + growth_rate) / (wacc - growth_rate)
    return intrinsic_value / shares_outstanding


def advanced_dcf(fcf_history, shares_outstanding, wacc=DEFAULT_WACC, terminal_growth=DEFAULT_GROWTH):
    """Multi-stage DCF: project FCF 5 years using historical growth, then add terminal value.

    Steps:
        1. Calculate growth rate (CAGR) from historical FCF (oldest → newest)
        2. Project FCF for 5 future years
        3. Discount each projected year to present value
        4. Add discounted terminal value (perpetuity beyond year 5)
        5. Divide total by shares outstanding

    Args:
        fcf_history: List of annual FCF values, oldest first. Needs at least 2 values.
        shares_outstanding: Total shares issued
        wacc: Discount rate (default 8.6%)
        terminal_growth: Long-term growth for terminal value (default 2.5%)

    Returns:
        Fair value per share (SAR), or None if inputs are insufficient.
    """
    if shares_outstanding is None or shares_outstanding <= 0:
        return None
    if fcf_history is None or len(fcf_history) < 2:
        return None
    if wacc <= terminal_growth:
        return None

    # Filter out None values
    valid_fcf = [f for f in fcf_history if f is not None]
    if len(valid_fcf) < 2:
        return None

    # Need positive FCF at start and end for meaningful CAGR
    fcf_oldest = valid_fcf[0]
    fcf_newest = valid_fcf[-1]
    if fcf_oldest <= 0 or fcf_newest <= 0:
        return None

    # Step 1: Calculate historical growth rate (CAGR)
    n_years = len(valid_fcf) - 1
    growth_rate = (fcf_newest / fcf_oldest) ** (1 / n_years) - 1

    # Clamp growth to reasonable bounds
    growth_rate = max(MIN_GROWTH_RATE, min(MAX_GROWTH_RATE, growth_rate))

    # Step 2 & 3: Project FCF and discount to present value
    projected_fcf = fcf_newest
    total_pv = 0.0

    for year in range(1, PROJECTION_YEARS + 1):
        projected_fcf = projected_fcf * (1 + growth_rate)
        discount_factor = (1 + wacc) ** year
        total_pv += projected_fcf / discount_factor

    # Step 4: Terminal value (perpetuity starting after year 5)
    terminal_value = projected_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** PROJECTION_YEARS)
    total_pv += pv_terminal

    # Step 5: Fair value per share
    return total_pv / shares_outstanding
