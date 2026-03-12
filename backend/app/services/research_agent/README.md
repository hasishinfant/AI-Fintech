# Research Agent Component

The Research Agent component is responsible for automated web intelligence gathering and analysis. It consists of two main classes:

## Components

### 1. WebCrawler

Handles external data source integration and web research.

**Features:**
- Search company news from news APIs
- Fetch MCA (Ministry of Corporate Affairs) filings
- Search e-Courts database for litigation
- Retrieve RBI notifications
- Automatic retry logic with exponential backoff
- Graceful error handling

**Usage:**
```python
from app.services.research_agent import WebCrawler

crawler = WebCrawler(
    news_api_key="your_news_api_key",
    mca_api_key="your_mca_api_key"
)

# Search for company news
articles = crawler.search_company_news("Company Name", days_back=90)

# Fetch MCA filings
mca_data = crawler.fetch_mca_filings("U12345AB2020PTC123456")

# Search for litigation
legal_cases = crawler.search_ecourts("Company Name", promoter_names=["John Doe"])
```

### 2. SentimentAnalyzer

Analyzes sentiment and extracts key events from news articles using NLP models.

**Features:**
- Sentiment classification (positive, neutral, negative)
- Key theme extraction
- Key event extraction
- Integration with OpenAI GPT models
- Fallback to rule-based classification
- Aggregated sentiment scoring

**Usage:**
```python
from app.services.research_agent import SentimentAnalyzer

# Initialize with OpenAI (optional)
analyzer = SentimentAnalyzer(openai_api_key="your_openai_key")

# Or use rule-based classification
analyzer = SentimentAnalyzer()

# Analyze sentiment of articles
sentiment_score = analyzer.analyze_news_sentiment(articles)

print(f"Overall sentiment: {sentiment_score.overall}")
print(f"Positive: {sentiment_score.positive_count}")
print(f"Negative: {sentiment_score.negative_count}")
print(f"Key themes: {sentiment_score.key_themes}")

# Extract key events
key_events = analyzer.extract_key_events(articles)

for event in key_events:
    print(f"{event['event']} - {event['sentiment']}")
```

## Integration Example

Complete workflow combining WebCrawler and SentimentAnalyzer:

```python
from app.services.research_agent import WebCrawler, SentimentAnalyzer

# Initialize components
crawler = WebCrawler(news_api_key="your_key")
analyzer = SentimentAnalyzer(openai_api_key="your_key")

# Fetch news articles
company_name = "Reliance Industries"
articles = crawler.search_company_news(company_name, days_back=90)

# Analyze sentiment
sentiment_score = analyzer.analyze_news_sentiment(articles)

# Extract key events
key_events = analyzer.extract_key_events(articles)

# Use results in credit assessment
print(f"Company: {company_name}")
print(f"Overall sentiment: {sentiment_score.overall:.2f}")
print(f"Key themes: {', '.join(sentiment_score.key_themes)}")
print(f"Recent events: {len(key_events)}")
```

## Sentiment Classification

### OpenAI-based Classification

When an OpenAI API key is provided, the analyzer uses GPT models for:
- More accurate sentiment classification
- Better theme extraction
- Detailed event extraction

### Rule-based Classification

When no API key is provided, the analyzer uses keyword-based rules:

**Positive keywords:** growth, profit, success, expansion, award, achievement, innovation, partnership, etc.

**Negative keywords:** loss, decline, lawsuit, fraud, scandal, investigation, penalty, default, etc.

**Neutral:** When positive and negative scores are equal or text has no strong indicators

## Sentiment Score

The overall sentiment score ranges from -1 to 1:
- **1.0**: All articles are positive
- **0.0**: Equal positive and negative articles
- **-1.0**: All articles are negative

Formula: `(positive_count - negative_count) / total_articles`

## Key Themes

Themes are automatically extracted and categorized:
- Financial Performance
- Legal Issues
- Regulatory
- Operations
- Management
- Market
- Technology
- Expansion

## Key Events

Events are extracted with:
- Event description
- Date
- Source URL
- Sentiment classification

Events are sorted by date (most recent first) and limited to top 20.

## Error Handling

Both components implement graceful degradation:
- API failures return empty results instead of crashing
- Missing API keys trigger warnings and use fallback methods
- Network errors are logged and handled gracefully
- Invalid responses are validated and defaulted

## Requirements

**Dependencies:**
- `openai` - For GPT-based sentiment analysis
- `requests` - For HTTP requests
- `beautifulsoup4` - For web scraping (future use)

**Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API key (optional)
- `NEWS_API_KEY` - News API key (optional)
- `MCA_API_KEY` - MCA API key (optional)

## Testing

Run unit tests:
```bash
pytest tests/test_web_crawler.py -v
pytest tests/test_sentiment_analyzer.py -v
```

Run demo:
```bash
python examples/sentiment_analysis_demo.py
```

## Requirements Mapping

### SentimentAnalyzer
- **Requirement 4.2**: Analyze news sentiment and classify as positive, neutral, or negative
- Implements `analyze_news_sentiment()` method
- Implements `extract_key_events()` method
- Integrates with OpenAI/Llama for advanced text analysis

### WebCrawler
- **Requirement 2.1**: Retrieve MCA filings
- **Requirement 2.2**: Fetch news articles
- **Requirement 2.3**: Search legal records
- **Requirement 4.1**: Search news APIs
- **Requirement 4.3**: Verify MCA compliance
- **Requirement 4.4**: Search e-Courts database
- **Requirement 4.5**: Retrieve RBI notifications
- **Requirement 4.6**: Provide source URLs and timestamps

## Future Enhancements

1. **Local LLM Support**: Add support for local Llama models via llama-cpp-python
2. **Caching**: Implement caching for API responses to reduce costs
3. **Batch Processing**: Add batch processing for large article sets
4. **Advanced NLP**: Integrate more sophisticated NLP models for better accuracy
5. **Multi-language**: Support sentiment analysis in multiple languages
6. **Entity Recognition**: Extract company names, people, and locations from articles
7. **Trend Analysis**: Track sentiment trends over time
