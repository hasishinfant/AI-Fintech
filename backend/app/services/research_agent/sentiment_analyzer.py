"""Sentiment analysis and key event extraction from news articles."""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime

from openai import OpenAI

from app.models.research import NewsArticle, SentimentScore

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analyzer for news articles using NLP models.
    
    Implements analyze_news_sentiment() and extract_key_events() with
    integration to OpenAI/Llama for advanced text analysis.
    
    Requirements: 4.2
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        use_local_llm: bool = False,
        local_llm_url: Optional[str] = None
    ):
        """
        Initialize SentimentAnalyzer with LLM configuration.
        
        Args:
            openai_api_key: OpenAI API key for GPT models
            model: Model name to use (default: gpt-3.5-turbo)
            use_local_llm: Whether to use local Llama model instead of OpenAI
            local_llm_url: URL for local Llama API endpoint
        """
        self.openai_api_key = openai_api_key
        self.model = model
        self.use_local_llm = use_local_llm
        self.local_llm_url = local_llm_url
        
        # Initialize OpenAI client if API key provided
        self.client = None
        if openai_api_key and not use_local_llm:
            self.client = OpenAI(api_key=openai_api_key)
    
    def analyze_news_sentiment(self, articles: List[NewsArticle]) -> SentimentScore:
        """
        Analyze sentiment of news articles.
        
        Processes a list of news articles and determines overall sentiment
        (positive, neutral, negative) using NLP models. Classifies each article
        and aggregates results into an overall sentiment score.
        
        Args:
            articles: List of NewsArticle objects to analyze
            
        Returns:
            SentimentScore with overall sentiment (-1 to 1), counts by category,
            and key themes extracted from the articles
            
        Requirements: 4.2
        """
        if not articles:
            logger.warning("No articles provided for sentiment analysis")
            return SentimentScore(
                overall=0.0,
                positive_count=0,
                neutral_count=0,
                negative_count=0,
                key_themes=[]
            )
        
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        all_themes = []
        
        # Analyze each article
        for article in articles:
            sentiment = self._classify_article_sentiment(article)
            
            # Update article sentiment
            article.sentiment = sentiment
            
            # Count sentiments
            if sentiment == "positive":
                positive_count += 1
            elif sentiment == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            # Extract themes from article
            themes = self._extract_themes(article)
            all_themes.extend(themes)
        
        # Calculate overall sentiment score (-1 to 1)
        total = len(articles)
        overall_score = (positive_count - negative_count) / total if total > 0 else 0.0
        
        # Get top key themes (deduplicate and limit)
        key_themes = self._aggregate_themes(all_themes)
        
        sentiment_score = SentimentScore(
            overall=overall_score,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            key_themes=key_themes
        )
        
        logger.info(
            f"Analyzed {total} articles: "
            f"{positive_count} positive, {neutral_count} neutral, "
            f"{negative_count} negative. Overall score: {overall_score:.2f}"
        )
        
        return sentiment_score
    
    def extract_key_events(self, articles: List[NewsArticle]) -> List[Dict[str, str]]:
        """
        Extract significant events from news articles.
        
        Uses NLP to identify and extract key events, announcements, and
        developments mentioned in news articles about the company.
        
        Args:
            articles: List of NewsArticle objects to process
            
        Returns:
            List of dictionaries containing event information with keys:
            - event: Description of the event
            - date: Date of the event (if mentioned)
            - source: Source article URL
            - sentiment: Sentiment of the event (positive/neutral/negative)
            
        Requirements: 4.2
        """
        if not articles:
            logger.warning("No articles provided for key event extraction")
            return []
        
        key_events = []
        
        for article in articles:
            events = self._extract_events_from_article(article)
            key_events.extend(events)
        
        # Sort by date (most recent first) and limit to top events
        key_events.sort(
            key=lambda x: x.get("date", datetime.min),
            reverse=True
        )
        
        logger.info(f"Extracted {len(key_events)} key events from {len(articles)} articles")
        
        return key_events[:20]  # Return top 20 events
    
    def _classify_article_sentiment(self, article: NewsArticle) -> str:
        """
        Classify sentiment of a single article.
        
        Args:
            article: NewsArticle to classify
            
        Returns:
            Sentiment classification: "positive", "neutral", or "negative"
        """
        # Combine title and content for analysis
        text = f"{article.title}. {article.content}"
        
        if not text.strip():
            return "neutral"
        
        # Use LLM for sentiment classification
        if self.client:
            try:
                sentiment = self._classify_with_openai(text)
                return sentiment
            except Exception as e:
                logger.error(f"Error classifying sentiment with OpenAI: {e}")
                # Fall back to rule-based classification
                return self._classify_with_rules(text)
        else:
            # Use rule-based classification if no LLM available
            return self._classify_with_rules(text)
    
    def _classify_with_openai(self, text: str) -> str:
        """
        Classify sentiment using OpenAI API.
        
        Args:
            text: Text to classify
            
        Returns:
            Sentiment: "positive", "neutral", or "negative"
        """
        prompt = f"""Analyze the sentiment of the following news text about a company.
Classify it as exactly one of: positive, neutral, or negative.

Text: {text[:1000]}

Respond with only one word: positive, neutral, or negative."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial news sentiment analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10
        )
        
        sentiment = response.choices[0].message.content.strip().lower()
        
        # Validate response
        if sentiment not in ["positive", "neutral", "negative"]:
            logger.warning(f"Invalid sentiment from OpenAI: {sentiment}, defaulting to neutral")
            return "neutral"
        
        return sentiment
    
    def _classify_with_rules(self, text: str) -> str:
        """
        Classify sentiment using rule-based approach.
        
        Simple keyword-based sentiment classification as fallback.
        
        Args:
            text: Text to classify
            
        Returns:
            Sentiment: "positive", "neutral", or "negative"
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_keywords = [
            "growth", "profit", "success", "expansion", "award", "achievement",
            "innovation", "partnership", "agreement", "approved", "launched",
            "increased", "improved", "strong", "positive", "gain", "win"
        ]
        
        # Negative keywords
        negative_keywords = [
            "loss", "decline", "lawsuit", "fraud", "scandal", "investigation",
            "penalty", "fine", "default", "bankruptcy", "closure", "layoff",
            "decreased", "weak", "negative", "fail", "crisis", "concern"
        ]
        
        positive_score = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_score = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def _extract_themes(self, article: NewsArticle) -> List[str]:
        """
        Extract themes from an article.
        
        Args:
            article: NewsArticle to extract themes from
            
        Returns:
            List of theme strings
        """
        # Use LLM for theme extraction if available
        if self.client:
            try:
                return self._extract_themes_with_openai(article)
            except Exception as e:
                logger.error(f"Error extracting themes with OpenAI: {e}")
                return self._extract_themes_with_rules(article)
        else:
            return self._extract_themes_with_rules(article)
    
    def _extract_themes_with_openai(self, article: NewsArticle) -> List[str]:
        """
        Extract themes using OpenAI API.
        
        Args:
            article: NewsArticle to extract themes from
            
        Returns:
            List of theme strings
        """
        text = f"{article.title}. {article.content}"
        
        prompt = f"""Extract 2-3 key themes or topics from this news article about a company.
Return only the themes as a comma-separated list.

Text: {text[:1000]}

Themes:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial news analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        themes_text = response.choices[0].message.content.strip()
        themes = [theme.strip() for theme in themes_text.split(",")]
        
        return themes[:3]  # Limit to 3 themes per article
    
    def _extract_themes_with_rules(self, article: NewsArticle) -> List[str]:
        """
        Extract themes using rule-based approach.
        
        Args:
            article: NewsArticle to extract themes from
            
        Returns:
            List of theme strings
        """
        text = f"{article.title}. {article.content}".lower()
        
        # Theme keywords
        theme_keywords = {
            "Financial Performance": ["revenue", "profit", "earnings", "financial", "results"],
            "Legal Issues": ["lawsuit", "litigation", "court", "legal", "case"],
            "Regulatory": ["regulation", "compliance", "rbi", "sebi", "government"],
            "Operations": ["operations", "production", "manufacturing", "facility"],
            "Management": ["ceo", "director", "management", "board", "appointment"],
            "Market": ["market", "share", "competition", "industry"],
            "Technology": ["technology", "digital", "innovation", "ai", "automation"],
            "Expansion": ["expansion", "growth", "acquisition", "merger", "new"]
        }
        
        detected_themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes[:3]  # Limit to 3 themes
    
    def _aggregate_themes(self, themes: List[str]) -> List[str]:
        """
        Aggregate and deduplicate themes.
        
        Args:
            themes: List of all themes from articles
            
        Returns:
            List of top themes (deduplicated and limited)
        """
        # Count theme occurrences
        theme_counts = {}
        for theme in themes:
            theme_lower = theme.lower().strip()
            theme_counts[theme_lower] = theme_counts.get(theme_lower, 0) + 1
        
        # Sort by frequency
        sorted_themes = sorted(
            theme_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top 5 themes
        return [theme for theme, count in sorted_themes[:5]]
    
    def _extract_events_from_article(self, article: NewsArticle) -> List[Dict[str, str]]:
        """
        Extract key events from a single article.
        
        Args:
            article: NewsArticle to extract events from
            
        Returns:
            List of event dictionaries
        """
        # Use LLM for event extraction if available
        if self.client:
            try:
                return self._extract_events_with_openai(article)
            except Exception as e:
                logger.error(f"Error extracting events with OpenAI: {e}")
                return self._extract_events_with_rules(article)
        else:
            return self._extract_events_with_rules(article)
    
    def _extract_events_with_openai(self, article: NewsArticle) -> List[Dict[str, str]]:
        """
        Extract events using OpenAI API.
        
        Args:
            article: NewsArticle to extract events from
            
        Returns:
            List of event dictionaries
        """
        text = f"{article.title}. {article.content}"
        
        prompt = f"""Extract key business events from this news article.
For each event, provide a brief description.
Return up to 3 events, one per line.

Text: {text[:1500]}

Events:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial news analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        events_text = response.choices[0].message.content.strip()
        event_lines = [line.strip() for line in events_text.split("\n") if line.strip()]
        
        events = []
        for event_desc in event_lines[:3]:
            # Clean up event description
            event_desc = re.sub(r"^[-•*\d.]+\s*", "", event_desc)
            
            events.append({
                "event": event_desc,
                "date": article.published_date,
                "source": article.url,
                "sentiment": article.sentiment
            })
        
        return events
    
    def _extract_events_with_rules(self, article: NewsArticle) -> List[Dict[str, str]]:
        """
        Extract events using rule-based approach.
        
        Args:
            article: NewsArticle to extract events from
            
        Returns:
            List of event dictionaries
        """
        # Simple rule-based: use article title as the event
        # In production, would use more sophisticated NLP
        
        event = {
            "event": article.title,
            "date": article.published_date,
            "source": article.url,
            "sentiment": article.sentiment
        }
        
        return [event]
