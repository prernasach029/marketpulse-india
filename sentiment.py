from transformers import pipeline
from scraper import get_news_headlines

def analyze_sentiment(ticker_name: str) -> dict:
    """
    Run FinBERT on news headlines and return sentiment score.
    
    Returns:
        dict with score (0-100), label, and raw results
    """
    print("Loading FinBERT model...")
    pipe = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        truncation=True
    )
    
    headlines = get_news_headlines(ticker_name)
    results = pipe(headlines)
    
    # Convert to numeric score
    score_map = {"positive": 1, "neutral": 0, "negative": -1}
    scores = [score_map.get(r["label"], 0) * r["score"] for r in results]
    avg = sum(scores) / len(scores)
    
    # Normalize to 0-100 (avg ranges from -1 to +1)
    # Higher score = more negative sentiment = higher risk
    risk_score = round((1 - avg) / 2 * 100, 2)
    
    return {
        "sentiment_risk_score": risk_score,
        "avg_sentiment": round(avg, 4),
        "headlines_analyzed": len(headlines),
        "sample_headline": headlines[0]
    }


if __name__ == "__main__":
    result = analyze_sentiment("Reliance Industries")
    print("\n--- Sentiment Results ---")
    for k, v in result.items():
        print(f"{k}: {v}")