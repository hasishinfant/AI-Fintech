"""Property-based tests for Conditions analysis in FiveCsAnalyzer.

Feature: intelli-credit
Tests the Conditions assessment functionality with property-based testing.
"""

from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from app.services.credit_engine import FiveCsAnalyzer
from app.models.research import RBINotification, SentimentScore
from app.models.credit_assessment import ConditionsScore


# Strategy for generating valid industry data
@st.composite
def industry_data_strategy(draw):
    """Generate realistic industry data for Conditions analysis."""
    return {
        "sector": draw(st.text(min_size=1, max_size=50)),
        "growth_rate": draw(st.floats(min_value=-10.0, max_value=20.0)),
        "volatility": draw(st.floats(min_value=0.0, max_value=1.0)),
        "commodity_exposure": draw(st.booleans()),
        "commodity_volatility": draw(st.floats(min_value=0.0, max_value=1.0)),
        "commodity_types": draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
    }


@st.composite
def rbi_notification_strategy(draw):
    """Generate realistic RBI notifications."""
    severity_keywords = {
        "high": ["ban", "restrict", "tighten", "increase", "mandatory"],
        "medium": ["guideline", "advisory", "monitor", "review"],
        "low": ["information", "clarification", "note"],
    }
    
    severity = draw(st.sampled_from(["high", "medium", "low"]))
    keywords = severity_keywords[severity]
    keyword = draw(st.sampled_from(keywords))
    
    return RBINotification(
        notification_id=draw(st.text(min_size=5, max_size=20)),
        title=f"RBI {keyword.title()} Notification",
        url=f"https://rbi.org.in/notification/{draw(st.text(min_size=5, max_size=20))}",
        published_date=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=365))),
        sector=draw(st.sampled_from(["Banking", "Finance", "Insurance", "General"])),
        content=f"This is a {severity} severity notification about {keyword}",
        summary=f"{severity.title()} severity: {keyword}",
    )


@st.composite
def sentiment_score_strategy(draw):
    """Generate realistic sentiment scores."""
    overall = draw(st.floats(min_value=-1.0, max_value=1.0))
    total_articles = draw(st.integers(min_value=1, max_value=100))
    
    # Distribute articles based on sentiment
    if overall > 0.5:
        positive = draw(st.integers(min_value=int(total_articles * 0.6), max_value=total_articles))
        negative = draw(st.integers(min_value=0, max_value=int(total_articles * 0.2)))
    elif overall < -0.5:
        negative = draw(st.integers(min_value=int(total_articles * 0.6), max_value=total_articles))
        positive = draw(st.integers(min_value=0, max_value=int(total_articles * 0.2)))
    else:
        positive = draw(st.integers(min_value=0, max_value=int(total_articles * 0.4)))
        negative = draw(st.integers(min_value=0, max_value=int(total_articles * 0.4)))
    
    neutral = total_articles - positive - negative
    
    return SentimentScore(
        overall=overall,
        positive_count=positive,
        neutral_count=max(0, neutral),
        negative_count=negative,
        key_themes=draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
    )


class TestConditionsAnalysisProperties:
    """Property-based tests for Conditions analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FiveCsAnalyzer()

    @settings(max_examples=50)
    @given(
        industry_data=industry_data_strategy(),
        rbi_notifications=st.lists(rbi_notification_strategy(), max_size=10),
        sentiment=sentiment_score_strategy(),
    )
    def test_conditions_score_always_valid_range(
        self, industry_data, rbi_notifications, sentiment
    ):
        """
        Property: Conditions Score Validity
        
        For any Conditions assessment with any combination of industry data,
        RBI notifications, and sentiment scores, the resulting Conditions score
        should always be within the valid range of 0 to 100 inclusive.
        
        Validates: Requirements 9.4
        """
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        assert isinstance(result, ConditionsScore)
        assert 0.0 <= result.score <= 100.0, (
            f"Conditions score {result.score} is outside valid range [0, 100]"
        )

    @settings(max_examples=50)
    @given(
        industry_data=industry_data_strategy(),
        rbi_notifications=st.lists(rbi_notification_strategy(), max_size=10),
        sentiment=sentiment_score_strategy(),
    )
    def test_conditions_assessment_includes_all_risk_factors(
        self, industry_data, rbi_notifications, sentiment
    ):
        """
        Property: Conditions Assessment Data Sources
        
        For any Conditions assessment, the result should include assessments
        of sector-specific risks, regulatory risks, and commodity risks.
        
        Validates: Requirements 9.1, 9.2, 9.3
        """
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # Should have sector risk assessment
        assert hasattr(result, "sector_risk")
        assert result.sector_risk in ["Low", "Medium", "High"]
        
        # Should have regulatory risk assessment
        assert hasattr(result, "regulatory_risk")
        assert result.regulatory_risk in ["Low", "Medium", "High"]
        
        # Should have commodity risk assessment
        assert hasattr(result, "commodity_risk")
        assert result.commodity_risk in ["Low", "Medium", "High", "none"]

    @settings(max_examples=50)
    @given(
        industry_data=industry_data_strategy(),
        rbi_notifications=st.lists(rbi_notification_strategy(), max_size=10),
        sentiment=sentiment_score_strategy(),
    )
    def test_conditions_assessment_documents_risk_factors(
        self, industry_data, rbi_notifications, sentiment
    ):
        """
        Property: Conditions Risk Factor Documentation
        
        For any Conditions assessment, the result should document specific
        risk factors with supporting details.
        
        Validates: Requirements 9.5
        """
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # Should have risk_factors list
        assert hasattr(result, "risk_factors")
        assert isinstance(result.risk_factors, list)
        
        # If there are risk factors, they should be non-empty strings
        for factor in result.risk_factors:
            assert isinstance(factor, str)
            assert len(factor) > 0

    @settings(max_examples=30)
    @given(
        growth_rate=st.floats(min_value=-10.0, max_value=20.0),
        volatility=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_sector_risk_assessment_reflects_growth_and_volatility(
        self, growth_rate, volatility
    ):
        """
        Property: Sector Risk Assessment Accuracy
        
        For any sector with given growth rate and volatility, the sector risk
        assessment should reflect these factors appropriately.
        
        Validates: Requirements 9.1
        """
        industry_data = {
            "sector": "Manufacturing",
            "growth_rate": growth_rate,
            "volatility": volatility,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=0,
            neutral_count=10,
            negative_count=0,
            key_themes=[],
        )
        
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # High volatility should result in higher risk
        if volatility > 0.7:
            assert result.sector_risk == "High"
        elif volatility > 0.5:
            assert result.sector_risk in ["Medium", "High"]
        
        # Negative growth should result in higher risk
        if growth_rate < -5.0:
            assert result.sector_risk == "High"
        elif growth_rate < 0.0:
            assert result.sector_risk in ["Medium", "High"]

    @settings(max_examples=30)
    @given(
        num_notifications=st.integers(min_value=0, max_value=5),
    )
    def test_regulatory_risk_increases_with_notifications(
        self, num_notifications
    ):
        """
        Property: Regulatory Risk Assessment Accuracy
        
        For any number of RBI notifications, the regulatory risk assessment
        should increase as the number and severity of notifications increase.
        
        Validates: Requirements 9.2
        """
        industry_data = {
            "sector": "Banking",
            "growth_rate": 5.0,
            "volatility": 0.3,
            "commodity_exposure": False,
        }
        
        # Generate notifications with high severity
        rbi_notifications = [
            RBINotification(
                notification_id=f"RBI{i:03d}",
                title="RBI Restriction Notification",
                url=f"https://rbi.org.in/notification/RBI{i:03d}",
                published_date=datetime.now() - timedelta(days=i),
                sector="Banking",
                content="This is a high-severity restriction",
                summary="High severity: restrict",
            )
            for i in range(num_notifications)
        ]
        
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=0,
            neutral_count=10,
            negative_count=0,
            key_themes=[],
        )
        
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # More notifications should result in higher risk
        if num_notifications > 0:
            assert result.regulatory_risk in ["Medium", "High"]
        else:
            assert result.regulatory_risk == "Low"

    @settings(max_examples=30)
    @given(
        commodity_volatility=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_commodity_risk_reflects_volatility(self, commodity_volatility):
        """
        Property: Commodity Risk Assessment Accuracy
        
        For any commodity volatility level, the commodity risk assessment
        should reflect the volatility appropriately.
        
        Validates: Requirements 9.3
        """
        industry_data = {
            "sector": "Agriculture",
            "growth_rate": 3.0,
            "volatility": 0.3,
            "commodity_exposure": True,
            "commodity_volatility": commodity_volatility,
            "commodity_types": ["wheat", "rice"],
        }
        rbi_notifications = []
        sentiment = SentimentScore(
            overall=0.0,
            positive_count=0,
            neutral_count=10,
            negative_count=0,
            key_themes=[],
        )
        
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # High volatility should result in higher risk
        if commodity_volatility > 0.6:
            assert result.commodity_risk == "High"
        elif commodity_volatility > 0.4:
            assert result.commodity_risk in ["Medium", "High"]
        elif commodity_volatility > 0.2:
            assert result.commodity_risk in ["Low", "Medium"]
        else:
            assert result.commodity_risk in ["Low", "none"]

    @settings(max_examples=30)
    @given(
        sentiment_overall=st.floats(min_value=-1.0, max_value=1.0),
    )
    def test_sentiment_affects_conditions_score(self, sentiment_overall):
        """
        Property: Sentiment Impact on Conditions Score
        
        For any sentiment score, positive sentiment should improve the
        Conditions score and negative sentiment should worsen it.
        
        Validates: Requirements 9.4
        """
        industry_data = {
            "sector": "Technology",
            "growth_rate": 8.0,
            "volatility": 0.4,
            "commodity_exposure": False,
        }
        rbi_notifications = []
        
        # Create sentiment with given overall score
        if sentiment_overall > 0:
            positive_count = 70
            negative_count = 10
        elif sentiment_overall < 0:
            positive_count = 10
            negative_count = 70
        else:
            positive_count = 40
            negative_count = 40
        
        sentiment = SentimentScore(
            overall=sentiment_overall,
            positive_count=positive_count,
            neutral_count=100 - positive_count - negative_count,
            negative_count=negative_count,
            key_themes=[],
        )
        
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # Positive sentiment should result in higher score
        if sentiment_overall > 0.5:
            assert result.score >= 70
        # Negative sentiment should result in lower score
        elif sentiment_overall < -0.5:
            assert result.score <= 95  # Sentiment adjustment is max 15 points

    @settings(max_examples=50)
    @given(
        industry_data=industry_data_strategy(),
        rbi_notifications=st.lists(rbi_notification_strategy(), max_size=10),
        sentiment=sentiment_score_strategy(),
    )
    def test_conditions_score_consistency(
        self, industry_data, rbi_notifications, sentiment
    ):
        """
        Property: Conditions Score Consistency
        
        For the same input data, the Conditions analysis should produce
        the same score consistently.
        
        Validates: Requirements 9.4
        """
        result1 = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        result2 = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # Scores should be identical for identical inputs
        assert result1.score == result2.score
        assert result1.sector_risk == result2.sector_risk
        assert result1.regulatory_risk == result2.regulatory_risk
        assert result1.commodity_risk == result2.commodity_risk

    @settings(max_examples=30)
    @given(
        industry_data=industry_data_strategy(),
        rbi_notifications=st.lists(rbi_notification_strategy(), max_size=10),
        sentiment=sentiment_score_strategy(),
    )
    def test_conditions_result_has_required_fields(
        self, industry_data, rbi_notifications, sentiment
    ):
        """
        Property: Conditions Result Completeness
        
        For any Conditions assessment, the result should include all
        required fields for documentation and explanation.
        
        Validates: Requirements 9.5
        """
        result = self.analyzer.analyze_conditions(
            industry_data, rbi_notifications, sentiment
        )
        
        # Check all required fields are present
        assert hasattr(result, "score")
        assert hasattr(result, "sector_risk")
        assert hasattr(result, "regulatory_risk")
        assert hasattr(result, "commodity_risk")
        assert hasattr(result, "risk_factors")
        
        # Check field types
        assert isinstance(result.score, (int, float))
        assert isinstance(result.sector_risk, str)
        assert isinstance(result.regulatory_risk, str)
        assert isinstance(result.commodity_risk, str)
        assert isinstance(result.risk_factors, list)
