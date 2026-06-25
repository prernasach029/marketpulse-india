def load_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
    --navy: #0A0F1E;
    --navy-2: #0E1426;
    --panel: #111932;
    --panel-2: #0D1424;
    --line: #1E2A48;
    --line-soft: #18223D;
    --accent: #2563EB;
    --accent-soft: rgba(37,99,235,.14);
    --accent-line: rgba(37,99,235,.45);
    --txt: #E7ECF6;
    --txt-2: #9AA6C2;
    --txt-3: #5E6C8C;
    --up: #16C77E;
    --up-soft: rgba(22,199,126,.12);
    --down: #F0455E;
    --down-soft: rgba(240,69,94,.12);
    --amber: #E0A33B;
    --amber-soft: rgba(224,163,59,.12);
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --sans: 'Inter', system-ui, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }
a { color: inherit; text-decoration: none; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: #1c2742; border-radius: 6px; }
::-webkit-scrollbar-track { background: transparent; }

.up { color: var(--up); }
.down { color: var(--down); }
.pill { padding: 2px 7px; border-radius: 4px; font-size: 11px; }
.pill.up { background: var(--up-soft); }
.pill.down { background: var(--down-soft); }

/* Mobile responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 0.5rem !important;
    }
    [data-testid="stSidebar"] {
        width: 80vw !important;
    }
    section[data-testid="stSidebarUserContent"] {
        padding: 1rem 0.5rem !important;
    }
}

/* Streamlit overrides */
[data-testid="stAppViewContainer"] { background: var(--navy) !important; }
[data-testid="stSidebar"] { background: var(--navy-2) !important; border-right: 1px solid var(--line) !important; }
[data-testid="stMain"] { background: var(--navy) !important; }
div[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

[data-testid="stMetric"] { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 8px !important; padding: 16px !important; }
[data-testid="stMetricLabel"] { color: var(--txt-3) !important; font-family: var(--mono) !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: .1em; }
[data-testid="stMetricValue"] { color: var(--txt) !important; font-family: var(--mono) !important; font-size: 22px !important; font-weight: 600 !important; }

[data-testid="stButton"] > button { background: var(--accent) !important; color: #fff !important; border: none !important; border-radius: 6px !important; font-family: var(--sans) !important; font-weight: 600 !important; font-size: 13px !important; }
[data-testid="stButton"] > button:hover { opacity: .85 !important; }

[data-testid="stTextInput"] input { background: var(--panel-2) !important; border: 1px solid var(--line) !important; border-radius: 6px !important; color: var(--txt) !important; font-family: var(--mono) !important; font-size: 13px !important; }
[data-baseweb="select"] { background: var(--panel-2) !important; border: 1px solid var(--line) !important; border-radius: 6px !important; }

h1, h2, h3, h4 { font-family: var(--sans) !important; color: var(--txt) !important; font-weight: 700 !important; }
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Sidebar nav items */
.nav-section { font-family: var(--mono); font-size: 9.5px; letter-spacing: .18em; color: var(--txt-3); text-transform: uppercase; padding: 14px 10px 7px; }
.nav-section:first-child { padding-top: 0; }

/* Ticker bar */
.tickerbar { height: 34px; background: var(--panel-2); border-bottom: 1px solid var(--line); display: flex; align-items: center; overflow: hidden; margin-bottom: 0; }
.tick-label { flex: none; font-family: var(--mono); font-size: 10px; letter-spacing: .1em; color: var(--txt-3); padding: 0 16px; border-right: 1px solid var(--line); height: 100%; display: flex; align-items: center; background: var(--navy-2); }
.tick-label .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--up); margin-right: 8px; box-shadow: 0 0 6px var(--up); display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 50% { opacity: .4; } }
.tick-track { display: flex; align-items: center; white-space: nowrap; animation: scroll 38s linear infinite; flex: none; }
.tickerbar:hover .tick-track { animation-play-state: paused; }
@keyframes scroll { to { transform: translateX(-50%); } }
.tick { display: inline-flex; align-items: baseline; gap: 8px; padding: 0 20px; font-size: 12px; }
.tick .sym { font-weight: 600; color: var(--txt-2); letter-spacing: .02em; }
.tick .val { font-family: var(--mono); color: var(--txt); }
.tick .chg { font-family: var(--mono); font-size: 11px; }

/* Topbar */
.topbar { height: 58px; border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; background: var(--navy); }
.topbar h1 { font-size: 17px; font-weight: 700; letter-spacing: -.01em; color: var(--txt); font-family: var(--sans); margin: 0; }
.topbar .crumb { font-family: var(--mono); font-size: 10.5px; color: var(--txt-3); letter-spacing: .08em; margin-top: 3px; }

/* Page content padding */
.page-content { padding: 22px 24px 60px; }
.block-container {
    padding-left: 1rem !important;
}


/* Panels */
.panel { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 10px; padding: 16px 18px; position: relative; overflow: hidden; margin-bottom: 14px; }
.panel-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.panel-h .t { font-size: 13px; font-weight: 600; letter-spacing: .01em; display: flex; align-items: center; gap: 8px; color: var(--txt); }
.panel-h .t .ic { color: var(--accent); display: flex; }
.panel-h .t .ic svg { width: 15px; height: 15px; }
.panel-h .tag { font-family: var(--mono); font-size: 9.5px; letter-spacing: .1em; color: var(--txt-3); border: 1px solid var(--line); padding: 3px 7px; border-radius: 4px; }
.grid { display: grid; gap: 14px; }
.full { grid-column: 1 / -1; }

/* Feature modules on overview */
.mods { display: flex; flex-direction: column; gap: 10px; }
.mod { display: flex; gap: 13px; align-items: flex-start; padding: 13px 14px; border: 1px solid var(--line-soft); border-radius: 9px; background: var(--panel-2); transition: border-color .12s; cursor: pointer; }
.mod:hover { border-color: var(--accent-line); }
.mod .mi { width: 34px; height: 34px; border-radius: 8px; flex: none; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent); }
.mod .mi svg { width: 17px; height: 17px; stroke-width: 1.8; }
.mod .mt { font-size: 13px; font-weight: 600; margin-bottom: 3px; color: var(--txt); }
.mod .md { font-size: 11.5px; color: var(--txt-2); line-height: 1.5; }
.mod .tags { display: flex; gap: 5px; margin-top: 8px; flex-wrap: wrap; }
.mod .tg { font-family: var(--mono); font-size: 9px; letter-spacing: .06em; color: var(--txt-3); border: 1px solid var(--line); padding: 2px 6px; border-radius: 4px; }

/* Watchlist table */
table { width: 100%; border-collapse: collapse; }
thead th { font-family: var(--mono); font-size: 9.5px; letter-spacing: .1em; color: var(--txt-3); text-transform: uppercase; text-align: right; padding: 0 0 11px; font-weight: 500; border-bottom: 1px solid var(--line); }
thead th:first-child { text-align: left; }
tbody td { padding: 11px 0; border-bottom: 1px solid var(--line-soft); font-family: var(--mono); font-size: 12.5px; text-align: right; color: var(--txt); }
tbody tr:last-child td { border-bottom: none; }
tbody td:first-child { text-align: left; }
.wl-name { display: flex; align-items: center; gap: 10px; font-family: var(--sans); }
.wl-logo { width: 26px; height: 26px; border-radius: 6px; flex: none; display: grid; place-items: center; font-family: var(--mono); font-weight: 700; font-size: 11px; background: #152037; border: 1px solid var(--line); color: var(--txt-2); }
.wl-tk { font-family: var(--mono); font-size: 10px; color: var(--txt-3); letter-spacing: .04em; }
.risk-chip { display: inline-block; font-family: var(--mono); font-size: 10px; padding: 2px 8px; border-radius: 4px; }
.rc-g { background: var(--up-soft); color: var(--up); }
.rc-a { background: var(--amber-soft); color: var(--amber); }
.rc-r { background: var(--down-soft); color: var(--down); }

/* Hero section */
.hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; margin-bottom: 20px; }
.hero h2 { font-size: 23px; font-weight: 700; letter-spacing: -.02em; color: var(--txt); font-family: var(--sans); }
.hero p { color: var(--txt-2); font-size: 13px; margin-top: 6px; max-width: 560px; line-height: 1.6; }
.hero .stamp { font-family: var(--mono); font-size: 10.5px; color: var(--txt-3); text-align: right; line-height: 1.7; }

/* Snap metrics row */
.snap { grid-template-columns: repeat(4, 1fr); margin-bottom: 14px; }
.snap .panel { padding: 15px 17px; }
.snap .l { font-family: var(--mono); font-size: 10px; letter-spacing: .12em; color: var(--txt-3); text-transform: uppercase; }
.snap .v { font-family: var(--mono); font-size: 24px; font-weight: 600; margin-top: 10px; letter-spacing: -.01em; color: var(--txt); }
.snap .c { font-family: var(--mono); font-size: 11.5px; margin-top: 6px; display: flex; gap: 7px; align-items: center; }

/* Split layout */
.split { display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; margin-bottom: 14px; }

/* Stock analysis specific */
.bull-box { background: var(--up-soft); border-left: 3px solid var(--up); padding: 14px 18px; border-radius: 6px; margin: 8px 0; font-size: 0.91em; line-height: 1.7; color: var(--txt); }
.bear-box { background: var(--down-soft); border-left: 3px solid var(--down); padding: 14px 18px; border-radius: 6px; margin: 8px 0; font-size: 0.91em; line-height: 1.7; color: var(--txt); }
.signal-box { background: var(--panel-2); border: 1px solid var(--accent-line); padding: 14px 18px; border-radius: 6px; margin: 8px 0; font-size: 0.93em; color: var(--txt); font-family: var(--mono); }
.tip-box { background: var(--amber-soft); border-left: 3px solid var(--amber); padding: 14px 18px; border-radius: 6px; margin: 8px 0; font-size: 0.91em; line-height: 1.7; color: var(--txt); }
.summary-box { background: var(--panel); border: 1px solid var(--line-soft); padding: 16px 20px; border-radius: 8px; margin: 8px 0; line-height: 1.7; font-size: 0.93em; color: var(--txt-2); }

/* News cards */
.news-card { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
.news-title { font-size: 0.95em; font-weight: 500; line-height: 1.5; margin-bottom: 6px; color: var(--txt); }
.news-meta { font-size: 0.77em; color: var(--txt-3); }
.news-source { color: var(--txt-2); font-weight: 500; font-family: var(--mono); }

/* Chat */
.chat-header { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; font-size: 0.9em; color: var(--txt-2); font-family: var(--mono); }
[data-testid="stChatMessage"] { background: var(--panel) !important; border-radius: 8px !important; border: 1px solid var(--line-soft) !important; margin-bottom: 8px; }

/* Disclaimer */
.disclaimer { font-size: 11px; color: var(--txt-3); text-align: center; margin-top: 20px; line-height: 1.5; font-family: var(--mono); letter-spacing: .02em; }

/* Sidebar brand */
.brand-block { padding: 18px 18px 16px; border-bottom: 1px solid var(--line); display: flex; align-items: center; gap: 10px; margin-bottom: 0; }
.brand-mark { width: 30px; height: 30px; border-radius: 7px; background: linear-gradient(145deg, var(--accent), #1746b0); display: grid; place-items: center; flex: none; box-shadow: 0 0 0 1px rgba(37,99,235,.4), 0 6px 16px rgba(37,99,235,.25); }
.brand-name { font-weight: 700; font-size: 14.5px; letter-spacing: -.01em; line-height: 1; color: var(--txt); font-family: var(--sans); }
.brand-sub { font-family: var(--mono); font-size: 9.5px; color: var(--txt-3); letter-spacing: .12em; margin-top: 3px; }
</style>
"""
