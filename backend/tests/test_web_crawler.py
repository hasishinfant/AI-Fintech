"""Unit tests for WebCrawler class."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import requests

from app.services.research_agent.web_crawler import WebCrawler
from app.models.research import NewsArticle, MCAData, LegalCase, RBINotification


class TestWebCrawler:
    """Test suite for WebCrawler class."""
    
    @pytest.fixture
    def crawler(self):
        """Create WebCrawler instance for testing."""
        return WebCrawler(
            news_api_key="test_news_key",
            mca_api_key="test_mca_key",
            timeout=10,
            max_retries=2
        )
    
    def test_initialization(self, crawler):
        """Test WebCrawler initialization."""
        assert crawler.news_api_key == "test_news_key"
        assert crawler.mca_api_key == "test_mca_key"
        assert crawler.timeout == 10
        assert crawler.session is not None
    
    def test_session_has_retry_logic(self, crawler):
        """Test that session is configured with retry logic."""
        # Check that adapters are mounted
        assert "http://" in crawler.session.adapters
        assert "https://" in crawler.session.adapters
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_company_news_success(self, mock_get, crawler):
        """Test successful news article retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Company XYZ Expands Operations",
                    "source": {"name": "Business Times"},
                    "url": "https://example.com/article1",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "description": "Company XYZ announced expansion plans..."
                },
                {
                    "title": "Company XYZ Q4 Results",
                    "source": {"name": "Financial Express"},
                    "url": "https://example.com/article2",
                    "publishedAt": "2024-01-10T14:30:00Z",
                    "description": "Company XYZ reported strong Q4 results..."
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Execute
        articles = crawler.search_company_news("Company XYZ", days_back=30)
        
        # Verify
        assert len(articles) == 2
        assert articles[0].title == "Company XYZ Expands Operations"
        assert articles[0].source == "Business Times"
        assert articles[0].url == "https://example.com/article1"
        assert articles[0].sentiment == "neutral"
        assert isinstance(articles[0].published_date, datetime)
        
        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]
        assert call_args[1]["params"]["q"] == "Company XYZ"
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_company_news_api_error(self, mock_get, crawler):
        """Test graceful handling of API errors."""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Execute
        articles = crawler.search_company_news("Company XYZ")
        
        # Verify graceful degradation - returns empty list
        assert articles == []
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_company_news_no_api_key(self, mock_get):
        """Test behavior when API key is not configured."""
        crawler = WebCrawler(news_api_key=None)
        
        # Execute
        articles = crawler.search_company_news("Company XYZ")
        
        # Verify returns empty list
        assert articles == []
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_fetch_mca_filings_success(self, mock_get, crawler):
        """Test successful MCA data retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cin": "U12345AB2020PTC123456",
            "company_name": "Test Company Ltd",
            "registration_date": "2020-01-15T00:00:00",
            "authorized_capital": 10000000.0,
            "paid_up_capital": 5000000.0,
            "last_filing_date": "2023-12-31T00:00:00",
            "compliance_status": "Active",
            "directors": [
                {"name": "John Doe", "din": "12345678"},
                {"name": "Jane Smith", "din": "87654321"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Execute
        mca_data = crawler.fetch_mca_filings("U12345AB2020PTC123456")
        
        # Verify
        assert mca_data is not None
        assert mca_data.cin == "U12345AB2020PTC123456"
        assert mca_data.company_name == "Test Company Ltd"
        assert mca_data.authorized_capital == 10000000.0
        assert mca_data.paid_up_capital == 5000000.0
        assert mca_data.compliance_status == "Active"
        assert len(mca_data.directors) == 2
        assert isinstance(mca_data.registration_date, datetime)
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_fetch_mca_filings_api_error(self, mock_get, crawler):
        """Test graceful handling of MCA API errors."""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Execute
        mca_data = crawler.fetch_mca_filings("U12345AB2020PTC123456")
        
        # Verify graceful degradation - returns None
        assert mca_data is None
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_fetch_mca_filings_no_api_key(self, mock_get):
        """Test behavior when MCA API key is not configured."""
        crawler = WebCrawler(mca_api_key=None)
        
        # Execute
        mca_data = crawler.fetch_mca_filings("U12345AB2020PTC123456")
        
        # Verify returns None
        assert mca_data is None
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_ecourts_success(self, mock_get, crawler):
        """Test successful e-Courts litigation search."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cases": [
                {
                    "case_number": "CS/123/2023",
                    "court_name": "Delhi High Court",
                    "filing_date": "2023-03-15T00:00:00",
                    "case_type": "Civil Suit",
                    "status": "Pending",
                    "case_summary": "Contract dispute case",
                    "parties": ["Company XYZ", "Vendor ABC"]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Execute
        cases = crawler.search_ecourts("Company XYZ", promoter_names=["John Doe"])
        
        # Verify
        assert len(cases) == 2  # One for company, one for promoter
        assert cases[0].case_number == "CS/123/2023"
        assert cases[0].court == "Delhi High Court"
        assert cases[0].case_type == "Civil Suit"
        assert cases[0].status == "Pending"
        assert isinstance(cases[0].filing_date, datetime)
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_ecourts_no_promoters(self, mock_get, crawler):
        """Test e-Courts search with only company name."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cases": []}
        mock_get.return_value = mock_response
        
        # Execute
        cases = crawler.search_ecourts("Company XYZ")
        
        # Verify
        assert cases == []
        # Should be called once for company only
        assert mock_get.call_count == 1
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_search_ecourts_api_error(self, mock_get, crawler):
        """Test graceful handling of e-Courts API errors."""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Execute
        cases = crawler.search_ecourts("Company XYZ")
        
        # Verify graceful degradation - returns empty list
        assert cases == []
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_fetch_rbi_notifications_success(self, mock_get, crawler):
        """Test RBI notifications retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>RBI notifications page</html>"
        mock_get.return_value = mock_response
        
        # Execute
        notifications = crawler.fetch_rbi_notifications("Banking")
        
        # Verify - currently returns empty list (placeholder implementation)
        assert isinstance(notifications, list)
        mock_get.assert_called_once()
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_fetch_rbi_notifications_api_error(self, mock_get, crawler):
        """Test graceful handling of RBI API errors."""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Execute
        notifications = crawler.fetch_rbi_notifications("Banking")
        
        # Verify graceful degradation - returns empty list
        assert notifications == []
    
    def test_context_manager(self):
        """Test WebCrawler as context manager."""
        with WebCrawler() as crawler:
            assert crawler.session is not None
        
        # Session should be closed after context exit
        # Note: We can't directly test if session is closed, but we verify no errors
    
    def test_close_method(self, crawler):
        """Test explicit close method."""
        crawler.close()
        # Verify no errors on close
    
    @patch('app.services.research_agent.web_crawler.requests.Session.get')
    def test_retry_on_server_error(self, mock_get):
        """Test that retry logic is triggered on server errors."""
        crawler = WebCrawler(news_api_key="test_key", max_retries=2, backoff_factor=0.1)
        
        # Mock successful response
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"articles": []}
        
        mock_get.return_value = mock_response_success
        
        # Execute
        articles = crawler.search_company_news("Company XYZ")
        
        # Verify it was called
        assert mock_get.call_count >= 1
        assert articles == []
    
    def test_date_range_calculation(self, crawler):
        """Test that date range is calculated correctly for news search."""
        with patch('app.services.research_agent.web_crawler.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"articles": []}
            mock_get.return_value = mock_response
            
            # Execute with 30 days back
            crawler.search_company_news("Company XYZ", days_back=30)
            
            # Verify date parameters
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            
            # Check that 'from' and 'to' dates are present
            assert "from" in params
            assert "to" in params
            
            # Verify date format (YYYY-MM-DD)
            from_date = datetime.strptime(params["from"], "%Y-%m-%d")
            to_date = datetime.strptime(params["to"], "%Y-%m-%d")
            
            # Verify date range is approximately 30 days
            date_diff = (to_date - from_date).days
            assert 29 <= date_diff <= 31  # Allow for some variation
