"""
Demo script showing SentimentAnalyzer integration with WebCrawler.

This example demonstrates how to:
1. Fetch news articles using WebCrawler
2. Analyze sentiment using SentimentAnalyzer
3. Extract key events from articles
"""

import os
from datetime import datetime

from app.services.research_agent.web_crawler import WebCrawler
from app.services.research_agent.sentiment_analyzer import SentimentAnalyzer
from app.models.research import NewsArticle


def demo_sentiment_analysis():
    """Demonstrate sentiment analysis workflow."""
    
    print("=" * 80)
    print("Sentiment Analysis Demo")
    print("=" * 80)
    
    # Create sample news articles (in production, these would come from WebCrawler)
    sample_articles = [
        NewsArticle(
            title="TechCorp Reports Record Q4 Revenue Growth",
            source="Business Times",
            url="https://example.com/article1",
            published_date=datetime(2024, 1, 15),
            content="TechCorp announced record-breaking Q4 revenue growth of 45%, "
                   "driven by strong demand for its innovative products. The company "
                   "also reported improved profit margins and successful market expansion.",
            sentiment="neutral"
        ),
        NewsArticle(
            title="TechCorp Faces Regulatory Investigation",
            source="Legal News",
            url="https://example.com/article2",
            published_date=datetime(2024, 1, 10),
            content="Regulatory authorities have launched an investigation into TechCorp's "
                   "compliance practices. The company faces potential penalties if violations "
                   "are confirmed. This development has raised concerns among investors.",
            sentiment="neutral"
        ),
        NewsArticle(
            title="TechCorp Launches AI-Powered Platform",
            source="Tech Daily",
            url="https://example.com/article3",
            published_date=datetime(2024, 1, 5),
            content="TechCorp successfully launched its new AI-powered platform, receiving "
                   "positive feedback from early adopters. The innovation is expected to "
                   "strengthen the company's competitive position in the market.",
            sentiment="neutral"
        ),
        NewsArticle(
            title="TechCorp Announces Strategic Partnership",
            source="Business Wire",
            url="https://example.com/article4",
            published_date=datetime(2024, 1, 3),
            content="TechCorp entered into a strategic partnership with a leading global "
                   "technology firm. The collaboration aims to accelerate product development "
                   "and expand market reach.",
            sentiment="neutral"
        )
    ]
    
    # Initialize SentimentAnalyzer
    # Note: Set OPENAI_API_KEY environment variable to use OpenAI
    # Otherwise, it will use rule-based classification
    openai_key = os.getenv("OPENAI_API_KEY")
    analyzer = SentimentAnalyzer(openai_api_key=openai_key)
    
    print(f"\nAnalyzing {len(sample_articles)} news articles...")
    print(f"Using {'OpenAI' if openai_key else 'rule-based'} sentiment classification\n")
    
    # Analyze sentiment
    sentiment_score = analyzer.analyze_news_sentiment(sample_articles)
    
    # Display results
    print("\n" + "=" * 80)
    print("SENTIMENT ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\nOverall Sentiment Score: {sentiment_score.overall:.2f} (range: -1 to 1)")
    print(f"  - Positive articles: {sentiment_score.positive_count}")
    print(f"  - Neutral articles: {sentiment_score.neutral_count}")
    print(f"  - Negative articles: {sentiment_score.negative_count}")
    
    print("\nKey Themes:")
    for i, theme in enumerate(sentiment_score.key_themes, 1):
        print(f"  {i}. {theme}")
    
    print("\n" + "-" * 80)
    print("INDIVIDUAL ARTICLE SENTIMENTS")
    print("-" * 80)
    
    for i, article in enumerate(sample_articles, 1):
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Date: {article.published_date.strftime('%Y-%m-%d')}")
        print(f"   Sentiment: {article.sentiment.upper()}")
        print(f"   URL: {article.url}")
    
    # Extract key events
    print("\n" + "=" * 80)
    print("KEY EVENTS EXTRACTION")
    print("=" * 80)
    
    key_events = analyzer.extract_key_events(sample_articles)
    
    print(f"\nExtracted {len(key_events)} key events:\n")
    
    for i, event in enumerate(key_events, 1):
        print(f"{i}. {event['event']}")
        print(f"   Date: {event['date'].strftime('%Y-%m-%d')}")
        print(f"   Sentiment: {event['sentiment'].upper()}")
        print(f"   Source: {event['source']}")
        print()
    
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


def demo_with_webcrawler():
    """
    Demonstrate integration with WebCrawler.
    
    Note: This requires valid API keys to work.
    """
    print("\n" + "=" * 80)
    print("WebCrawler + SentimentAnalyzer Integration Demo")
    print("=" * 80)
    
    # Get API keys from environment
    news_api_key = os.getenv("NEWS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not news_api_key:
        print("\nSkipping WebCrawler demo - NEWS_API_KEY not set")
        print("Set NEWS_API_KEY environment variable to enable this demo")
        return
    
    # Initialize components
    crawler = WebCrawler(news_api_key=news_api_key)
    analyzer = SentimentAnalyzer(openai_api_key=openai_api_key)
    
    # Fetch news articles
    company_name = "Reliance Industries"
    print(f"\nFetching news articles for: {company_name}")
    
    articles = crawler.search_company_news(company_name, days_back=30)
    
    if not articles:
        print("No articles found")
        return
    
    print(f"Found {len(articles)} articles")
    
    # Analyze sentiment
    print("\nAnalyzing sentiment...")
    sentiment_score = analyzer.analyze_news_sentiment(articles)
    
    print(f"\nOverall Sentiment: {sentiment_score.overall:.2f}")
    print(f"Positive: {sentiment_score.positive_count}, "
          f"Neutral: {sentiment_score.neutral_count}, "
          f"Negative: {sentiment_score.negative_count}")
    
    print("\nKey Themes:")
    for theme in sentiment_score.key_themes:
        print(f"  - {theme}")
    
    # Extract key events
    print("\nExtracting key events...")
    key_events = analyzer.extract_key_events(articles)
    
    print(f"\nTop {min(5, len(key_events))} Key Events:")
    for i, event in enumerate(key_events[:5], 1):
        print(f"\n{i}. {event['event']}")
        print(f"   Date: {event['date'].strftime('%Y-%m-%d')}")
        print(f"   Sentiment: {event['sentiment']}")


if __name__ == "__main__":
    # Run basic demo with sample data
    demo_sentiment_analysis()
    
    # Optionally run WebCrawler integration demo
    # Uncomment the line below if you have API keys configured
    # demo_with_webcrawler()
