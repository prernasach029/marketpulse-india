
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import feedparser

def get_news_headlines(ticker_name: str, max_items: int = 10) -> list:
    query = ticker_name.replace(" ", "+") + "+stock"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:max_items]]
    if not headlines:
        return ["No news found"]
    return headlines

def get_news_headlines(ticker_name: str, max_items: int = 10) -> list:
    """
    Scrape financial news headlines from Google News RSS.
    
    Args:
        ticker_name: company name e.g. "Reliance Industries"
        max_items: number of headlines to fetch
    
    Returns:
        list of headline strings
    """
    query = ticker_name.replace(" ", "+") + "+stock"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:max_items]]
    
    if not headlines:
        return ["No news found"]
    
    return headlines


if __name__ == "__main__":
    headlines = get_news_headlines("Reliance Industries")
    for h in headlines:
        print(h)