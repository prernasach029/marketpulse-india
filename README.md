# MarketPulse India 📈

> NSE stock risk analysis for Indian retail investors — powered by EVT, HMM, FinBERT, and LLM-based AI insights.

🔗 **Live App:** [marketpulse-india.streamlit.app](https://marketpulse-india.streamlit.app)

---

## What is this?

MarketPulse India is a multi-model financial risk dashboard that helps retail investors understand the risk profile of NSE-listed stocks. It combines three statistical/ML engines with an AI assistant to give both quantitative metrics and plain-English explanations.

Built as part of an MSc Statistics & Data Science project at SVKM's NMIMS Mumbai.

---

## Features

### Stock Analysis
- **Extreme Value Theory (EVT/GPD)** — Peaks Over Threshold method to estimate 99% Value at Risk (VaR) and Expected Shortfall (ES)
- **Hidden Markov Model (HMM)** — Volatility regime detection (High Vol / Low Vol) using Gaussian HMM
- **FinBERT Sentiment** — Financial news sentiment scoring using HuggingFace's `ProsusAI/finbert` model
- **Composite Risk Score** — Weighted combination of EVT, HMM, and sentiment signals into a 0–100 score with Red/Amber/Green label
- **30-Day Price Forecast** — ARIMA-based price prediction with confidence bands

### News Feed
- Real-time financial news from multiple sources via Google News RSS
- Timezone-aware timestamps (IST, GST, GMT, EST, PST, SGT)
- Language filter (English / Hindi)

### Portfolio Tracker
- Analyze up to 5 NSE stocks simultaneously
- Ranked risk table sorted from lowest to highest risk
- Portfolio health score with AI rebalancing advice

### AI Assistant
- Context-aware chatbot powered by Groq's Llama 3.3 70B
- Knows your last stock analysis and answers follow-up questions
- Bull/Bear case analysis, Buy/Hold/Sell signal, Portfolio tips

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Tail Risk | SciPy (GPD/EVT) |
| Regime Detection | hmmlearn (Gaussian HMM) |
| Sentiment | HuggingFace Transformers (FinBERT) |
| Forecasting | statsmodels (ARIMA) |
| AI Insights | Groq API (Llama 3.3 70B) |
| Data | yfinance (NSE via Yahoo Finance) |
| News | feedparser (Google News RSS) |

---

## Project Structure
marketpulse/

├── app.py          # Main Streamlit app (all pages)

├── risk.py         # EVT/GPD tail risk engine

├── regime.py       # HMM volatility regime detection

├── sentiment.py    # FinBERT news sentiment scorer

├── scraper.py      # Google News RSS scraper

├── scoring.py      # Composite risk score calculator

├── data/

│   └── fetcher.py  # yfinance data pipeline

└── requirements.txt
---

## How It Works

### 1. Tail Risk (EVT/GPD)
Uses the **Peaks Over Threshold (POT)** method from Extreme Value Theory. Daily log returns are computed, losses beyond the 95th percentile threshold are fitted to a **Generalized Pareto Distribution (GPD)**, and 99% VaR and Expected Shortfall are derived analytically.

### 2. Volatility Regime (HMM)
A **2-state Gaussian HMM** is fitted to absolute daily returns. The model learns two hidden states — High Volatility and Low Volatility — and labels each trading day accordingly. The current regime is used as a risk signal.

### 3. News Sentiment (FinBERT)
Headlines are scraped from Google News RSS for the given company. Each headline is classified as **positive / neutral / negative** by FinBERT, weighted by confidence score, and aggregated into a 0–100 sentiment risk score.

### 4. Composite Score
Score = 0.50 × EVT_score + 0.30 × Regime_score + 0.20 × Sentiment_score
- **Green (< 35):** Lower risk
- **Amber (35–65):** Moderate risk  
- **Red (> 65):** High risk

---

## Setup & Installation

```bash
# Clone the repo
git clone https://github.com/prernasach029/marketpulse-india.git
cd marketpulse-india

# Create conda environment
conda create -n marketpulse python=3.11
conda activate marketpulse

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "GROQ_API_KEY=your-key-here" > .env

# Run the app
streamlit run app.py
```

---

## API Keys Required

| Key | Where to get | Free? |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Yes |

---

## Example Tickers

| Company | Ticker |
|---|---|
| Reliance Industries | `RELIANCE.NS` |
| TCS | `TCS.NS` |
| HDFC Bank | `HDFCBANK.NS` |
| Infosys | `INFY.NS` |
| Wipro | `WIPRO.NS` |

---

## Disclaimer

This app is for **educational purposes only**. Nothing here constitutes financial advice. Always consult a SEBI-registered investment advisor before making investment decisions.

---

## Author

**Prerna Sachdeva**  
MSc Statistics & Data Science, SVKM's NMIMS Mumbai  
[GitHub](https://github.com/prernasach029)
