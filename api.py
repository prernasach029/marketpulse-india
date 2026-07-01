from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, ".")

from data.fetcher import fetch_stock_data, compute_returns
from risk import compute_tail_risk
from regime import detect_regimes
from sentiment import analyze_sentiment
from scoring import compute_composite_score

app = FastAPI(title="MarketPulse India API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "https://marketpulse-react.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    ticker: str
    company: str
    period: str = "2y"


class ChatRequest(BaseModel):
    message: str
    analysis_data: dict = {}
    history: list = []


class InsightsRequest(BaseModel):
    company: str
    ticker: str
    var_99: float
    es_99: float
    regime: str
    sentiment_score: float
    composite_score: float
    label: str
    headline: str


@app.get("/")
def root():
    return {"status": "MarketPulse India API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        df = fetch_stock_data(req.ticker, period=req.period)
        df = compute_returns(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch data for {req.ticker}")

    try:
        evt = compute_tail_risk(df["log_return"])
    except Exception as e:
        raise HTTPException(status_code=500, detail="EVT model error")

    try:
        regime_df, _ = detect_regimes(df["log_return"])
        current_regime = regime_df["regime"].iloc[-1]
        regime_counts = regime_df["regime"].value_counts().to_dict()
    except:
        current_regime = "Unknown"
        regime_counts = {}

    try:
        sent = analyze_sentiment(req.company)
    except:
        sent = {
            "sentiment_risk_score": 50.0,
            "avg_sentiment": 0.0,
            "headlines_analyzed": 0,
            "sample_headline": "N/A"
        }

    score = compute_composite_score(
        var_99=evt["VaR_99"],
        es_99=evt["ES_99"],
        regime=current_regime,
        sentiment_risk_score=sent["sentiment_risk_score"]
    )

    price_history = df["Close"].tail(60).reset_index()
    price_history.columns = ["date", "price"]
    price_history["date"] = price_history["date"].astype(str)

    forecast_data = []
    try:
        from statsmodels.tsa.arima.model import ARIMA
        import warnings
        import pandas as pd
        warnings.filterwarnings("ignore")
        prices = df["Close"].values
        model = ARIMA(prices, order=(5, 1, 0))
        fitted = model.fit()
        forecast = fitted.forecast(steps=30)
        last_date = df.index[-1]
        future_dates = pd.bdate_range(start=last_date, periods=31)[1:]
        forecast_data = [
            {
                "date": str(d)[:10],
                "price": round(float(p), 2),
                "lower": round(float(p * 0.97), 2),
                "upper": round(float(p * 1.03), 2)
            }
            for d, p in zip(future_dates, forecast)
        ]
    except:
        pass

    return {
        "ticker": req.ticker,
        "company": req.company,
        "var_99": evt["VaR_99"],
        "es_99": evt["ES_99"],
        "regime": current_regime,
        "regime_counts": regime_counts,
        "sentiment_score": sent["sentiment_risk_score"],
        "sample_headline": sent["sample_headline"],
        "composite_score": score["composite_score"],
        "label": score["label"],
        "evt_score": score["evt_score"],
        "regime_score": score["regime_score"],
        "sentiment_score_component": score["sentiment_score"],
        "price_history": price_history.to_dict(orient="records"),
        "forecast": forecast_data,
        "current_price": round(float(df["Close"].iloc[-1]), 2)
    }


@app.get("/news")
def get_news(query: str = "NSE stock market", max_items: int = 12):
    try:
        import feedparser
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        query_encoded = query.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        news = []
        from email.utils import parsedate_to_datetime
        import pytz
        tz = pytz.timezone("Asia/Kolkata")
        for entry in feed.entries[:max_items]:
            title = entry.title
            source = "Unknown"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title, source = parts[0], parts[1]
            pub_time = ""
            try:
                dt = parsedate_to_datetime(entry.published)
                dt_local = dt.astimezone(tz)
                pub_time = dt_local.strftime("%d %b %Y, %I:%M %p IST")
            except:
                pass
            news.append({
                "title": title,
                "source": source,
                "date": pub_time,
                "link": entry.link if hasattr(entry, "link") else ""
            })
        return {"news": news}
    except Exception as e:
        return {"news": []}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        data = req.analysis_data
        context = ""
        if data:
            context = (
                "User last analysis:\n"
                f"- Stock: {data.get('company')} ({data.get('ticker')})\n"
                f"- Risk Score: {data.get('composite_score')}/100 - {data.get('label')}\n"
                f"- Regime: {data.get('regime')}\n"
                f"- VaR: {data.get('var_99')}%\n"
            )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are MarketPulse AI, a professional investment assistant for Indian retail investors.\n"
                    f"{context}\n"
                    "Be concise and clear. Plain language only.\n"
                    "Always note this is not financial advice."
                )
            }
        ]
        for msg in req.history[-8:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": req.message})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=600,
            messages=messages
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insights")
def get_insights(req: InsightsRequest):
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = (
            f"You are a friendly financial advisor for Indian retail investors.\n\n"
            f"Data for {req.company} ({req.ticker}):\n"
            f"- 99% VaR: {req.var_99}%\n"
            f"- 99% ES: {req.es_99}%\n"
            f"- Volatility Regime: {req.regime}\n"
            f"- Sentiment Risk: {req.sentiment_score}/100\n"
            f"- Composite Risk Score: {req.composite_score}/100 ({req.label})\n"
            f"- Latest News: {req.headline}\n\n"
            "Respond in this exact structure:\n\n"
            "**What this means**\n"
            "[2-3 plain English sentences]\n\n"
            "**Bull Case**\n"
            "[2-3 reasons to consider buying/holding]\n\n"
            "**Bear Case**\n"
            "[2-3 reasons to be cautious]\n\n"
            "**Signal**\n"
            "[Buy / Hold / Sell - one sentence reason]\n\n"
            "**Portfolio Tip**\n"
            "[One actionable suggestion]\n\n"
            "Keep it concise and jargon-free."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"insights": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/earnings")
def get_earnings(ticker: str, company: str = ""):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        income = stock.quarterly_income_stmt

        revenue_trend = []
        profit_trend = []
        eps_history = []

        if income is not None and not income.empty:
            if "Total Revenue" in income.index:
                rev = income.loc["Total Revenue"].dropna().sort_index()
                revenue_trend = [
                    {"quarter": str(d)[:10], "revenue": round(v / 1e7, 2)}
                    for d, v in zip(rev.index, rev.values)
                ]

            profit_keys = ["Net Income", "Net Income Common Stockholders"]
            profit_key = next((k for k in profit_keys if k in income.index), None)
            if profit_key:
                prof = income.loc[profit_key].dropna().sort_index()
                profit_trend = [
                    {"quarter": str(d)[:10], "profit": round(v / 1e7, 2)}
                    for d, v in zip(prof.index, prof.values)
                ]

        try:
            earnings = stock.earnings_history
            if earnings is not None and not earnings.empty:
                eps = earnings[["epsEstimate", "epsActual"]].dropna().tail(8)
                eps_history = [
                    {"date": str(i)[:10], "estimate": row["epsEstimate"], "actual": row["epsActual"]}
                    for i, row in eps.iterrows()
                ]
        except:
            pass

        ai_summary = ""
        try:
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            pe = info.get("trailingPE", "N/A")
            eps_val = info.get("trailingEps", "N/A")
            margin = info.get("profitMargins", "N/A")
            rev_val = info.get("totalRevenue", "N/A")
            prompt = (
                f"You are a financial analyst helping Indian retail investors understand earnings.\n\n"
                f"Company: {company} ({ticker})\n"
                f"P/E Ratio: {pe}\n"
                f"EPS (TTM): {eps_val}\n"
                f"Profit Margin: {margin}\n"
                f"Total Revenue: {rev_val}\n\n"
                "Give a concise earnings analysis with: Earnings Health, Strengths, Concerns, Valuation, Bottom Line. Simple language."
            )
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            ai_summary = res.choices[0].message.content
        except:
            pass

        return {
            "pe": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
            "eps": info.get("trailingEps"),
            "revenue": round(info.get("totalRevenue", 0) / 1e7, 0) if info.get("totalRevenue") else None,
            "margin": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
            "revenue_trend": revenue_trend,
            "profit_trend": profit_trend,
            "eps_history": eps_history,
            "ai_summary": ai_summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        @app.get("/stocks")
def get_stocks():
    try:
        import requests
        import pandas as pd
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {"User-Agent": "Mozilla/5.0"}
        df = pd.read_csv(url, storage_options={"headers": headers})
        stocks = {}
        for _, row in df.iterrows():
            name = str(row["NAME OF COMPANY"]).strip().title()
            ticker = str(row["SYMBOL"]).strip() + ".NS"
            stocks[name] = ticker
        return {"stocks": stocks}
    except:
        # Fallback to hardcoded list
        return {"stocks": {
            "Reliance Industries": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "HDFC Bank": "HDFCBANK.NS",
            "Infosys": "INFY.NS",
        }}