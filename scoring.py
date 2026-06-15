def compute_composite_score(
    var_99: float,
    es_99: float,
    regime: str,
    sentiment_risk_score: float
) -> dict:
    """
    Combine EVT, HMM, and FinBERT into a composite risk score.
    
    Args:
        var_99: 99% VaR in % (from risk.py)
        es_99: 99% ES in % (from risk.py)
        regime: "High Vol" or "Low Vol" (from regime.py)
        sentiment_risk_score: 0-100 (from sentiment.py)
    
    Returns:
        dict with composite_score, label, component breakdown
    """
    # --- EVT Score (0-100) ---
    # Typical NSE large-cap VaR range: 2% to 8%
    evt_score = min(max((var_99 - 2) / (8 - 2) * 100, 0), 100)
    
    # --- Regime Score (0 or 100) ---
    regime_score = 75 if regime == "High Vol" else 25
    
    # --- Sentiment Score already 0-100 ---
    sent_score = min(max(sentiment_risk_score, 0), 100)
    
    # --- Weighted Composite ---
    # EVT carries most weight as it's statistically grounded
    composite = (
        0.50 * evt_score +
        0.30 * regime_score +
        0.20 * sent_score
    )
    composite = round(composite, 2)
    
    # --- Label ---
    if composite >= 65:
        label = "🔴 High Risk"
    elif composite >= 35:
        label = "🟡 Moderate Risk"
    else:
        label = "🟢 Low Risk"
    
    return {
        "composite_score": composite,
        "label": label,
        "evt_score": round(evt_score, 2),
        "regime_score": regime_score,
        "sentiment_score": round(sent_score, 2)
    }


if __name__ == "__main__":
    # Test with Reliance values from our previous runs
    result = compute_composite_score(
        var_99=3.6034,
        es_99=4.0998,
        regime="Low Vol",
        sentiment_risk_score=51.87
    )
    print("\n--- Composite Risk Score ---")
    for k, v in result.items():
        print(f"{k}: {v}")