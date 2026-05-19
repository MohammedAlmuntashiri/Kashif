"""
Unit tests for app.api.pdf._values_match.

_values_match is the boolean check behind every "Match" ✓/✗ in the upload
preview table, AND the safety gate that decides whether
?auto_commit_if_match=true is allowed to write extracted values to the DB.
Tightening or loosening this function changes both the user-visible accuracy
and the risk profile of the writeback path, so it's worth pinning down.

Contract (from the source):
    - Both None      → match
    - One None       → no match
    - Both numbers   → match iff |db - extracted| / max(|db|, 1) <= tolerance
    - Tolerance default 1% (0.01)
"""
import pytest

from app.api.pdf import _values_match


# ── None handling ────────────────────────────────────────────────────

def test_both_none_match():
    """Neither side has data → treated as a match (no disagreement)."""
    assert _values_match(None, None) is True


@pytest.mark.parametrize("db, extracted", [
    (None, 100.0),
    (100.0, None),
    (None, 0),
    (0, None),
])
def test_one_side_none_does_not_match(db, extracted):
    """One side has data the other doesn't → mismatch."""
    assert _values_match(db, extracted) is False


# ── Tolerance behavior on equal-ish numbers ──────────────────────────

def test_exact_equal_matches():
    assert _values_match(1_000_000_000.0, 1_000_000_000.0) is True


def test_within_default_one_percent_matches():
    # 1,000,000,000 vs 1,005,000,000 → 0.5% off, within 1%
    assert _values_match(1_000_000_000.0, 1_005_000_000.0) is True


def test_at_default_tolerance_boundary_matches():
    # Exactly 1% off — the comparison uses <=, so this should match.
    assert _values_match(1_000.0, 1_010.0) is True


def test_just_outside_default_tolerance_does_not_match():
    # 1.01% off — fails the 1% gate.
    assert _values_match(1_000.0, 1_010.01) is False


def test_custom_tolerance_widens_the_gate():
    # 5% off, but caller allows 10% — should match.
    assert _values_match(100.0, 105.0, tolerance=0.10) is True


def test_custom_tolerance_tightens_the_gate():
    # Within 1% but caller demands 0.1% — should NOT match.
    assert _values_match(1_000.0, 1_005.0, tolerance=0.001) is False


# ── Zero-denominator protection ──────────────────────────────────────

def test_zero_db_with_tiny_extracted_matches():
    # max(|db|, 1) in the denominator prevents a div-by-zero blow-up
    # and treats sub-1 extracted differences against db=0 as matches.
    assert _values_match(0, 0.005) is True


def test_zero_db_with_large_extracted_does_not_match():
    assert _values_match(0, 100.0) is False


def test_tiny_db_uses_one_in_denominator():
    # db=0.5, extracted=1.0 → diff=0.5. denom = max(0.5, 1) = 1 → 50% off,
    # which would normally fail, but normalized to 1 it's still 50% off.
    assert _values_match(0.5, 1.0) is False


# ── Sign and magnitude ──────────────────────────────────────────────

def test_negative_values_within_tolerance_match():
    # Loss-making companies have negative FCF / net_income — the function
    # should still compare correctly via |db|.
    assert _values_match(-1_000.0, -1_005.0) is True


def test_negative_vs_positive_does_not_match():
    # Sign flip on the same magnitude → 200% off → not a match.
    assert _values_match(-100.0, 100.0) is False
