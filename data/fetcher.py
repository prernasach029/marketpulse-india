import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for an NSE stock.
    
    Args:
        ticker: NSE ticker with .NS suffix e.g. "RELIANCE.NS"
        period: how far back to pull — "1y", "2y", "5y"
    
    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    
    if df.empty:
        raise ValueError(f"No data found for {ticker}. Check the ticker symbol.")
    
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index = pd.to_datetime(df.index)
    df.dropna(inplace=True)
    
    print(f"✅ Fetched {len(df)} rows for {ticker}")
    return df


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily log returns column — this is what EVT and HMM will consume."""
    df = df.copy()
    df["log_return"] = (df["Close"] / df["Close"].shift(1)).apply(lambda x: __import__("numpy").log(x))
    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    # Quick test — run: python data/fetcher.py
    ticker = "RELIANCE.NS"
    df = fetch_stock_data(ticker, period="2y")
    df = compute_returns(df)
    print(df.tail())
    print(f"\nShape: {df.shape}")