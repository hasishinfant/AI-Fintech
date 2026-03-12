"""Unit tests for SentimentAnalyzer class."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from app.services.research_agent.sentiment_analyzer import SentimentAnalyzer
from app.models.research import NewsArticle, SentimentScore


class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create SentimentAnalyzer instance for testing."""
        return SentimentAnalyzer(
            openai_api_key=None,  # Use rule-based for testing
            model="gpt-3.5-turbo"
        )
    
    @pytest.fixture
    def sample_articles(self):
        """Create sample news articles for testing."""
        return [
            NewsArticle(
                title="Company XYZ Reports Strong Q4 Growth",
                source="Business Times",
                url="https://example.com/article1",
                published_date=datetime(2024, 1, 15),
                content="Company XYZ announced strong growth in Q4 with increased revenue and profit margins.",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Company XYZ Faces Lawsuit Over Contract Dispute",
                source="Legal News",
                url="https://example.com/article2",
                published_date=datetime(2024, 1, 10),
                content="Company XYZ is facing a lawsuit from a former partner over alleged contract violations.",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Company XYZ Launches New Product Line",
                source="Tech Daily",
                url="https://example.com/article3",
                published_date=datetime(2024, 1, 5),
                content="Company XYZ successfully launched its innovative new product line to positive market reception.",
                sentiment="neutral"
            )
        ]
    
    def test_initialization(self, analyzer):
        """Test SentimentAnalyzer initialization."""
        assert analyzer.openai_api_key is None
        assert analyzer.model == "gpt-3.5-turbo"
        assert analyzer.use_local_llm is False
        assert analyzer.client is None
    
    def test_initialization_with_openai_key(self):
        """Test initialization with OpenAI API key."""
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        assert analyzer.openai_api_key == "test_key"
        assert analyzer.client is not None
    
    def test_analyze_news_sentiment_empty_list(self, analyzer):
        """Test sentiment analysis with empty article list."""
        result = analyzer.analyze_news_sentiment([])
        
        assert result.overall == 0.0
        assert result.positive_count == 0
        assert result.neutral_count == 0
        assert result.negative_count == 0
        assert result.key_themes == []
    
    def test_analyze_news_sentiment_rule_based(self, analyzer, sample_articles):
        """Test sentiment analysis using rule-based classification."""
        result = analyzer.analyze_news_sentiment(sample_articles)
        
        # Verify result structure
        assert isinstance(result, SentimentScore)
        assert -1.0 <= result.overall <= 1.0
        assert result.positive_count + result.neutral_count + result.negative_count == 3
        
        # Verify articles were classified
        assert sample_articles[0].sentiment in ["positive", "neutral", "negative"]
        assert sample_articles[1].sentiment in ["positive", "neutral", "negative"]
        assert sample_articles[2].sentiment in ["positive", "neutral", "negative"]
        
        # Verify key themes were extracted
        assert isinstance(result.key_themes, list)
    
    def test_classify_with_rules_positive(self, analyzer):
        """Test rule-based classification for positive sentiment."""
        text = "Company achieved strong growth with increased profit and successful expansion"
        sentiment = analyzer._classify_with_rules(text)
        assert sentiment == "positive"
    
    def test_classify_with_rules_negative(self, analyzer):
        """Test rule-based classification for negative sentiment."""
        text = "Company faces lawsuit and reports significant loss with declining revenue"
        sentiment = analyzer._classify_with_rules(text)
        assert sentiment == "negative"
    
    def test_classify_with_rules_neutral(self, analyzer):
        """Test rule-based classification for neutral sentiment."""
        text = "Company held its annual meeting and discussed various topics"
        sentiment = analyzer._classify_with_rules(text)
        assert sentiment == "neutral"
    
    def test_classify_with_rules_empty_text(self, analyzer):
        """Test rule-based classification with empty text."""
        sentiment = analyzer._classify_with_rules("")
        assert sentiment == "neutral"
    
    def test_extract_themes_with_rules(self, analyzer):
        """Test theme extraction using rule-based approach."""
        article = NewsArticle(
            title="Company Reports Strong Financial Results",
            source="Business Times",
            url="https://example.com/article",
            published_date=datetime(2024, 1, 15),
            content="Company announced strong revenue growth and improved profit margins in Q4.",
            sentiment="neutral"
        )
        
        themes = analyzer._extract_themes_with_rules(article)
        
        assert isinstance(themes, list)
        assert len(themes) <= 3
        # Should detect "Financial Performance" theme
        assert any("financial" in theme.lower() for theme in themes)
    
    def test_extract_themes_multiple_categories(self, analyzer):
        """Test theme extraction with multiple theme categories."""
        article = NewsArticle(
            title="Company Faces Regulatory Investigation",
            source="Legal News",
            url="https://example.com/article",
            published_date=datetime(2024, 1, 15),
            content="Regulatory authorities have launched an investigation into the company's compliance practices.",
            sentiment="neutral"
        )
        
        themes = analyzer._extract_themes_with_rules(article)
        
        assert isinstance(themes, list)
        # Should detect both "Legal Issues" and "Regulatory" themes
        assert len(themes) > 0
    
    def test_aggregate_themes(self, analyzer):
        """Test theme aggregation and deduplication."""
        themes = [
            "Financial Performance",
            "financial performance",
            "Legal Issues",
            "Financial Performance",
            "Market",
            "legal issues",
            "Operations"
        ]
        
        aggregated = analyzer._aggregate_themes(themes)
        
        assert isinstance(aggregated, list)
        assert len(aggregated) <= 5
        # Most frequent theme should be first
        assert "financial performance" == aggregated[0]
    
    def test_extract_key_events_empty_list(self, analyzer):
        """Test key event extraction with empty article list."""
        events = analyzer.extract_key_events([])
        assert events == []
    
    def test_extract_key_events_rule_based(self, analyzer, sample_articles):
        """Test key event extraction using rule-based approach."""
        events = analyzer.extract_key_events(sample_articles)
        
        assert isinstance(events, list)
        assert len(events) > 0
        assert len(events) <= 20  # Should limit to top 20
        
        # Verify event structure
        for event in events:
            assert "event" in event
            assert "date" in event
            assert "source" in event
            assert "sentiment" in event
            assert isinstance(event["date"], datetime)
    
    def test_extract_events_with_rules(self, analyzer):
        """Test event extraction from single article using rules."""
        article = NewsArticle(
            title="Company Announces Major Acquisition",
            source="Business Times",
            url="https://example.com/article",
            published_date=datetime(2024, 1, 15),
            content="Company announced the acquisition of a competitor for $100M.",
            sentiment="positive"
        )
        
        events = analyzer._extract_events_with_rules(article)
        
        assert len(events) == 1
        assert events[0]["event"] == "Company Announces Major Acquisition"
        assert events[0]["date"] == datetime(2024, 1, 15)
        assert events[0]["source"] == "https://example.com/article"
        assert events[0]["sentiment"] == "positive"
    
    def test_extract_key_events_sorting(self, analyzer):
        """Test that key events are sorted by date (most recent first)."""
        articles = [
            NewsArticle(
                title="Old Event",
                source="Source",
                url="https://example.com/1",
                published_date=datetime(2024, 1, 1),
                content="Old content",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Recent Event",
                source="Source",
                url="https://example.com/2",
                published_date=datetime(2024, 1, 20),
                content="Recent content",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Middle Event",
                source="Source",
                url="https://example.com/3",
                published_date=datetime(2024, 1, 10),
                content="Middle content",
                sentiment="neutral"
            )
        ]
        
        events = analyzer.extract_key_events(articles)
        
        # Most recent should be first
        assert events[0]["event"] == "Recent Event"
        assert events[1]["event"] == "Middle Event"
        assert events[2]["event"] == "Old Event"
    
    @patch('app.services.research_agent.sentiment_analyzer.OpenAI')
    def test_classify_with_openai_success(self, mock_openai_class):
        """Test sentiment classification using OpenAI API."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="positive"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        analyzer.client = mock_client
        
        sentiment = analyzer._classify_with_openai("Great news about company growth")
        
        assert sentiment == "positive"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('app.services.research_agent.sentiment_analyzer.OpenAI')
    def test_classify_with_openai_invalid_response(self, mock_openai_class):
        """Test handling of invalid OpenAI response."""
        # Mock OpenAI client with invalid response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="invalid_sentiment"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        analyzer.client = mock_client
        
        sentiment = analyzer._classify_with_openai("Some text")
        
        # Should default to neutral for invalid response
        assert sentiment == "neutral"
    
    @patch('app.services.research_agent.sentiment_analyzer.OpenAI')
    def test_classify_with_openai_error_fallback(self, mock_openai_class):
        """Test fallback to rule-based on OpenAI error."""
        # Mock OpenAI client that raises exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        analyzer.client = mock_client
        
        article = NewsArticle(
            title="Company Reports Strong Growth",
            source="Source",
            url="https://example.com",
            published_date=datetime(2024, 1, 15),
            content="Strong profit and revenue growth",
            sentiment="neutral"
        )
        
        sentiment = analyzer._classify_article_sentiment(article)
        
        # Should fall back to rule-based classification
        assert sentiment in ["positive", "neutral", "negative"]
    
    @patch('app.services.research_agent.sentiment_analyzer.OpenAI')
    def test_extract_themes_with_openai(self, mock_openai_class):
        """Test theme extraction using OpenAI API."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Financial Performance, Market Expansion, Innovation"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        analyzer.client = mock_client
        
        article = NewsArticle(
            title="Company Expands",
            source="Source",
            url="https://example.com",
            published_date=datetime(2024, 1, 15),
            content="Content",
            sentiment="neutral"
        )
        
        themes = analyzer._extract_themes_with_openai(article)
        
        assert len(themes) == 3
        assert "Financial Performance" in themes
        assert "Market Expansion" in themes
        assert "Innovation" in themes
    
    @patch('app.services.research_agent.sentiment_analyzer.OpenAI')
    def test_extract_events_with_openai(self, mock_openai_class):
        """Test event extraction using OpenAI API."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="1. Company announced Q4 results\n2. New CEO appointed\n3. Product launch scheduled"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        analyzer = SentimentAnalyzer(openai_api_key="test_key")
        analyzer.client = mock_client
        
        article = NewsArticle(
            title="Company News",
            source="Source",
            url="https://example.com",
            published_date=datetime(2024, 1, 15),
            content="Content",
            sentiment="positive"
        )
        
        events = analyzer._extract_events_with_openai(article)
        
        assert len(events) == 3
        assert "Q4 results" in events[0]["event"]
        assert events[0]["sentiment"] == "positive"
        assert events[0]["source"] == "https://example.com"
    
    def test_sentiment_score_calculation(self, analyzer):
        """Test overall sentiment score calculation."""
        articles = [
            NewsArticle(
                title="Positive News",
                source="Source",
                url="https://example.com/1",
                published_date=datetime(2024, 1, 15),
                content="Great success and strong growth with improved profit",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Negative News",
                source="Source",
                url="https://example.com/2",
                published_date=datetime(2024, 1, 15),
                content="Lawsuit and loss with declining revenue and bankruptcy concerns",
                sentiment="neutral"
            ),
            NewsArticle(
                title="Positive News 2",
                source="Source",
                url="https://example.com/3",
                published_date=datetime(2024, 1, 15),
                content="Achievement and innovation with successful expansion",
                sentiment="neutral"
            )
        ]
        
        result = analyzer.analyze_news_sentiment(articles)
        
        # Should have 2 positive, 1 negative
        # Overall score = (2 - 1) / 3 = 0.33
        assert result.positive_count == 2
        assert result.negative_count == 1
        assert result.neutral_count == 0
        assert abs(result.overall - 0.33) < 0.01
    
    def test_classify_article_sentiment_empty_content(self, analyzer):
        """Test classification with empty article content."""
        article = NewsArticle(
            title="",
            source="Source",
            url="https://example.com",
            published_date=datetime(2024, 1, 15),
            content="",
            sentiment="neutral"
        )
        
        sentiment = analyzer._classify_article_sentiment(article)
        assert sentiment == "neutral"
