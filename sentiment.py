import feedparser
import os
from groq import Groq

def get_news_headlines(ticker_name: str, max_items: int = 10) -> list:
    try:
        query = ticker_name.replace(" ", "+") + "+stock"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        headlines = [entry.title for entry in feed.entries[:max_items]]
        return headlines if headlines else ["No news found"]
    except:
        return ["No news found"]

def analyze_sentiment(ticker_name: str) -> dict:
    """
    Use Groq LLM for sentiment instead of FinBERT.
    Much faster, no 1.3GB model download needed.
    """
    headlines = get_news_headlines(ticker_name)
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "sentiment_risk_score": 50.0,
                "avg_sentiment": 0.0,
                "headlines_analyzed": len(headlines),
                "sample_headline": headlines[0] if headlines else "N/A"
            }
        
        client = Groq(api_key=api_key)
        headlines_text = "\n".join(f"- {h}" for h in headlines[:10])
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Analyze the sentiment of these financial news headlines about a stock.
Headlines:
{headlines_text}

Reply with ONLY a JSON object like this:
{{"score": 45, "sentiment": "neutral"}}

Where score is 0-100 (0=very positive/low risk, 50=neutral, 100=very negative/high risk).
No explanation, just the JSON."""
            }]
        )
        
        import json
        text = response.choices[0].message.content.strip()
        # Clean up response
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        score = float(data.get("score", 50))
        
        return {
            "sentiment_risk_score": round(score, 2),
            "avg_sentiment": round((50 - score) / 50, 4),
            "headlines_analyzed": len(headlines),
            "sample_headline": headlines[0] if headlines else "N/A"
        }
    except:
        return {
            "sentiment_risk_score": 50.0,
            "avg_sentiment": 0.0,
            "headlines_analyzed": len(headlines),
            "sample_headline": headlines[0] if headlines else "N/A"
        }