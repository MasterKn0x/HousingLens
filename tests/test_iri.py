import pytest
from model.iri_calculator import calculate_iri

def test_iri_bounds():
    """Ensure IRI is always between 1 and 10."""
    assert calculate_iri(0, 1000000) == 1
    assert calculate_iri(1000000**2, 1000000) == 10
    assert calculate_iri(-1, 1000000) == 1
    assert calculate_iri(0, -10000) == 10

def test_iri_deterministic():
    """Ensure predictable outcomes for known inputs."""
    # predicted_price = 1M, std_dev = 300k, cv = 0.3
    # MAX_CV = 0.6
    # raw_score = 1 + (0.3 / 0.6) * 9 = 1 + 0.5 * 9 = 5.5 -> rounds to 6
    assert calculate_iri(300000**2, 1000000) == 6

def test_iri_edge_cases():
    """Test zero and negative price handling."""
    assert calculate_iri(100, 0) == 10
    assert calculate_iri(100, -5000) == 10
