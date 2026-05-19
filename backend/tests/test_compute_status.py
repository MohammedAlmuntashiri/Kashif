"""
Unit tests for app.services.valuation_engine.compute_status.

compute_status decides the "undervalued / fair / overvalued" badge that
appears on every stock card and stock detail page. It is a pure function
(no DB, no I/O), which makes it a great candidate for a fast unit test.

Contract (from the source):
    - Returns "undervalued" when fair_value > market_price * 1.10
    - Returns "overvalued"  when fair_value < market_price * 0.90
    - Returns "fair"        otherwise
    - Returns None          when either input is None or non-positive
"""
import pytest

from app.services.valuation_engine import compute_status


# ── Happy path: clearly under-, fair-, and over-valued ──────────────

@pytest.mark.parametrize("market, fair", [
    (100.0, 150.0),   # +50%
    (100.0, 111.0),   # +11% — just past the threshold
    (1.0,   2.0),     # 2x
    (27.84, 35.21),   # Savola-like real-world ratio
])
def test_clearly_undervalued(market, fair):
    assert compute_status(market, fair) == "undervalued"


@pytest.mark.parametrize("market, fair", [
    (100.0, 50.0),    # -50%
    (100.0, 89.0),    # -11% — just past the threshold
    (216.70, 78.01),  # Habib-like ratio
])
def test_clearly_overvalued(market, fair):
    assert compute_status(market, fair) == "overvalued"


@pytest.mark.parametrize("market, fair", [
    (100.0, 100.0),   # exact match
    (100.0, 110.0),   # +10% — at upper boundary, NOT past it
    (100.0, 90.0),    # -10% — at lower boundary, NOT past it
    (100.0, 105.0),   # within band
    (100.0, 95.0),    # within band
])
def test_within_fair_band(market, fair):
    assert compute_status(market, fair) == "fair"


# ── Boundary precision: 10% threshold is "strictly greater than" ────

def test_just_above_undervalued_threshold():
    # 110.001 / 100 = 1.10001 > 1.10  → undervalued
    assert compute_status(100.0, 110.001) == "undervalued"


def test_just_below_overvalued_threshold():
    # 89.999 / 100 = 0.89999 < 0.90  → overvalued
    assert compute_status(100.0, 89.999) == "overvalued"


# ── Invalid inputs: must return None, never raise ────────────────────

@pytest.mark.parametrize("market, fair", [
    (None, 100.0),    # market price missing
    (100.0, None),    # fair value missing
    (None, None),     # both missing
    (0,    100.0),    # zero market price
    (100.0, 0),       # zero fair value
    (-10.0, 100.0),   # negative market price
    (100.0, -10.0),   # negative fair value
])
def test_invalid_inputs_return_none(market, fair):
    assert compute_status(market, fair) is None


# ── Real-world spot checks from the actual DB ────────────────────────

def test_aramco_2025_overvalued_example():
    # From the actual DB at 2026-05-19: market=27.84, fair=24.31 → -12.7%
    assert compute_status(27.84, 24.31) == "overvalued"


def test_aramco_2024_fair_example():
    # From the actual DB: market=27.84, fair=26.13 → -6.1% (within band)
    assert compute_status(27.84, 26.13) == "fair"
