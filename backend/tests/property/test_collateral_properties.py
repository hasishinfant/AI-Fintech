"""Property-based tests for Collateral analysis in Five Cs framework.

Feature: intelli-credit
Properties tested:
- Property 21: LTV Calculation Formula
- Property 22: LTV Threshold Flagging
- Property 23: Aggregate LTV Calculation
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime
from app.services.credit_engine import FiveCsAnalyzer
from app.models.financial import Asset


# Feature: intelli-credit, Property 21: LTV Calculation Formula
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    collateral_value=st.floats(min_value=0.01, max_value=1e9),
)
def test_ltv_calculation_formula(loan_amount, collateral_value):
    """For any collateral information with loan amount and collateral value,
    the calculated LTV should equal loan amount divided by collateral value.
    
    **Validates: Requirements 8.1**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create a single collateral asset
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Commercial property",
            value=collateral_value,
            valuation_date=datetime.now(),
        )
    ]
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Calculate expected LTV
    expected_ltv = loan_amount / collateral_value
    
    # The calculated LTV should match the formula
    assert abs(result.ltv - expected_ltv) < 0.001, \
        f"Expected LTV={expected_ltv}, got {result.ltv}"


# Feature: intelli-credit, Property 22: LTV Threshold Flagging
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    collateral_value=st.floats(min_value=0.01, max_value=1e9),
)
def test_ltv_threshold_flagging(loan_amount, collateral_value):
    """For any loan application where LTV exceeds 0.75, the system should
    flag the application as having insufficient collateral coverage.
    
    **Validates: Requirements 8.2**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create a single collateral asset
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Commercial property",
            value=collateral_value,
            valuation_date=datetime.now(),
        )
    ]
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Calculate LTV
    ltv = loan_amount / collateral_value
    
    # Check threshold flagging
    if ltv > 0.75:
        # Should be flagged with lower score
        assert result.score < 70, \
            f"LTV={ltv} > 0.75 should result in score < 70, got {result.score}"
    elif ltv <= 0.75:
        # Should not be critically flagged
        assert result.score >= 70, \
            f"LTV={ltv} <= 0.75 should result in score >= 70, got {result.score}"


# Feature: intelli-credit, Property 23: Aggregate LTV Calculation
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    num_assets=st.integers(min_value=1, max_value=5),
    asset_value_base=st.floats(min_value=100000.0, max_value=1e8),
)
def test_aggregate_ltv_calculation(loan_amount, num_assets, asset_value_base):
    """For any loan application with multiple collateral assets, the system
    should calculate an aggregate LTV across all assets.
    
    **Validates: Requirements 8.3**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create multiple collateral assets
    collateral_assets = []
    total_collateral_value = 0.0
    
    for i in range(num_assets):
        # Vary asset values to create realistic scenario
        asset_value = asset_value_base * (1.0 + (i * 0.1))
        collateral_assets.append(
            Asset(
                asset_type=f"Asset Type {i % 3}",
                description=f"Asset {i}",
                value=asset_value,
                valuation_date=datetime.now(),
            )
        )
        total_collateral_value += asset_value
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Calculate expected aggregate LTV
    expected_ltv = loan_amount / total_collateral_value
    
    # The calculated LTV should match the aggregate formula
    assert abs(result.ltv - expected_ltv) < 0.001, \
        f"Expected aggregate LTV={expected_ltv}, got {result.ltv}"


# Feature: intelli-credit, Property 13: Five Cs Score Validity (Collateral component)
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    collateral_value=st.floats(min_value=0.01, max_value=1e9),
)
def test_collateral_score_validity_range(loan_amount, collateral_value):
    """For any completed Collateral assessment, the score should be within
    the range 0 to 100 inclusive.
    
    **Validates: Requirements 8.4**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create a single collateral asset
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Commercial property",
            value=collateral_value,
            valuation_date=datetime.now(),
        )
    ]
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Score should be within 0-100
    assert 0 <= result.score <= 100, \
        f"Collateral score should be 0-100, got {result.score}"


# Feature: intelli-credit, Property 8.5: Collateral Composition Documentation
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    num_assets=st.integers(min_value=1, max_value=3),
    asset_value_base=st.floats(min_value=100000.0, max_value=1e8),
)
def test_collateral_composition_documentation(loan_amount, num_assets, asset_value_base):
    """For any collateral evaluation, the system should document asset types,
    values, and valuation dates.
    
    **Validates: Requirements 8.5**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create multiple collateral assets
    collateral_assets = []
    for i in range(num_assets):
        asset_value = asset_value_base * (1.0 + (i * 0.1))
        collateral_assets.append(
            Asset(
                asset_type=f"Asset Type {i}",
                description=f"Asset {i}",
                value=asset_value,
                valuation_date=datetime.now(),
            )
        )
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Should have documented the collateral type
    assert result.collateral_type is not None, \
        "Collateral type should be documented"
    
    # Should have documented the valuation date
    assert result.valuation_date is not None, \
        "Valuation date should be documented"
    
    # Should have documented the LTV
    assert result.ltv is not None, \
        "LTV should be documented"


# Feature: intelli-credit, Property 21: LTV Calculation with Multiple Assets
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    asset1_value=st.floats(min_value=100000.0, max_value=1e8),
    asset2_value=st.floats(min_value=100000.0, max_value=1e8),
    asset3_value=st.floats(min_value=100000.0, max_value=1e8),
)
def test_ltv_calculation_multiple_assets(loan_amount, asset1_value, asset2_value, asset3_value):
    """For any collateral with multiple assets, the LTV calculation should
    correctly aggregate all asset values.
    
    **Validates: Requirements 8.1, 8.3**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create multiple collateral assets
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Property 1",
            value=asset1_value,
            valuation_date=datetime.now(),
        ),
        Asset(
            asset_type="Machinery",
            description="Equipment",
            value=asset2_value,
            valuation_date=datetime.now(),
        ),
        Asset(
            asset_type="Inventory",
            description="Raw materials",
            value=asset3_value,
            valuation_date=datetime.now(),
        ),
    ]
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Calculate expected aggregate LTV
    total_collateral = asset1_value + asset2_value + asset3_value
    expected_ltv = loan_amount / total_collateral
    
    # The calculated LTV should match the aggregate formula
    assert abs(result.ltv - expected_ltv) < 0.001, \
        f"Expected LTV={expected_ltv}, got {result.ltv}"


# Feature: intelli-credit, Property 22: LTV Threshold at Boundary
@settings(max_examples=100)
@given(
    collateral_value=st.floats(min_value=100000.0, max_value=1e8),
)
def test_ltv_threshold_boundary_cases(collateral_value):
    """For loan applications at the LTV threshold of 0.75, the system should
    correctly classify the risk level.
    
    **Validates: Requirements 8.2**
    """
    analyzer = FiveCsAnalyzer()
    
    # Test at threshold (LTV = 0.75)
    loan_at_threshold = collateral_value * 0.75
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Property",
            value=collateral_value,
            valuation_date=datetime.now(),
        )
    ]
    
    result_at_threshold = analyzer.analyze_collateral(collateral_assets, loan_at_threshold)
    
    # At threshold, score should be around 70
    assert 65 <= result_at_threshold.score <= 75, \
        f"At LTV=0.75, score should be around 70, got {result_at_threshold.score}"
    
    # Test just below threshold (LTV = 0.74)
    loan_below_threshold = collateral_value * 0.74
    result_below = analyzer.analyze_collateral(collateral_assets, loan_below_threshold)
    
    # Below threshold, score should be higher
    assert result_below.score >= 70, \
        f"Below LTV=0.75, score should be >= 70, got {result_below.score}"
    
    # Test just above threshold (LTV = 0.76)
    loan_above_threshold = collateral_value * 0.76
    result_above = analyzer.analyze_collateral(collateral_assets, loan_above_threshold)
    
    # Above threshold, score should be lower
    assert result_above.score < 70, \
        f"Above LTV=0.75, score should be < 70, got {result_above.score}"


# Feature: intelli-credit, Property 23: Aggregate LTV with Varying Asset Types
@settings(max_examples=100)
@given(
    loan_amount=st.floats(min_value=0.01, max_value=1e9),
    real_estate_value=st.floats(min_value=100000.0, max_value=1e8),
    machinery_value=st.floats(min_value=50000.0, max_value=5e7),
    inventory_value=st.floats(min_value=10000.0, max_value=1e7),
)
def test_aggregate_ltv_mixed_asset_types(loan_amount, real_estate_value, machinery_value, inventory_value):
    """For collateral with mixed asset types, the aggregate LTV should
    correctly sum all asset values regardless of type.
    
    **Validates: Requirements 8.3**
    """
    analyzer = FiveCsAnalyzer()
    
    # Create collateral with mixed asset types
    collateral_assets = [
        Asset(
            asset_type="Real Estate",
            description="Commercial property",
            value=real_estate_value,
            valuation_date=datetime.now(),
        ),
        Asset(
            asset_type="Machinery",
            description="Industrial equipment",
            value=machinery_value,
            valuation_date=datetime.now(),
        ),
        Asset(
            asset_type="Inventory",
            description="Raw materials",
            value=inventory_value,
            valuation_date=datetime.now(),
        ),
    ]
    
    # Analyze collateral
    result = analyzer.analyze_collateral(collateral_assets, loan_amount)
    
    # Calculate expected aggregate LTV
    total_collateral = real_estate_value + machinery_value + inventory_value
    expected_ltv = loan_amount / total_collateral
    
    # The calculated LTV should match the aggregate formula
    assert abs(result.ltv - expected_ltv) < 0.001, \
        f"Expected LTV={expected_ltv}, got {result.ltv}"
    
    # Primary collateral type should be the most valuable
    if real_estate_value >= machinery_value and real_estate_value >= inventory_value:
        assert result.collateral_type == "Real Estate"
    elif machinery_value >= real_estate_value and machinery_value >= inventory_value:
        assert result.collateral_type == "Machinery"
    else:
        assert result.collateral_type == "Inventory"
