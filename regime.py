import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
import warnings
warnings.filterwarnings("ignore")

def detect_regimes(log_returns: pd.Series, n_states: int = 2):
    returns = log_returns.dropna()
    
    # Only use absolute returns as single feature — simpler and more stable
    features = np.abs(returns.values).reshape(-1, 1)
    
    model = GaussianHMM(
        n_components=n_states,
        covariance_type="diag",
        n_iter=10000,
        random_state=0
    )
    model.fit(features)
    hidden_states = model.predict(features)
    
    # High vol = state with higher mean absolute return
    means = [features[hidden_states == i].mean() for i in range(n_states)]
    high_vol_state = int(np.argmax(means))
    
    df_out = pd.DataFrame({
        "log_return": returns.values,
        "regime_id": hidden_states,
        "regime": ["High Vol" if s == high_vol_state else "Low Vol"
                   for s in hidden_states]
    }, index=returns.index)
    
    return df_out, model


if __name__ == "__main__":
    from data.fetcher import fetch_stock_data, compute_returns
    df = fetch_stock_data("RELIANCE.NS", period="2y")
    df = compute_returns(df)
    result, model = detect_regimes(df["log_return"])
    print("\n--- Regime Detection Results ---")
    print(result["regime"].value_counts())
    print(f"\nLast 5 days:\n{result[['log_return', 'regime']].tail()}")