import pandas as pd
import pytest
from model.train import engineer_features

def test_engineer_features_basic():
    """Test standard case for feature engineering."""
    df = pd.DataFrame([
        {"district": "Colombo", "subcategory": "House", "bedrooms": 3, "bathrooms": 2, "land_size_perches": 10},
        {"district": "Kandy",   "subcategory": "Apartment", "bedrooms": 2, "bathrooms": 1, "land_size_perches": 5}
    ])
    
    # Run engineering
    X, _ = engineer_features(df)
    
    # Assert features are present
    assert "district_ord" in X.columns
    assert "is_apartment" in X.columns
    assert "total_rooms" in X.columns
    
    # Assert values
    assert X.iloc[0]["is_apartment"] == 0
    assert X.iloc[1]["is_apartment"] == 1
    assert X.iloc[0]["total_rooms"] == 5

def test_engineer_features_missing():
    """Test robustness with missing values."""
    df = pd.DataFrame([
        {"district": "Colombo", "subcategory": None, "bedrooms": "NaN", "bathrooms": None, "land_size_perches": 10}
    ])
    
    X, _ = engineer_features(df)
    
    # Default filling: bedrooms->3, bathrooms->2
    assert X.iloc[0]["total_rooms"] == 5
    assert X.iloc[0]["is_apartment"] == 0
