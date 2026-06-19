def load_css():
    return """
<style>
/* MarketPulse India · Bloomberg-style dark theme */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
    --navy:        #0A0F1E;
    --navy-2:      #0E1426;
    --panel:       #111932;
    --panel-2:     #0D1424;
    --line:        #1E2A48;
    --line-soft:   #18223D;
    --accent:      #2563EB;
    --accent-soft: rgba(37,99,235,.14);
    --accent-line: rgba(37,99,235,.45);
    --txt:         #E7ECF6;
    --txt-2:       #9AA6C2;
    --txt-3:       #5E6C8C;
    --up:          #16C77E;
    --up-soft:     rgba(22,199,126,.12);
    --down:        #F0455E;
    --down-soft:   rgba(240,69,94,.12);
    --amber:       #E0A33B;
    --amber-soft:  rgba(224,163,59,.12);
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --sans: 'Inter', system-ui, sans-serif;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }

body {
    background: var(--navy);
    color: var(--txt);
    font-family: var(--sans);
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    display: grid;
    grid-template-columns: 228px 1fr;
    grid-template-rows: 100vh;
    overflow: hidden;
}

a { color: inherit; text-decoration: none; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: #1C2742; border-radius: 6px; }
::-webkit-scrollbar-track { background: transparent; }

.up   { color: var(--up); }
.down { color: var(--down); }
.pill { padding: 2px 7px; border-radius: 4px; font-size: 11px; }
.pill.up   { background: var(--up-soft); }
.pill.down { background: var(--down-soft); }

/* ── Sidebar ── */
.sidebar {
    background: var(--navy-2);
    border-right: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 18px 18px 16px;
    border-bottom: 1px solid var(--line);
}
.brand .mark {
    width: 30px; height: 30px;
    border-radius: 7px;
    flex: none;
    background: linear-gradient(145deg, var(--accent), #1746b0);
    display: grid;
    place-items: center;
    box-shadow: 0 0 0 1px rgba(37,99,235,.4), 0 6px 16px rgba(37,99,235,.25);
}
.brand .mark svg { width: 17px; height: 17px; }
.brand .name {
    font-weight: 700;
    font-size: 14.5px;
    letter-spacing: -.01em;
    line-height: 1;
}
.brand .sub {
    font-family: var(--mono);
    font-size: 9.5px;
    color: var(--txt-3);
    letter-spacing: .12em;
    margin-top: 3px;
}
.nav { padding: 14px 12px; flex: 1; overflow-y: auto; }
.nav-label {
    font-family: var(--mono);
    font-size: 9.5px;
    letter-spacing: .18em;
    color: var(--txt-3);
    padding: 0 10px;
    margin: 14px 0 7px;
    text-transform: uppercase;
}
.nav-label:first-child { margin-top: 0; }
.nav-item {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 9px 10px;
    border-radius: 7px;
    cursor: pointer;
    color: var(--txt-2);
    font-size: 13px;
    font-weight: 500;
    transition: background .12s, color .12s;
    margin-bottom: 2px;
    position: relative;
}
.nav-item svg { width: 16px; height: 16px; flex: none; stroke-width: 1.7; }
.nav-item:hover { background: #131c34; color: var(--txt); }
.nav-item.active { background: var(--accent-soft); color: #fff; }
.nav-item.active::before {
    content: "";
    position: absolute;
    left: -12px; top: 7px; bottom: 7px;
    width: 3px;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
}
.nav-item.active svg { color: var(--accent); }
.prefs {
    border-top: 1px solid var(--line);
    padding: 14px 16px 16px;
}
.pref-row { margin-bottom: 10px; }
.pref-row label {
    display: block;
    font-family: var(--mono);
    font-size: 9.5px;
    letter-spacing: .1em;
    color: var(--txt-3);
    margin-bottom: 5px;
    text-transform: uppercase;
}
.pref-row select {
    width: 100%;
    background: var(--panel-2);
    border: 1px solid var(--line);
    color: var(--txt);
    font-family: var(--sans);
    font-size: 12px;
    padding: 5px 8px;
    border-radius: 5px;
    outline: none;
}
.pref-row select:focus { border-color: var(--accent-line); }

/* ── Main column ── */
.main {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
}

/* ── Ticker bar ── */
.tickerbar {
    height: 34px;
    background: var(--panel-2);
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: center;
    overflow: hidden;
}
.tick-label {
    flex: none;
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: .1em;
    color: var(--txt-3);
    padding: 0 16px;
    border-right: 1px solid var(--line);
}
.tick-label .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--up);
    margin-right: 8px;
    box-shadow: 0 0 6px var(--up);
    display: inline-block;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 50% { opacity: .4; } }
.tick-track {
    display: flex;
    align-items: center;
    white-space: nowrap;
    animation: scroll 38s linear infinite;
    flex: none;
}
.tickerbar:hover .tick-track { animation-play-state: paused; }
@keyframes scroll { to { transform: translateX(-50%); } }
.tick {
    display: inline-flex;
    align-items: baseline;
    gap: 8px;
    padding: 0 20px;
    font-size: 12px;
}
.tick .sym  { font-weight: 600; color: var(--txt-2); letter-spacing: .02em; }
.tick .val  { font-family: var(--mono); color: var(--txt); }
.tick .chg  { font-family: var(--mono); font-size: 11px; }

/* ── Topbar ── */
.topbar {
    height: 60px;
    border-bottom: 1px solid var(--line);
    flex: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar h1 { font-size: 17px; font-weight: 700; letter-spacing: -.01em; }
.topbar .crumb {
    font-family: var(--mono);
    font-size: 10.5px;
    color: var(--txt-3);
    letter-spacing: .08em;
    margin-top: 3px;
}

/* ── Search ── */
.search {
    display: flex;
    align-items: center;
    gap: 9px;
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 7px;
    padding: 0 0 0 0;
}
.search .field {
    display: flex;
    align-items: center;
    gap: 9px;
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 7px;
}
.search .field svg { width: 15px; height: 15px; color: var(--txt-3); }
.search input {
    background: none;
    border: none;
    outline: none;
    color: var(--txt);
    font-family: var(--mono);
    font-size: 13px;
    width: 150px;
}
.search input::placeholder { color: var(--txt-3); }
.search .sep  { width: 1px; height: 38px; background: var(--line); }
.search .field.sm input { width: 118px; font-family: var(--sans); }
.search button {
    background: var(--accent);
    color: #fff;
    border: none;
    height: 38px;
    padding: 0 20px;
    border-radius: 0 7px 7px 0;
    font-weight: 600;
    cursor: pointer;
}
.search button:hover { background: #1d57d6; }
.search button.solo  { border-radius: 7px; }

/* ── Scroll area ── */
.scroll { overflow-y: auto; padding: 22px 24px 60px; flex: 1; }

/* ── Panels & shared bits ── */
.panel {
    background: var(--panel);
    border: 1px solid var(--line-soft);
    border-radius: 10px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    margin-bottom: 14px;
}
.panel-h {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.panel-h .t {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: .01em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-h .t .ic { color: var(--accent); }
.panel-h .t .ic svg { width: 15px; height: 15px; }
.panel-h .tag {
    font-family: var(--mono);
    font-size: 9.5px;
    letter-spacing: .1em;
    color: var(--txt-3);
    border: 1px solid var(--line);
    padding: 2px 7px;
    border-radius: 4px;
}
.grid  { display: grid; gap: 14px; }
.full  { grid-column: 1 / -1; }

.disclaimer {
    font-size: 11px;
    color: var(--txt-3);
    text-align: center;
    margin-top: 8px;
    line-height: 1.5;
    font-family: var(--mono);
    letter-spacing: .02em;
}

/* ── Chart helpers ── */
.axis-y       { font-family: var(--mono); font-size: 9px; fill: var(--txt-3); }
.grid-line    { stroke: var(--line-soft); stroke-width: 1; }
.chart-foot   { display: flex; justify-content: space-between; font-family: var(--mono); font-size: 9.5px; color: var(--txt-3); margin-top: 8px; }
.legend       { display: flex; gap: 16px; font-family: var(--mono); font-size: 10px; color: var(--txt-2); }
.legend i     { width: 14px; height: 0; border-top-width: 2px; border-top-style: solid; display: inline-block; margin-right: 6px; vertical-align: middle; }

/* ── Page section heading ── */
.section-h {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: .01em;
    margin: 6px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--txt);
}
.section-h .ic { color: var(--accent); display: flex; }
.section-h .ic svg { width: 15px; height: 15px; }

/* ── Streamlit overrides ── */
[data-testid="stAppViewContainer"] { background: var(--navy) !important; }
[data-testid="stSidebar"]          { background: var(--navy-2) !important; border-right: 1px solid var(--line) !important; }
[data-testid="stMain"]             { background: var(--navy) !important; }
.block-container                   { padding: 1.5rem 2rem !important; max-width: 100% !important; }
#MainMenu, footer, header          { visibility: hidden; }
[data-testid="stDecoration"]       { display: none; }

[data-testid="stMetric"]           { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 8px !important; padding: 16px !important; }
[data-testid="stMetricLabel"]      { color: var(--txt-2) !important; font-family: var(--mono) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .08em; }
[data-testid="stMetricValue"]      { color: var(--txt) !important; font-family: var(--mono) !important; font-size: 22px !important; font-weight: 600 !important; }

[data-testid="stButton"] > button  { background: var(--accent) !important; color: #fff !important; border: none !important; border-radius: 6px !important; font-family: var(--sans) !important; font-weight: 600 !important; }
[data-testid="stButton"] > button:hover { opacity: .85 !important; }

[data-testid="stTextInput"] input  { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 6px !important; color: var(--txt) !important; font-family: var(--mono) !important; }
[data-baseweb="select"]            { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 6px !important; }

[data-testid="stTabs"] [role="tab"] { color: var(--txt-2) !important; font-family: var(--sans) !important; font-size: 13px !important; font-weight: 500 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }

.stPlotlyChart { background: var(--panel) !important; border-radius: 8px !important; border: 1px solid var(--line) !important; padding: 8px; }

h1, h2, h3, h4 { font-family: var(--sans) !important; color: var(--txt) !important; font-weight: 700 !important; }
</style>
"""
