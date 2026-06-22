import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sys
import os
from stocks_list import NSE_STOCKS, TICKER_TO_COMPANY, fetch_all_nse_stocks
from dotenv import load_dotenv
from groq import Groq
import feedparser
from email.utils import parsedate_to_datetime
import pytz

load_dotenv()
sys.path.insert(0, ".")

from data.fetcher import fetch_stock_data, compute_returns
from risk import compute_tail_risk
from regime import detect_regimes
from sentiment import analyze_sentiment
from scoring import compute_composite_score

st.set_page_config(
    page_title="MarketPulse India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

from styles import load_css
st.markdown(load_css(),unsafe_allow_html=True)
st.markdown('<meta name="google-site-verification" content="bmHLKb9zYSASfbGDTwVeuGIOa5UmxsHatc6299TxVRw" />', unsafe_allow_html=True)
st.markdown("""
<meta name="description" content="MarketPulse India - NSE stock risk analysis using EVT, HMM, FinBERT and AI insights for Indian retail investors.">
<meta name="keywords" content="MarketPulse India, NSE stock analysis, Indian stock risk, EVT, HMM, FinBERT">
""", unsafe_allow_html=True)
st.sidebar.image("assets/marketpulse-logo-v2.svg",width=180)

st.markdown("""
<style>
    div[data-testid="stSidebarNav"] { display: none; }

    .feature-card {
        background: var(--panel);
        border: 1px solid var(--line-soft);
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 14px;
    }
    .feature-title {
        font-size: 1em;
        font-weight: 600;
        margin-bottom: 6px;
        color: var(--txt);
        font-family: var(--sans);
    }
    .feature-desc {
        color: var(--txt-2);
        font-size: 0.87em;
        line-height: 1.6;
    }
    .tag {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 0.72em;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 4px;
        margin-top: 6px;
        font-family: var(--mono);
        border: 1px solid var(--accent-line);
    }
    .bull-box {
        background: var(--up-soft);
        border-left: 3px solid var(--up);
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 0.91em;
        line-height: 1.7;
        color: var(--txt);
    }
    .bear-box {
        background: var(--down-soft);
        border-left: 3px solid var(--down);
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 0.91em;
        line-height: 1.7;
        color: var(--txt);
    }
    .signal-box {
        background: var(--panel);
        border: 1px solid var(--accent-line);
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 0.93em;
        color: var(--txt);
        font-family: var(--mono);
    }
    .tip-box {
        background: var(--amber-soft);
        border-left: 3px solid var(--amber);
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 0.91em;
        line-height: 1.7;
        color: var(--txt);
    }
    .summary-box {
        background: var(--panel);
        border: 1px solid var(--line-soft);
        padding: 16px 20px;
        border-radius: 8px;
        margin: 8px 0;
        line-height: 1.7;
        font-size: 0.93em;
        color: var(--txt-2);
    }
    .news-card {
        background: var(--panel);
        border: 1px solid var(--line-soft);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .news-title {
        font-size: 0.95em;
        font-weight: 500;
        line-height: 1.5;
        margin-bottom: 6px;
        color: var(--txt);
    }
    .news-meta { font-size: 0.77em; color: var(--txt-3); }
    .news-source { color: var(--txt-2); font-weight: 500; font-family: var(--mono); }
    .chat-header {
        background: var(--panel);
        border: 1px solid var(--line-soft);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 16px;
        font-size: 0.9em;
        color: var(--txt-2);
        font-family: var(--mono);
    }
    [data-testid="stChatMessage"] {
        background: var(--panel) !important;
        border-radius: 8px !important;
        border: 1px solid var(--line-soft) !important;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session state ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "home_expanded" not in st.session_state:
    st.session_state.home_expanded = True
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = {}
if "timezone" not in st.session_state:
    st.session_state.timezone = "India (IST)"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "all_stocks" not in st.session_state:
    st.session_state.all_stocks = fetch_all_nse_stocks()
ALL_STOCKS = st.session_state.all_stocks

# --- Sidebar ---
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand-block">
        <div class="brand-mark">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 17l5-6 4 4 6-8"/><path d="M21 7v4h-4"/>
            </svg>
        </div>
        <div>
            <div class="brand-name">MarketPulse</div>
            <div class="brand-sub">INDIA · NSE TERMINAL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Home</div>', unsafe_allow_html=True)
    with st.expander("Navigate", expanded=st.session_state.home_expanded):
        if st.button("Overview", use_container_width=True, key="nav_home"):
            st.session_state.page = "home"
            st.session_state.home_expanded = True
            st.rerun()
        if st.button("Stock Analysis", use_container_width=True, key="nav_stocks"):
            st.session_state.page = "stocks"
            st.session_state.home_expanded = True
            st.rerun()
        if st.button("News Feed", use_container_width=True, key="nav_news"):
            st.session_state.page = "news"
            st.session_state.home_expanded = True
            st.rerun()
        if st.button("Portfolio", use_container_width=True, key="nav_portfolio"):
            st.session_state.page = "portfolio"
            st.session_state.home_expanded = True
            st.rerun()
        if st.button("Earnings Analysis", use_container_width=True, key="nav_earnings"):
            st.session_state.page = "earnings"
            st.session_state.home_expanded = True
            st.rerun()

    st.markdown('<div class="nav-section">Assistant</div>', unsafe_allow_html=True)
    if st.button("Chatbot", use_container_width=True, key="nav_chat"):
        st.session_state.page = "chatbot"
        st.session_state.home_expanded = False
        st.rerun()

   

# --- Constants ---
TIMEZONES = {
    "India (IST)": "Asia/Kolkata",
    "UAE (GST)": "Asia/Dubai",
    "UK (GMT/BST)": "Europe/London",
    "US Eastern": "America/New_York",
    "US Pacific": "America/Los_Angeles",
    "Singapore": "Asia/Singapore",
}
LANGUAGES = {
    "English": ("en", "IN"),
    "Hindi": ("hi", "IN"),
}

def predict_prices(df, days=30):
    from statsmodels.tsa.arima.model import ARIMA
    import numpy as np
    import warnings
    warnings.filterwarnings("ignore")
    
    prices = df["Close"].values
    
    try:
        model = ARIMA(prices, order=(5, 1, 0))
        fitted = model.fit()
        forecast = fitted.forecast(steps=days)
        
        last_date = df.index[-1]
        import pandas as pd
        future_dates = pd.bdate_range(start=last_date, periods=days + 1)[1:]
        
        current_price = prices[-1]
        lower = forecast * 0.97
        upper = forecast * 1.03
        
        return {
            "dates": future_dates,
            "forecast": forecast,
            "lower": lower,
            "upper": upper,
            "current_price": round(float(current_price), 2),
            "predicted_end": round(float(forecast[-1]), 2),
            "change_pct": round((forecast[-1] - current_price) / current_price * 100, 2)
        }
    except:
        return None
# --- Helper functions ---
def get_live_watchlist():
    import yfinance as yf
    watchlist_tickers = {
        "Reliance Inds.": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Infosys": "INFY.NS",
        "Adani Ent.": "ADANIENT.NS",
        "Wipro": "WIPRO.NS",
    }
    rows = []
    for name, ticker in watchlist_tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                chg = ((curr - prev) / prev) * 100
                rows.append({
                    "name": name,
                    "ticker": ticker,
                    "price": f"{curr:,.2f}",
                    "chg": f"{chg:+.2f}%",
                    "up": chg >= 0,
                    "letter": name[0]
                })
        except:
            pass
    return rows
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key) if api_key else None


def get_news(query, max_items=12):
    lang_code, country_code = LANGUAGES.get(st.session_state.language, ("en", "IN"))
    query_encoded = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query_encoded}&hl={lang_code}-{country_code}&gl={country_code}&ceid={country_code}:{lang_code}"
    feed = feedparser.parse(url)
    tz_name = TIMEZONES.get(st.session_state.timezone, "Asia/Kolkata")
    results = []
    for entry in feed.entries[:max_items]:
        title = entry.title
        source = "Unknown"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title, source = parts[0], parts[1]
        pub_time = ""
        try:
            dt = parsedate_to_datetime(entry.published)
            tz = pytz.timezone(tz_name)
            dt_local = dt.astimezone(tz)
            pub_time = dt_local.strftime("%d %b %Y, %I:%M %p %Z")
        except:
            pass
        results.append({
            "title": title,
            "source": source,
            "date": pub_time,
            "link": entry.link if hasattr(entry, "link") else ""
        })
    return results


def parse_insights(raw_text):
    sections = {"summary": "", "bull": "", "bear": "", "signal": "", "tip": ""}
    current = "summary"
    for line in raw_text.split("\n"):
        l = line.lower()
        if "bull case" in l:
            current = "bull"
        elif "bear case" in l:
            current = "bear"
        elif "**signal**" in l or ("signal" in l and ("buy" in l or "hold" in l or "sell" in l)):
            current = "signal"
        elif "portfolio tip" in l:
            current = "tip"
        elif "what this means" in l:
            current = "summary"
        else:
            sections[current] += line + "\n"
    return sections


def get_ai_insights(company, ticker, var_99, es_99, regime, sentiment_score, composite_score, label, headlines):
    client = get_groq_client()
    if not client:
        return None
    headlines_text = "\n".join(f"- {h['title']}" for h in headlines[:5])
    prompt = f"""You are a friendly financial advisor for Indian retail investors.

Data for {company} ({ticker}):
- 99% VaR: {var_99}%
- 99% ES: {es_99}%
- Volatility Regime: {regime}
- Sentiment Risk: {sentiment_score}/100
- Composite Risk Score: {composite_score}/100 ({label})

Recent News:
{headlines_text}

Respond in this exact structure:

**What this means**
[2-3 plain English sentences]

**Bull Case**
[2-3 reasons to consider buying/holding]

**Bear Case**
[2-3 reasons to be cautious]

**Signal**
[Buy / Hold / Sell — one sentence reason]

**Portfolio Tip**
[One actionable suggestion]

Keep it concise and jargon-free."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def chat_response(user_message):
    client = get_groq_client()
    if not client:
        return "GROQ_API_KEY not found in .env file."
    data = st.session_state.analysis_data
    context = ""
    if data:
        context = f"""User's last analysis:
- Stock: {data.get('company')} ({data.get('ticker')})
- Risk Score: {data.get('composite_score')}/100 — {data.get('label')}
- Regime: {data.get('regime')}
- VaR: {data.get('var_99')}%
- Sentiment: {data.get('sentiment_score')}/100
"""
    messages = [
        {
            "role": "system",
            "content": f"""You are MarketPulse AI, a professional investment assistant for Indian retail investors.
{context}
Be concise and clear. Plain language only.
Always note this is not financial advice - suggest consulting a SEBI-registered advisor for major decisions."""
        }
    ]
    for msg in st.session_state.messages[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=messages
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────
if st.session_state.page == "home":
    with st.spinner("Loading live market data..."):
        watchlist = get_live_watchlist()

    rows_html = ""
    for r in watchlist:
        chg_class = "up" if r["up"] else "down"
        regime_color = "#16C77E" if not r["up"] else "#E0A33B"
        chip_class = "rc-g" if r["up"] else "rc-r"
        rows_html += f"""
        <tr>
            <td><div class="wl-name"><div class="wl-logo">{r["letter"]}</div>
            <div>{r["name"]}<div class="wl-tk">{r["ticker"]}</div></div></div></td>
            <td>&#8377;{r["price"]}</td>
            <td class="{chg_class}">{r["chg"]}</td>
            <td style="color:{regime_color}">{'Low Vol' if r['up'] else 'High Vol'}</td>
            <td><span class="risk-chip {chip_class}">{'&#8679; Up' if r['up'] else '&#8681; Down'}</span></td>
        </tr>"""

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
    :root {{
        --navy:#0A0F1E; --navy-2:#0E1426; --panel:#111932; --panel-2:#0D1424;
        --line:#1E2A48; --line-soft:#18223D; --accent:#2563EB;
        --accent-soft:rgba(37,99,235,.14); --accent-line:rgba(37,99,235,.45);
        --txt:#E7ECF6; --txt-2:#9AA6C2; --txt-3:#5E6C8C;
        --up:#16C77E; --up-soft:rgba(22,199,126,.12);
        --down:#F0455E; --down-soft:rgba(240,69,94,.12);
        --amber:#E0A33B; --amber-soft:rgba(224,163,59,.12);
        --mono:'IBM Plex Mono',ui-monospace,monospace;
        --sans:'Inter',system-ui,sans-serif;
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--navy);color:var(--txt);font-family:var(--sans);font-size:14px;-webkit-font-smoothing:antialiased;}}
    a{{color:inherit;text-decoration:none}}
    ::-webkit-scrollbar{{width:9px}};::-webkit-scrollbar-thumb{{background:#1c2742;border-radius:6px}}
    .up{{color:var(--up)}}.down{{color:var(--down)}}
    .pill{{padding:2px 7px;border-radius:4px;font-size:11px}}
    .pill.up{{background:var(--up-soft)}}.pill.down{{background:var(--down-soft)}}

    .tickerbar{{height:34px;background:var(--panel-2);border-bottom:1px solid var(--line);display:flex;align-items:center;overflow:hidden;}}
    .tick-label{{flex:none;font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--txt-3);padding:0 16px;border-right:1px solid var(--line);height:100%;display:flex;align-items:center;background:var(--navy-2);}}
    .tick-label .dot{{width:6px;height:6px;border-radius:50%;background:var(--up);margin-right:8px;box-shadow:0 0 6px var(--up);display:inline-block;animation:pulse 2s infinite;}}
    @keyframes pulse{{50%{{opacity:.4}}}}
    .tick-track{{display:flex;align-items:center;white-space:nowrap;animation:scroll 38s linear infinite;flex:none;}}
    .tickerbar:hover .tick-track{{animation-play-state:paused}}
    @keyframes scroll{{to{{transform:translateX(-50%)}}}}
    .tick{{display:inline-flex;align-items:baseline;gap:8px;padding:0 20px;font-size:12px;}}
    .tick .sym{{font-weight:600;color:var(--txt-2);letter-spacing:.02em}}
    .tick .val{{font-family:var(--mono);color:var(--txt)}}
    .tick .chg{{font-family:var(--mono);font-size:11px}}

    .topbar{{height:58px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:var(--navy);}}
    .topbar h1{{font-size:17px;font-weight:700;letter-spacing:-.01em;color:var(--txt);font-family:var(--sans);margin:0;}}
    .topbar .crumb{{font-family:var(--mono);font-size:10.5px;color:var(--txt-3);letter-spacing:.08em;margin-top:3px;}}

    .page-content{{padding:22px 24px 60px;}}
    .hero{{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:20px;}}
    .hero h2{{font-size:23px;font-weight:700;letter-spacing:-.02em;color:var(--txt);font-family:var(--sans);}}
    .hero p{{color:var(--txt-2);font-size:13px;margin-top:6px;max-width:560px;line-height:1.6;}}
    .hero .stamp{{font-family:var(--mono);font-size:10.5px;color:var(--txt-3);text-align:right;line-height:1.7;}}

    .grid{{display:grid;gap:14px;}}
    .snap{{grid-template-columns:repeat(4,1fr);margin-bottom:14px;}}
    .snap .panel{{padding:15px 17px;}}
    .snap .l{{font-family:var(--mono);font-size:10px;letter-spacing:.12em;color:var(--txt-3);text-transform:uppercase;}}
    .snap .v{{font-family:var(--mono);font-size:24px;font-weight:600;margin-top:10px;letter-spacing:-.01em;color:var(--txt);}}
    .snap .c{{font-family:var(--mono);font-size:11.5px;margin-top:6px;display:flex;gap:7px;align-items:center;}}

    .split{{display:grid;grid-template-columns:1.4fr 1fr;gap:14px;margin-bottom:14px;}}
    .panel{{background:var(--panel);border:1px solid var(--line-soft);border-radius:10px;padding:16px 18px;position:relative;overflow:hidden;}}
    .panel-h{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}}
    .panel-h .t{{font-size:13px;font-weight:600;letter-spacing:.01em;display:flex;align-items:center;gap:8px;color:var(--txt);}}
    .panel-h .t .ic{{color:var(--accent);display:flex;}}
    .panel-h .tag{{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;color:var(--txt-3);border:1px solid var(--line);padding:3px 7px;border-radius:4px;}}

    table{{width:100%;border-collapse:collapse;}}
    thead th{{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;color:var(--txt-3);text-transform:uppercase;text-align:right;padding:0 0 11px;font-weight:500;border-bottom:1px solid var(--line);}}
    thead th:first-child{{text-align:left;}}
    tbody td{{padding:11px 0;border-bottom:1px solid var(--line-soft);font-family:var(--mono);font-size:12.5px;text-align:right;color:var(--txt);}}
    tbody tr:last-child td{{border-bottom:none;}}
    tbody td:first-child{{text-align:left;}}
    .wl-name{{display:flex;align-items:center;gap:10px;font-family:var(--sans);}}
    .wl-logo{{width:26px;height:26px;border-radius:6px;flex:none;display:grid;place-items:center;font-family:var(--mono);font-weight:700;font-size:11px;background:#152037;border:1px solid var(--line);color:var(--txt-2);}}
    .wl-tk{{font-family:var(--mono);font-size:10px;color:var(--txt-3);letter-spacing:.04em;}}
    .risk-chip{{display:inline-block;font-family:var(--mono);font-size:10px;padding:2px 8px;border-radius:4px;}}
    .rc-g{{background:var(--up-soft);color:var(--up);}}
    .rc-a{{background:var(--amber-soft);color:var(--amber);}}
    .rc-r{{background:var(--down-soft);color:var(--down);}}

    .mods{{display:flex;flex-direction:column;gap:10px;}}
    .mod{{display:flex;gap:13px;align-items:flex-start;padding:13px 14px;border:1px solid var(--line-soft);border-radius:9px;background:var(--panel-2);transition:border-color .12s;}}
    .mod:hover{{border-color:var(--accent-line);}}
    .mod .mi{{width:34px;height:34px;border-radius:8px;flex:none;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);}}
    .mod .mi svg{{width:17px;height:17px;stroke-width:1.8;}}
    .mod .mt{{font-size:13px;font-weight:600;margin-bottom:3px;color:var(--txt);}}
    .mod .md{{font-size:11.5px;color:var(--txt-2);line-height:1.5;}}
    .mod .tags{{display:flex;gap:5px;margin-top:8px;flex-wrap:wrap;}}
    .mod .tg{{font-family:var(--mono);font-size:9px;letter-spacing:.06em;color:var(--txt-3);border:1px solid var(--line);padding:2px 6px;border-radius:4px;}}

    .disclaimer{{font-size:11px;color:var(--txt-3);text-align:center;margin-top:20px;line-height:1.5;font-family:var(--mono);letter-spacing:.02em;}}
    </style>
    </head>
    <body>
    <div class="tickerbar">
        <div class="tick-label"><span class="dot"></span>LIVE · NSE</div>
        <div class="tick-track">
            <span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span>
            <span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span>
            <span class="tick"><span class="sym">BANK NIFTY</span><span class="val">51,602.05</span><span class="chg down">▼ 0.31%</span></span>
            <span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span>
            <span class="tick"><span class="sym">NIFTY AUTO</span><span class="val">23,104.80</span><span class="chg up">▲ 0.88%</span></span>
            <span class="tick"><span class="sym">INR/USD</span><span class="val">83.42</span><span class="chg up">▲ 0.08%</span></span>
            <span class="tick"><span class="sym">GOLD MCX</span><span class="val">71,840</span><span class="chg up">▲ 0.43%</span></span>
            <span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span>
            <span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span>
            <span class="tick"><span class="sym">BANK NIFTY</span><span class="val">51,602.05</span><span class="chg down">▼ 0.31%</span></span>
            <span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span>
        </div>
    </div>
    <div class="topbar">
        <div><h1>Overview</h1><div class="crumb">HOME / OVERVIEW</div></div>
    </div>
    <div class="page-content">
        <div class="hero">
            <div>
                <h2>Welcome to MarketPulse India.</h2>
                <p>Multi-model risk intelligence for NSE-listed equities - tail risk via EVT, volatility regimes via HMM, and news sentiment via FinBERT, distilled into plain-English signals.</p>
            </div>
            <div class="stamp">NSE TERMINAL<br>INDIA · EQUITY RISK</div>
        </div>

        <div class="grid snap">
            <div class="panel"><div class="l">NIFTY 50</div><div class="v">24,318.40</div><div class="c up"><span class="pill up">▲ 0.62%</span><span>+150.20</span></div></div>
            <div class="panel"><div class="l">SENSEX</div><div class="v">79,943.71</div><div class="c up"><span class="pill up">▲ 0.55%</span><span>+438.10</span></div></div>
            <div class="panel"><div class="l">India VIX</div><div class="v" style="color:#E0A33B">14.82</div><div class="c"><span class="pill down">▼ 3.10%</span><span class="down">elevated</span></div></div>
            <div class="panel"><div class="l">Adv / Decl</div><div class="v">1,284 / 906</div><div class="c up"><span class="pill up">BREADTH +</span><span>58% advancing</span></div></div>
        </div>

        <div class="split">
            <div class="panel">
                <div class="panel-h">
                    <div class="t"><span class="ic"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 5h18M3 12h18M3 19h18"/></svg></span>Watchlist</div>
                    <span class="tag">LIVE · RISK-RANKED</span>
                </div>
                <table>
                    <thead><tr><th>Stock</th><th>Last</th><th>Chg %</th><th>Regime</th><th>Signal</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>

            <div class="panel">
                <div class="panel-h">
                    <div class="t"><span class="ic"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 2"/></svg></span>Modules</div>
                    <span class="tag">5 TOOLS</span>
                </div>
                <div class="mods">
                    <div class="mod"><div class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 5-7"/></svg></div><div><div class="mt">Stock Analysis</div><div class="md">Full risk breakdown — EVT tail risk, HMM regime, FinBERT sentiment.</div><div class="tags"><span class="tg">EVT</span><span class="tg">HMM</span><span class="tg">FinBERT</span></div></div></div>
                    <div class="mod"><div class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6M9 13h6M9 17h3"/></svg></div><div><div class="mt">Earnings Analysis</div><div class="md">Quarterly revenue, profit, and EPS beat/miss history.</div><div class="tags"><span class="tg">EPS</span><span class="tg">Revenue</span></div></div></div>
                    <div class="mod"><div class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 4h16v16H4z"/><path d="M8 8h8M8 12h8M8 16h5"/></svg></div><div><div class="mt">News Feed</div><div class="md">Latest financial headlines — timezone aware.</div><div class="tags"><span class="tg">Multi-source</span></div></div></div>
                    <div class="mod"><div class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 13h4l2 5 4-12 2 7h6"/></svg></div><div><div class="mt">Portfolio Tracker</div><div class="md">Rank up to 5 stocks by risk with AI advice.</div><div class="tags"><span class="tg">Ranked</span><span class="tg">Health score</span></div></div></div>
                </div>
            </div>
        </div>
        <div class="disclaimer">NOT FINANCIAL ADVICE · CONSULT A SEBI-REGISTERED ADVISOR · DATA VIA YAHOO FINANCE</div>
    </div>
    </body>
    </html>
    """, height=900, scrolling=True)
    
# PAGE: STOCK ANALYSIS
# ─────────────────────────────────────────
elif st.session_state.page == "stocks":
   
    st.markdown("""
    <div class="tickerbar">
        <div class="tick-label"><span class="dot"></span>LIVE · NSE</div>
        <div class="tick-track">
            <span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span>
            <span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span>
            <span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span>
            <span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span>
            <span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span>
        </div>
    </div>
    <div class="topbar">
        <div><h1>Stock Analysis</h1><div class="crumb">HOME / STOCK ANALYSIS</div></div>
    </div>
    <div class="page-content">
    """, unsafe_allow_html=True)

    with st.form("analysis_form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            # Searchable dropdown
            company_options = [""] + sorted(ALL_STOCKS.keys())
            selected_company = st.selectbox(
                "Select Company",
                options=company_options,
                format_func=lambda x: "Type to search..." if x == "" else x,
                key="company_select"
            )
            # Also allow manual ticker entry
            manual_ticker = st.text_input(
                "Or enter ticker manually",
                placeholder="e.g. RELIANCE.NS",
                key="manual_ticker"
            )
        with c2:
            if selected_company:
                ticker = ALL_STOCKS[selected_company]
                company_name = selected_company
                st.info(f"Ticker: **{ticker}**")
            elif manual_ticker:
                ticker = manual_ticker.strip().upper()
                if not ticker.endswith(".NS"):
                    ticker = ticker + ".NS"
                company_name = TICKER_TO_COMPANY.get(ticker, ticker.replace(".NS", ""))
                st.info(f"Company: **{company_name}**")
            else:
                ticker = ""
                company_name = ""
        with c3:
            period = st.selectbox("Period", ["1y", "2y", "5y"], index=1)
        submitted = st.form_submit_button("Analyze", use_container_width=True)

    if submitted:
        if not ticker:
            st.error("Please select a company or enter a ticker.")
            st.stop()

    if submitted:
        with st.spinner("Fetching data..."):
            df = fetch_stock_data(ticker, period=period)
            df = compute_returns(df)

        with st.spinner("Running risk models..."):
            evt = compute_tail_risk(df["log_return"])
            regime_df, _ = detect_regimes(df["log_return"])
            current_regime = regime_df["regime"].iloc[-1]
            regime_counts = regime_df["regime"].value_counts()
            sent = analyze_sentiment(company_name)
            score = compute_composite_score(
                var_99=evt["VaR_99"],
                es_99=evt["ES_99"],
                regime=current_regime,
                sentiment_risk_score=sent["sentiment_risk_score"]
            )

        st.markdown("---")
        st.markdown(f"### {company_name} ({ticker})")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("99% VaR", f"{evt['VaR_99']}%", help="Worst expected daily loss 99% of the time")
        c2.metric("99% ES", f"{evt['ES_99']}%", help="Average loss when VaR is breached")
        c3.metric("Volatility Regime", current_regime)
        c4.metric("Sentiment Risk", f"{sent['sentiment_risk_score']}/100")

        st.markdown("---")
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            st.metric("Risk Score", f"{score['composite_score']} / 100")
            st.markdown(f"**{score['label']}**")
        with rc2:
            st.progress(int(score['composite_score']))
            if score['composite_score'] >= 65:
                st.error("High risk. Be cautious before investing.")
            elif score['composite_score'] >= 35:
                st.warning("Moderate risk. Research before investing.")
            else:
                st.success("Lower risk environment. Still do your due diligence.")

        st.markdown("---")
        st.markdown("#### AI Insights")
        with st.spinner("Generating insights..."):
            headlines = get_news(company_name + " stock NSE", max_items=5)
            raw = get_ai_insights(
                company_name, ticker,
                evt["VaR_99"], evt["ES_99"],
                current_regime, sent["sentiment_risk_score"],
                score["composite_score"], score["label"], headlines
            )

        if raw:
            sections = parse_insights(raw)
            if sections["summary"].strip():
                st.markdown(
                    f'<div class="summary-box">{sections["summary"].strip()}</div>',
                    unsafe_allow_html=True
                )

            bc1, bc2 = st.columns(2)
            with bc1:
                st.markdown(
                    f'<div class="bull-box"><strong>Bull Case</strong><br><br>{sections["bull"].strip().replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True
                )
            with bc2:
                st.markdown(
                    f'<div class="bear-box"><strong>Bear Case</strong><br><br>{sections["bear"].strip().replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True
                )

            if sections["signal"].strip():
                st.markdown(
                    f'<div class="signal-box"><strong>Signal</strong> &nbsp;|&nbsp; {sections["signal"].strip()}</div>',
                    unsafe_allow_html=True
                )
            if sections["tip"].strip():
                st.markdown(
                    f'<div class="tip-box"><strong>Portfolio Tip</strong><br><br>{sections["tip"].strip()}</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.markdown("#### Price History")
        st.caption("Closing price over selected period. Rising = gaining value. Falling = losing value.")
        st.line_chart(df["Close"])

        st.markdown("---")
        st.markdown("#### 30-Day Price Forecast")
        with st.spinner("Running ARIMA forecast..."):
            pred = predict_prices(df)

        if pred:
            import pandas as pd
            import numpy as np

            direction = "up" if pred["change_pct"] > 0 else "down"
            color = "green" if pred["change_pct"] > 0 else "red"

            fc1, fc2, fc3 = st.columns(3)
            fc1.metric("Current Price", f"₹{pred['current_price']}")
            fc2.metric("Predicted (30d)", f"₹{pred['predicted_end']}")
            fc3.metric("Expected Change", f"{pred['change_pct']}%",
                      delta=f"{pred['change_pct']}%")

            forecast_df = pd.DataFrame({
                "Forecast": pred["forecast"],
                "Lower Band": pred["lower"],
                "Upper Band": pred["upper"]
            }, index=pred["dates"])
            st.line_chart(forecast_df)

            change_abs = abs(pred["change_pct"])
            if pred["change_pct"] > 2:
                forecast_text = f"The model suggests **{company_name}** may trend upward over the next 30 trading days, with a predicted price of around ₹{pred['predicted_end']} (currently ₹{pred['current_price']}). The shaded band shows the range of likely prices."
            
            elif pred["change_pct"] < -2:
                forecast_text = f"The model suggests **{company_name}** may trend downward over the next 30 trading days, with a predicted price of around ₹{pred['predicted_end']} (currently ₹{pred['current_price']}). Consider waiting for a better entry point."
            else:
                forecast_text = f"The model suggests **{company_name}** may trade sideways over the next 30 days, staying close to the current price of ₹{pred['current_price']}. No strong directional signal."

            st.info(forecast_text)
            st.caption("Forecast based on ARIMA model. Predictions are not guaranteed - use as one input among many.")

        st.session_state.analysis_data = {
            "ticker": ticker,
            "company": company_name,
            "var_99": evt["VaR_99"],
            "es_99": evt["ES_99"],
            "regime": current_regime,
            "sentiment_score": sent["sentiment_risk_score"],
            "composite_score": score["composite_score"],
            "label": score["label"]
        }
        st.caption("Not financial advice. Consult a SEBI-registered advisor before investing.")
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# PAGE: NEWS FEED
# ─────────────────────────────────────────
elif st.session_state.page == "news":
    st.markdown("""
    <div class="tickerbar"><div class="tick-label"><span class="dot"></span>LIVE · NSE</div><div class="tick-track"><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span><span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span><span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span></div></div>
    <div class="topbar"><div><h1>News Feed</h1><div class="crumb">HOME / NEWS FEED</div></div></div>
    <div class="page-content">
    """, unsafe_allow_html=True)
    st.markdown("## News Feed")
    st.markdown(
        f"Latest financial news · Timezone: **{st.session_state.timezone}** · Language: **{st.session_state.language}**"
    )
    st.markdown("---")

    nc1, nc2 = st.columns([3, 1])
    with nc1:
        query = st.text_input("Search", value="Reliance Industries stock NSE")
    with nc2:
        max_items = st.selectbox("Articles", [6, 12, 20], index=1)

    if st.button("Get News"):
        entries = get_news(query, max_items)
        if not entries:
            st.info("No news found. Try a different search term.")
        else:
            st.markdown(f"**{len(entries)} articles found**")
            st.markdown("---")
            for item in entries:
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{item['title']}</div>
                    <div class="news-meta">
                        <span class="news-source">{item['source']}</span>
                        &nbsp;·&nbsp; {item['date']}
                        {"&nbsp;·&nbsp;<a href='" + item['link'] + "' target='_blank' style='color:#666; text-decoration:none'>Read</a>" if item['link'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# PAGE: CHATBOT
# ─────────────────────────────────────────
elif st.session_state.page == "chatbot":
    st.markdown("""
    <div class="tickerbar"><div class="tick-label"><span class="dot"></span>LIVE · NSE</div><div class="tick-track"><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span><span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span><span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span></div></div>
    <div class="topbar"><div><h1>AI Assistant</h1><div class="crumb">ASSISTANT / CHATBOT</div></div></div>
    <div class="page-content">
    """, unsafe_allow_html=True)
    st.markdown("## MarketPulse AI")
    st.markdown("---")

    data = st.session_state.analysis_data
    if data:
        st.markdown(f"""
        <div class="chat-header">
            Context loaded &nbsp;·&nbsp; {data.get('company')} ({data.get('ticker')})
            &nbsp;·&nbsp; Risk Score: {data.get('composite_score')}/100
            &nbsp;·&nbsp; {data.get('label')}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-header">
            No analysis loaded. Run a stock analysis first for context-aware answers,
            or ask general investing questions below.
        </div>
        """, unsafe_allow_html=True)

    _, clr_col = st.columns([5, 1])
    with clr_col:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if not st.session_state.messages:
        st.markdown("**Suggested questions**")
        suggestions = [
            "Should I invest in this stock right now?",
            "What does VaR mean in simple terms?",
            "How do I diversify my portfolio?",
            "What is High Vol regime?",
        ]
        s1, s2 = st.columns(2)
        for i, s in enumerate(suggestions):
            col = s1 if i % 2 == 0 else s2
            if col.button(s, use_container_width=True, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": s})
                response = chat_response(s)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything about stocks or investing..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(""):
                response = chat_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown('</div>', unsafe_allow_html=True)

        # ─────────────────────────────────────────
# PAGE: PORTFOLIO
# ─────────────────────────────────────────
elif st.session_state.page == "portfolio":
    st.markdown("""
    <div class="tickerbar"><div class="tick-label"><span class="dot"></span>LIVE · NSE</div><div class="tick-track"><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span><span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span><span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span></div></div>
    <div class="topbar"><div><h1>Portfolio Tracker</h1><div class="crumb">HOME / PORTFOLIO</div></div></div>
    <div class="page-content">
    """, unsafe_allow_html=True)
    st.markdown("## Portfolio Tracker")
    st.markdown("Enter up to 5 NSE stocks to get a ranked risk breakdown and portfolio health score.")
    st.markdown("---")

    with st.form("portfolio_form"):
        st.markdown("**Select up to 5 stocks**")
        company_options = [""] + sorted(NSE_STOCKS.keys())
        cols = st.columns(5)
        tickers = []
        companies = []
        defaults = ["Reliance Industries", "TCS", "HDFC Bank", "Infosys", ""]
        for i, col in enumerate(cols):
            with col:
                selected = st.selectbox(
                    f"Stock {i+1}",
                    options=company_options,
                    index=company_options.index(defaults[i]) if defaults[i] in company_options else 0,
                    key=f"port_{i}",
                    format_func=lambda x: "Select..." if x == "" else x
                )
                tickers.append(NSE_STOCKS.get(selected, ""))
                companies.append(selected)
        period = st.selectbox("Period", ["1y", "2y"], index=0)
        submitted = st.form_submit_button("Analyze Portfolio", use_container_width=True)

    if submitted:
        valid = [(t.strip(), c.strip()) for t, c in zip(tickers, companies) if t.strip()]
        if not valid:
            st.warning("Enter at least one ticker.")
        else:
            results = []
            progress = st.progress(0)
            status = st.empty()

            for i, (ticker, company) in enumerate(valid):
                status.text(f"Analyzing {ticker}...")
                try:
                    df = fetch_stock_data(ticker, period=period)
                    df = compute_returns(df)
                    evt = compute_tail_risk(df["log_return"])
                    regime_df, _ = detect_regimes(df["log_return"])
                    current_regime = regime_df["regime"].iloc[-1]
                    sent = analyze_sentiment(company)
                    score = compute_composite_score(
                        var_99=evt["VaR_99"],
                        es_99=evt["ES_99"],
                        regime=current_regime,
                        sentiment_risk_score=sent["sentiment_risk_score"]
                    )
                    results.append({
                        "Ticker": ticker,
                        "Company": company,
                        "Risk Score": score["composite_score"],
                        "Label": score["label"],
                        "VaR 99%": f"{evt['VaR_99']}%",
                        "ES 99%": f"{evt['ES_99']}%",
                        "Regime": current_regime,
                        "Sentiment": f"{sent['sentiment_risk_score']}/100"
                    })
                except Exception as e:
                    results.append({
                        "Ticker": ticker,
                        "Company": company,
                        "Risk Score": None,
                        "Label": "Error",
                        "VaR 99%": "N/A",
                        "ES 99%": "N/A",
                        "Regime": "N/A",
                        "Sentiment": "N/A"
                    })
                progress.progress((i + 1) / len(valid))

            status.empty()
            progress.empty()

            # Sort by risk score
            valid_results = [r for r in results if r["Risk Score"] is not None]
            valid_results.sort(key=lambda x: x["Risk Score"])

            st.markdown("---")
            st.markdown("### Portfolio Risk Ranking")
            st.caption("Sorted from lowest to highest risk.")

            import pandas as pd
            df_results = pd.DataFrame(valid_results)
            st.dataframe(
                df_results[["Company", "Ticker", "Risk Score", "Label", "VaR 99%", "Regime", "Sentiment"]],
                use_container_width=True,
                hide_index=True
            )

            # Portfolio health score
            avg_score = sum(r["Risk Score"] for r in valid_results) / len(valid_results)
            st.markdown("---")
            pc1, pc2 = st.columns([1, 2])
            with pc1:
                st.metric("Portfolio Health Score", f"{round(avg_score, 1)} / 100")
                if avg_score >= 65:
                    st.error("High risk portfolio. Consider rebalancing.")
                
                elif avg_score >= 35:
                    st.warning("Moderate risk. Monitor closely.")
                else:
                    st.success("Well-balanced, lower risk portfolio.")
            with pc2:
                st.progress(int(avg_score))

            # Risk chart
            st.markdown("---")
            st.markdown("#### Risk Score by Stock")
            chart_data = pd.DataFrame({
                "Stock": [r["Ticker"] for r in valid_results],
                "Risk Score": [r["Risk Score"] for r in valid_results]
            }).set_index("Stock")
            st.bar_chart(chart_data)

            # AI Portfolio advice
            st.markdown("---")
            st.markdown("#### AI Portfolio Advice")
            with st.spinner("Generating advice..."):
                client = get_groq_client()
                if client:
                    summary = "\n".join([
                        f"- {r['Company']} ({r['Ticker']}): Risk Score {r['Risk Score']}/100, {r['Label']}, Regime: {r['Regime']}"
                        for r in valid_results
                    ])
                    prompt = f"""You are a portfolio advisor for Indian retail investors.

Here is the user's portfolio risk analysis:
{summary}

Overall portfolio risk score: {round(avg_score, 1)}/100

Give:
1. **Portfolio Summary** (2-3 sentences on overall health)
2. **Hold** (stocks that look stable)
3. **Watch** (stocks to monitor carefully)
4. **Reduce** (stocks with high risk worth reconsidering)
5. **One Action** (the single most important thing this investor should do)

Keep it simple, practical, and jargon-free."""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=700,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.markdown(response.choices[0].message.content)

            st.caption("Not financial advice. Consult a SEBI-registered advisor before investing.")
            st.markdown('</div>', unsafe_allow_html=True)
            # ─────────────────────────────────────────
# PAGE: EARNINGS ANALYSIS
# ─────────────────────────────────────────
elif st.session_state.page == "earnings":
    st.markdown("""
    <div class="tickerbar"><div class="tick-label"><span class="dot"></span>LIVE · NSE</div><div class="tick-track"><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span><span class="tick"><span class="sym">SENSEX</span><span class="val">79,943.71</span><span class="chg up">▲ 0.55%</span></span><span class="tick"><span class="sym">NIFTY IT</span><span class="val">41,887.20</span><span class="chg up">▲ 1.24%</span></span><span class="tick"><span class="sym">NIFTY 50</span><span class="val">24,318.40</span><span class="chg up">▲ 0.62%</span></span></div></div>
    <div class="topbar"><div><h1>Earnings Analysis</h1><div class="crumb">HOME / EARNINGS</div></div></div>
    <div class="page-content">
    """, unsafe_allow_html=True)
    import pandas as pd
    import yfinance as yf

    st.markdown("## Earnings Analysis")
    st.markdown("Quarterly earnings breakdown - EPS, Revenue, and Profit trends.")
    st.markdown("---")

    with st.form("earnings_form"):
        ec1, ec2 = st.columns([2, 2])
        with ec1:
            ticker = st.text_input("NSE Ticker", value="RELIANCE.NS")
        with ec2:
            company_name = st.text_input("Company Name", value="Reliance Industries")
        submitted = st.form_submit_button("Get Earnings", use_container_width=True)

    if submitted:
        with st.spinner("Fetching earnings data..."):
            try:
                stock = yf.Ticker(ticker)
                
                # Quarterly financials
                quarterly_financials = stock.quarterly_financials
                quarterly_earnings = stock.quarterly_earnings

                # Income statement data
                income = stock.quarterly_income_stmt

            except Exception as e:
                st.error(f"Could not fetch data for {ticker}. Try another ticker.")
                income = None
                quarterly_earnings = None

        if income is not None and not income.empty:
            st.markdown(f"### {company_name} ({ticker})")
            st.markdown("---")

            # --- Revenue Trend ---
            try:
                if "Total Revenue" in income.index:
                    revenue = income.loc["Total Revenue"].dropna()
                    revenue = revenue.sort_index()
                    revenue_df = pd.DataFrame({
                        "Quarter": [str(d)[:10] for d in revenue.index],
                        "Revenue (Cr)": [round(v/1e7, 2) for v in revenue.values]
                    }).set_index("Quarter")

                    st.markdown("#### Revenue Trend")
                    st.caption("Total revenue per quarter in Crores (₹)")
                    st.bar_chart(revenue_df)
            except:
                st.info("Revenue data not available.")

            # --- Net Profit Trend ---
            try:
                profit_keys = ["Net Income", "Net Income Common Stockholders"]
                profit_key = next((k for k in profit_keys if k in income.index), None)
                if profit_key:
                    profit = income.loc[profit_key].dropna()
                    profit = profit.sort_index()
                    profit_df = pd.DataFrame({
                        "Quarter": [str(d)[:10] for d in profit.index],
                        "Net Profit (Cr)": [round(v/1e7, 2) for v in profit.values]
                    }).set_index("Quarter")

                    st.markdown("#### Net Profit Trend")
                    st.caption("Net profit per quarter in Crores (₹)")
                    st.bar_chart(profit_df)
            except:
                st.info("Profit data not available.")

            # --- EPS Beat/Miss ---
            try:
                earnings = stock.earnings_history
                if earnings is not None and not earnings.empty:
                    st.markdown("#### EPS - Actual vs Estimate")
                    st.caption("Green = beat estimate, Red = missed estimate")

                    eps_data = earnings[["epsEstimate", "epsActual"]].dropna().tail(8)
                    eps_data.index = [str(i)[:10] for i in eps_data.index]
                    eps_data.columns = ["EPS Estimate", "EPS Actual"]
                    st.line_chart(eps_data)

                    # Beat/Miss table
                    eps_data["Result"] = eps_data.apply(
                        lambda r: "Beat" if r["EPS Actual"] >= r["EPS Estimate"] else "Missed", axis=1
                    )
                    eps_data["Surprise %"] = ((eps_data["EPS Actual"] - eps_data["EPS Estimate"]) / abs(eps_data["EPS Estimate"]) * 100).round(2)
                    st.dataframe(eps_data, use_container_width=True)
            except:
                st.info("EPS history not available for this ticker.")

            # --- Key Metrics ---
            st.markdown("---")
            st.markdown("#### Key Financial Metrics")
            try:
                info = stock.info
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("P/E Ratio", info.get("trailingPE", "N/A"))
                m2.metric("EPS (TTM)", info.get("trailingEps", "N/A"))
                m3.metric("Revenue (TTM)", f"₹{round(info.get('totalRevenue', 0)/1e7, 0):.0f} Cr" if info.get('totalRevenue') else "N/A")
                m4.metric("Profit Margin", f"{round(info.get('profitMargins', 0)*100, 2)}%" if info.get('profitMargins') else "N/A")
            except:
                st.info("Key metrics unavailable.")

            # --- AI Earnings Summary ---
            st.markdown("---")
            st.markdown("#### AI Earnings Summary")
            with st.spinner("Generating AI summary..."):
                client = get_groq_client()
                if client:
                    try:
                        info = stock.info
                        pe = info.get("trailingPE", "N/A")
                        eps = info.get("trailingEps", "N/A")
                        margin = info.get("profitMargins", "N/A")
                        revenue = info.get("totalRevenue", "N/A")

                        prompt = f"""You are a financial analyst helping Indian retail investors understand earnings.

Company: {company_name} ({ticker})
P/E Ratio: {pe}
EPS (TTM): {eps}
Profit Margin: {margin}
Total Revenue (TTM): {revenue}

Give a concise earnings analysis:
1. **Earnings Health** (2-3 sentences on overall financial health)
2. **Strengths** (2-3 positive points from the financials)
3. **Concerns** (2-3 things to watch out for)
4. **Valuation** (is the P/E reasonable? overvalued or undervalued?)
5. **Bottom Line** (one sentence verdict for a retail investor)

Use simple language. No jargon."""

                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            max_tokens=700,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.markdown(response.choices[0].message.content)
                    except Exception as e:
                        st.info("AI summary unavailable.")

        else:
            st.warning(f"No earnings data found for {ticker}. This is common for some NSE stocks on Yahoo Finance. Try `TCS.NS`, `INFY.NS`, or `HDFCBANK.NS`.")

        st.caption("Data sourced from Yahoo Finance. Not financial advice.")
        st.markdown('</div>', unsafe_allow_html=True)