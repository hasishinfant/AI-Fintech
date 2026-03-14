"""Web crawler for external data source integration."""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.models.research import NewsArticle, MCAData, LegalCase, RBINotification

logger = logging.getLogger(__name__)


class WebCrawler:
    """
    Web crawler for gathering external intelligence data.
    
    Implements search_company_news(), fetch_mca_filings(), search_ecourts(),
    and fetch_rbi_notifications() with retry logic and error handling.
    
    Requirements: 2.1, 2.2, 2.3, 4.1, 4.3, 4.4, 4.5
    """
    
    def __init__(
        self,
        news_api_key: Optional[str] = None,
        mca_api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        """
        Initialize WebCrawler with API credentials and retry configuration.
        
        Args:
            news_api_key: API key for news service
            mca_api_key: API key for MCA data service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.news_api_key = news_api_key
        self.mca_api_key = mca_api_key
        self.timeout = timeout
        
        # Configure session with retry logic
        self.session = self._create_session(max_retries, backoff_factor)
    
    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """
        Create requests session with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def search_company_news(
        self,
        company_name: str,
        days_back: int = 90
    ) -> List[NewsArticle]:
        """
        Search news APIs for company mentions.
        
        Retrieves recent news articles about the specified company from the past
        N days. Includes retry logic and error handling for API calls.
        
        Args:
            company_name: Name of the company to search for
            days_back: Number of days to look back (default: 90)
            
        Returns:
            List of NewsArticle objects with source URLs and timestamps
            
        Requirements: 2.2, 4.1, 4.6
        """
        articles = []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Example using NewsAPI (https://newsapi.org/)
            # In production, this would use actual API credentials
            if self.news_api_key:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": company_name,
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": self.news_api_key
                }
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                for article_data in data.get("articles", []):
                    article = NewsArticle(
                        title=article_data.get("title", ""),
                        source=article_data.get("source", {}).get("name", "Unknown"),
                        url=article_data.get("url", ""),
                        published_date=datetime.fromisoformat(
                            article_data.get("publishedAt", "").replace("Z", "+00:00")
                        ),
                        content=article_data.get("description", ""),
                        sentiment="neutral"  # Will be analyzed separately
                    )
                    articles.append(article)
                
                logger.info(f"Retrieved {len(articles)} news articles for {company_name}")
            else:
                logger.warning("News API key not configured, returning empty results")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news for {company_name}: {e}")
            # Return empty list on error (graceful degradation)
        
        except Exception as e:
            logger.error(f"Unexpected error in search_company_news: {e}")
        
        return articles
    
    def fetch_mca_filings(self, cin: str) -> Optional[MCAData]:
        """
        Retrieve MCA filings for company.
        
        Fetches Ministry of Corporate Affairs data including company registration,
        directors, capital structure, and compliance status.
        
        Args:
            cin: Corporate Identification Number (21-character unique identifier)
            
        Returns:
            MCAData object with company information, or None on error
            
        Requirements: 2.1, 4.3, 4.6
        """
        try:
            # Example using MCA API
            # In production, this would use actual MCA API or data provider
            if self.mca_api_key:
                url = f"https://api.mca.gov.in/v1/company/{cin}"
                headers = {
                    "Authorization": f"Bearer {self.mca_api_key}",
                    "Content-Type": "application/json"
                }
                
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                mca_data = MCAData(
                    cin=cin,
                    company_name=data.get("company_name", ""),
                    registration_date=datetime.fromisoformat(
                        data.get("registration_date", "")
                    ),
                    authorized_capital=float(data.get("authorized_capital", 0)),
                    paid_up_capital=float(data.get("paid_up_capital", 0)),
                    last_filing_date=datetime.fromisoformat(
                        data.get("last_filing_date", "")
                    ),
                    compliance_status=data.get("compliance_status", "Unknown"),
                    directors=data.get("directors", [])
                )
                
                logger.info(f"Retrieved MCA data for CIN: {cin}")
                return mca_data
            else:
                logger.warning("MCA API key not configured, returning None")
                return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching MCA data for CIN {cin}: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error in fetch_mca_filings: {e}")
            return None
    
    def search_ecourts(
        self,
        company_name: str,
        promoter_names: Optional[List[str]] = None
    ) -> List[LegalCase]:
        """
        Search e-Courts database for litigation.
        
        Searches the Indian e-Courts system for pending or past litigation
        involving the company or its promoters.
        
        Args:
            company_name: Name of the company to search for
            promoter_names: Optional list of promoter names to search
            
        Returns:
            List of LegalCase objects with case details
            
        Requirements: 2.3, 4.4, 4.6
        """
        cases = []
        
        try:
            # Example using e-Courts API
            # In production, this would use actual e-Courts API or data provider
            url = "https://services.ecourts.gov.in/ecourtindia_v6/cases/search"
            
            # Search for company
            search_terms = [company_name]
            if promoter_names:
                search_terms.extend(promoter_names)
            
            for search_term in search_terms:
                params = {
                    "party_name": search_term,
                    "state_code": "all",
                    "dist_code": "all"
                }
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                for case_data in data.get("cases", []):
                    case = LegalCase(
                        case_number=case_data.get("case_number", ""),
                        court=case_data.get("court_name", ""),
                        filing_date=datetime.fromisoformat(
                            case_data.get("filing_date", "")
                        ),
                        case_type=case_data.get("case_type", ""),
                        status=case_data.get("status", ""),
                        summary=case_data.get("case_summary", ""),
                        parties=case_data.get("parties", [])
                    )
                    cases.append(case)
            
            logger.info(f"Retrieved {len(cases)} legal cases for {company_name}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching e-Courts for {company_name}: {e}")
            # Return empty list on error (graceful degradation)
        
        except Exception as e:
            logger.error(f"Unexpected error in search_ecourts: {e}")
        
        return cases
    
    def fetch_rbi_notifications(self, sector: str) -> List[RBINotification]:
        """
        Retrieve relevant RBI notifications for regulatory data.
        
        Fetches Reserve Bank of India notifications and circulars relevant
        to the specified sector.
        
        Args:
            sector: Industry sector (e.g., "Banking", "NBFC", "Manufacturing")
            
        Returns:
            List of RBINotification objects with regulatory updates
            
        Requirements: 4.5, 4.6
        """
        notifications = []
        
        try:
            # Example using RBI website scraping or API
            # In production, this would scrape RBI website or use data provider
            url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx"
            params = {
                "Id": sector,
                "Mode": "0"
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML response (simplified example)
            # In production, would use BeautifulSoup or similar
            # For now, return empty list as placeholder
            
            logger.info(f"Retrieved {len(notifications)} RBI notifications for sector: {sector}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching RBI notifications for sector {sector}: {e}")
            # Return empty list on error (graceful degradation)
        
        except Exception as e:
            logger.error(f"Unexpected error in fetch_rbi_notifications: {e}")
        
        return notifications
    
    def close(self):
        """Close the session and cleanup resources."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
