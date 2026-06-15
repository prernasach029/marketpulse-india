import numpy as np
import pandas as pd
from scipy.stats import genpareto

def compute_tail_risk(log_returns: pd.Series, threshold_pct: float = 0.05) -> dict:
    """
    Peaks Over Threshold (POT) method using GPD.
    
    Args:
        log_returns: daily log returns series
        threshold_pct: top X% of losses to use as tail (default 5%)
    
    Returns:
        dict with VaR_99, ES_99, threshold, n_exceedances
    """
    # Work with losses (flip sign)
    losses = -log_returns.dropna()
    
    # Set threshold at 95th percentile of losses
    u = np.quantile(losses, 1 - threshold_pct)
    
    # Exceedances — losses beyond the threshold
    exceedances = losses[losses > u] - u
    n_exceed = len(exceedances)
    n_total = len(losses)
    
    if n_exceed < 10:
        raise ValueError("Too few exceedances. Try a lower threshold_pct.")
    
    # Fit GPD to exceedances
    c, loc, scale = genpareto.fit(exceedances, floc=0)
    
    # 99% VaR using GPD formula
    p = 0.99
    VaR_99 = u + (scale / c) * ((( n_total / n_exceed) * (1 - p)) ** (-c) - 1)
    
    # 99% Expected Shortfall
    ES_99 = (VaR_99 + scale - c * u) / (1 - c)
    
    return {
        "VaR_99": round(VaR_99 * 100, 4),   # in %
        "ES_99": round(ES_99 * 100, 4),       # in %
        "threshold": round(u * 100, 4),
        "n_exceedances": n_exceed,
        "gpd_shape": round(c, 4),
        "gpd_scale": round(scale, 4)
    }


if __name__ == "__main__":
    from data.fetcher import fetch_stock_data, compute_returns
    df = fetch_stock_data("RELIANCE.NS", period="2y")
    df = compute_returns(df)
    result = compute_tail_risk(df["log_return"])
    print("\n--- Tail Risk Results ---")
    for k, v in result.items():
        print(f"{k}: {v}")