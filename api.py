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
    allow_origins=["*"],
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


@app.get("/stocks")
def get_stocks():
    stocks = {
        "360 One Wam": "360ONE.NS", "3M India": "3MINDIA.NS", "Aarti Industries": "AARTIIND.NS",
        "Aavas Financiers": "AAVAS.NS", "Abbott India": "ABBOTINDIA.NS", "Adani Enterprises": "ADANIENT.NS",
        "Adani Green Energy": "ADANIGREEN.NS", "Adani Ports": "ADANIPORTS.NS", "Adani Power": "ADANIPOWER.NS",
        "Adani Total Gas": "ATGL.NS", "Adani Transmission": "ADANITRANS.NS", "Aditya Birla Capital": "ABCAPITAL.NS",
        "Aditya Birla Fashion": "ABFRL.NS", "Alkem Laboratories": "ALKEM.NS", "Amara Raja Energy": "AMARAJABAT.NS",
        "Ambuja Cements": "AMBUJACEM.NS", "Angel One": "ANGELONE.NS", "Apollo Hospitals": "APOLLOHOSP.NS",
        "Apollo Tyres": "APOLLOTYRE.NS", "Ashok Leyland": "ASHOKLEY.NS", "Asian Paints": "ASIANPAINT.NS",
        "Astral": "ASTRAL.NS", "Atul": "ATUL.NS", "Aurobindo Pharma": "AUROPHARMA.NS",
        "Avenue Supermarts": "DMART.NS", "Axis Bank": "AXISBANK.NS", "Bajaj Auto": "BAJAJ-AUTO.NS",
        "Bajaj Finance": "BAJFINANCE.NS", "Bajaj Finserv": "BAJAJFINSV.NS", "Bajaj Holdings": "BAJAJHLDNG.NS",
        "Balkrishna Industries": "BALKRISIND.NS", "Bank of Baroda": "BANKBARODA.NS", "Bank of India": "BANKINDIA.NS",
        "Berger Paints": "BERGEPAINT.NS", "Bharat Electronics": "BEL.NS", "Bharat Forge": "BHARATFORG.NS",
        "Bharat Heavy Electricals": "BHEL.NS", "Bharat Petroleum": "BPCL.NS", "Biocon": "BIOCON.NS",
        "Birla Corporation": "BIRLACORPN.NS", "Bosch": "BOSCHLTD.NS", "Britannia Industries": "BRITANNIA.NS",
        "BSE": "BSE.NS", "Canara Bank": "CANBK.NS", "Castrol India": "CASTROLIND.NS",
        "Cholamandalam Investment": "CHOLAFIN.NS", "Cipla": "CIPLA.NS", "Coal India": "COALINDIA.NS",
        "Coforge": "COFORGE.NS", "Colgate Palmolive": "COLPAL.NS", "Container Corporation": "CONCOR.NS",
        "Coromandel International": "COROMANDEL.NS", "Crompton Greaves Consumer": "CROMPTON.NS",
        "Cummins India": "CUMMINSIND.NS", "Dabur India": "DABUR.NS", "Dalmia Bharat": "DALBHARAT.NS",
        "Deepak Nitrite": "DEEPAKNTR.NS", "Delhivery": "DELHIVERY.NS", "Divi's Laboratories": "DIVISLAB.NS",
        "Dixon Technologies": "DIXON.NS", "DLF": "DLF.NS", "Dr Lal Pathlabs": "LALPATHLAB.NS",
        "Dr Reddys Laboratories": "DRREDDY.NS", "Eicher Motors": "EICHERMOT.NS", "Emami": "EMAMILTD.NS",
        "Endurance Technologies": "ENDURANCE.NS", "Escorts Kubota": "ESCORTS.NS", "Exide Industries": "EXIDEIND.NS",
        "Federal Bank": "FEDERALBNK.NS", "Finolex Cables": "FINCABLES.NS", "Gail India": "GAIL.NS",
        "Gland Pharma": "GLAND.NS", "Glenmark Pharmaceuticals": "GLENMARK.NS", "GMR Airports": "GMRINFRA.NS",
        "Godrej Consumer Products": "GODREJCP.NS", "Godrej Properties": "GODREJPROP.NS",
        "Granules India": "GRANULES.NS", "Grasim Industries": "GRASIM.NS", "Gujarat Gas": "GUJGASLTD.NS",
        "Gujarat Pipavav Port": "GPPL.NS", "HAL": "HAL.NS", "Havells India": "HAVELLS.NS",
        "HCL Technologies": "HCLTECH.NS", "HDFC AMC": "HDFCAMC.NS", "HDFC Bank": "HDFCBANK.NS",
        "HDFC Life Insurance": "HDFCLIFE.NS", "Hero MotoCorp": "HEROMOTOCO.NS", "Hindustan Aeronautics": "HAL.NS",
        "Hindustan Copper": "HINDCOPPER.NS", "Hindustan Petroleum": "HINDPETRO.NS",
        "Hindustan Unilever": "HINDUNILVR.NS", "Hindustan Zinc": "HINDZINC.NS", "ICICI Bank": "ICICIBANK.NS",
        "ICICI Lombard": "ICICIGI.NS", "ICICI Prudential Life": "ICICIPRULI.NS", "IDBI Bank": "IDBI.NS",
        "IDFC First Bank": "IDFCFIRSTB.NS", "IEX": "IEX.NS", "IFCI": "IFCI.NS",
        "India Cements": "INDIACEM.NS", "Indian Bank": "INDIANB.NS", "Indian Hotels": "INDHOTEL.NS",
        "Indian Oil": "IOC.NS", "Indian Railway Catering": "IRCTC.NS", "Indraprastha Gas": "IGL.NS",
        "IndusInd Bank": "INDUSINDBK.NS", "Info Edge": "NAUKRI.NS", "Infosys": "INFY.NS",
        "Interglobe Aviation": "INDIGO.NS", "Ipca Laboratories": "IPCALAB.NS", "ITC": "ITC.NS",
        "J K Cement": "JKCEMENT.NS", "Jindal Steel Power": "JINDALSTEL.NS", "JSW Energy": "JSWENERGY.NS",
        "JSW Steel": "JSWSTEEL.NS", "Jubilant Foodworks": "JUBLFOOD.NS", "Kajaria Ceramics": "KAJARIACER.NS",
        "Kotak Mahindra Bank": "KOTAKBANK.NS", "L&T Finance": "LTF.NS", "L&T Technology Services": "LTTS.NS",
        "Larsen & Toubro": "LT.NS", "Laurus Labs": "LAURUSLABS.NS", "LIC Housing Finance": "LICHSGFIN.NS",
        "Life Insurance Corporation": "LICI.NS", "Lupin": "LUPIN.NS", "LTIMindtree": "LTIM.NS",
        "Macrotech Developers": "LODHA.NS", "Mahanagar Gas": "MGL.NS", "Mahindra & Mahindra": "M&M.NS",
        "Mahindra & Mahindra Financial": "M&MFIN.NS", "Mankind Pharma": "MANKIND.NS", "Marico": "MARICO.NS",
        "Maruti Suzuki": "MARUTI.NS", "Max Financial Services": "MFSL.NS", "Max Healthcare": "MAXHEALTH.NS",
        "Minda Industries": "MINDAIND.NS", "Mphasis": "MPHASIS.NS", "MRF": "MRF.NS",
        "Natco Pharma": "NATCOPHARM.NS", "Nestle India": "NESTLEIND.NS", "NMDC": "NMDC.NS",
        "NTPC": "NTPC.NS", "Nykaa": "NYKAA.NS", "Oil India": "OIL.NS",
        "ONGC": "ONGC.NS", "Oracle Financial Services": "OFSS.NS", "Page Industries": "PAGEIND.NS",
        "Paytm": "PAYTM.NS", "PB Fintech": "POLICYBZR.NS", "Persistent Systems": "PERSISTENT.NS",
        "Petronet LNG": "PETRONET.NS", "PI Industries": "PIIND.NS", "Pidilite Industries": "PIDILITIND.NS",
        "Power Finance Corporation": "PFC.NS", "Power Grid": "POWERGRID.NS", "Punjab National Bank": "PNB.NS",
        "Rail Vikas Nigam": "RVNL.NS", "Reliance Industries": "RELIANCE.NS", "REC": "RECLTD.NS",
        "SBI": "SBIN.NS", "SBI Cards": "SBICARD.NS", "SBI Life Insurance": "SBILIFE.NS",
        "Schaeffler India": "SCHAEFFLER.NS", "Shree Cement": "SHREECEM.NS", "Siemens": "SIEMENS.NS",
        "SRF": "SRF.NS", "Sun Pharma": "SUNPHARMA.NS", "Sun TV Network": "SUNTV.NS",
        "Sundaram Finance": "SUNDARMFIN.NS", "Sundram Fasteners": "SUNDRMFAST.NS", "Supreme Industries": "SUPREMEIND.NS",
        "Tata Chemicals": "TATACHEM.NS", "Tata Communications": "TATACOMM.NS", "Tata Consumer Products": "TATACONSUM.NS",
        "Tata Elxsi": "TATAELXSI.NS", "Tata Motors": "TATAMOTORS.NS", "Tata Power": "TATAPOWER.NS",
        "Tata Steel": "TATASTEEL.NS", "TCS": "TCS.NS", "Tech Mahindra": "TECHM.NS",
        "Thermax": "THERMAX.NS", "Titan Company": "TITAN.NS", "Torrent Pharmaceuticals": "TORNTPHARM.NS",
        "Torrent Power": "TORNTPOWER.NS", "Trent": "TRENT.NS", "Tube Investments": "TIINDIA.NS",
        "TVS Motor": "TVSMOTOR.NS", "UltraTech Cement": "ULTRACEMCO.NS", "Union Bank": "UNIONBANK.NS",
        "UPL": "UPL.NS", "Varun Beverages": "VBL.NS", "Vedanta": "VEDL.NS",
        "Voltas": "VOLTAS.NS", "Wipro": "WIPRO.NS", "Zomato": "ZOMATO.NS",
        "Zydus Lifesciences": "ZYDUSLIFE.NS", "ABB India": "ABB.NS", "ACC": "ACC.NS",
        "Affle India": "AFFLE.NS", "AGS Transact Technologies": "AGSTRA.NS", "Alembic Pharma": "APLLTD.NS",
        "Alkyl Amines": "ALKYLAMINE.NS", "Amrutanjan Health Care": "AMRUTANJAN.NS",
        "Apollo Tyres": "APOLLOTYRE.NS", "Aptus Value Housing": "APTUS.NS",
        "Archean Chemical": "ARCHEAN.NS", "Asahi India Glass": "ASAHIINDIA.NS",
        "Astra Microwave": "ASTRAMICRO.NS", "Astrazeneca Pharma": "ASTRAZEN.NS",
        "Bajaj Electricals": "BAJAJELEC.NS", "Balaji Amines": "BALAMINES.NS",
        "Balrampur Chini Mills": "BALRAMCHIN.NS", "Bandhan Bank": "BANDHANBNK.NS",
        "Bank of Maharashtra": "MAHABANK.NS", "BASF India": "BASF.NS",
        "Bata India": "BATAIND.NS", "Birlasoft": "BSOFT.NS",
        "Blue Dart Express": "BLUEDART.NS", "Blue Star": "BLUESTARCO.NS",
        "Brigade Enterprises": "BRIGADE.NS", "Carborundum Universal": "CARBORUNIV.NS",
        "Cash Urja": "CASHURJA.NS", "Ceat": "CEATLTD.NS",
        "Central Bank of India": "CENTRALBK.NS", "Century Textiles": "CENTURYTEX.NS",
        "CESC": "CESC.NS", "Chambal Fertilisers": "CHAMBLFERT.NS",
        "Chalet Hotels": "CHALET.NS", "City Union Bank": "CUB.NS",
        "Clean Science Technology": "CLEAN.NS", "Computer Age Management": "CAMS.NS",
        "Craftsman Automation": "CRAFTSMAN.NS", "Credit Access Grameen": "CREDITACC.NS",
        "CSB Bank": "CSBBANK.NS", "Cyient": "CYIENT.NS",
        "Data Patterns": "DATAPATTNS.NS", "DCB Bank": "DCBBANK.NS",
        "DCM Shriram": "DCMSHRIRAM.NS", "Deepak Fertilisers": "DEEPAKFERT.NS",
        "Dhani Services": "DHANI.NS", "Dodla Dairy": "DODLA.NS",
        "Dr Agarwals Eye Hospital": "DRAGARWAL.NS", "Edelweiss Financial": "EDELWEISS.NS",
        "Elin Electronics": "ELIN.NS", "Elgi Equipments": "ELGIEQUIP.NS",
        "Emcure Pharmaceuticals": "EMCURE.NS", "Engineers India": "ENGINERSIN.NS",
        "EPL": "EPL.NS", "Equitas Small Finance Bank": "EQUITASBNK.NS",
        "Eris Lifesciences": "ERIS.NS", "Esab India": "ESABINDIA.NS",
        "Fine Organic Industries": "FINEORG.NS", "Firstsource Solutions": "FSL.NS",
        "Fusion Micro Finance": "FUSION.NS", "Galaxy Surfactants": "GALAXYSURF.NS",
        "Garware Technical Fibres": "GARFIBRES.NS", "Gateway Distriparks": "GATEWAY.NS",
        "GE T&D India": "GET&D.NS", "GE Vernova T&D India": "GET&D.NS",
        "Global Health": "MEDANTA.NS", "Go Fashion India": "GOCOLORS.NS",
        "Godrej Agrovet": "GODREJAGRO.NS", "Godrej Industries": "GODREJIND.NS",
        "GPT Infraprojects": "GPTINFRA.NS", "Greenpanel Industries": "GREENPANEL.NS",
        "Grindwell Norton": "GRINDWELL.NS", "Happiest Minds": "HAPPSTMNDS.NS",
        "Harsha Engineers": "HARSHA.NS", "HLE Glascoat": "HLEGLAS.NS",
        "Home First Finance": "HOMEFIRST.NS", "Honda India Power": "HONDAPOWER.NS",
        "HUDCO": "HUDCO.NS", "ICICI Securities": "ISEC.NS",
        "IIFL Finance": "IIFL.NS", "IIFL Securities": "IIFLSEC.NS",
        "Indian Energy Exchange": "IEX.NS", "Indian Overseas Bank": "IOB.NS",
        "Indigo Paints": "INDIGOPNTS.NS", "Indus Towers": "INDUSTOWER.NS",
        "Inox Green Energy": "INOXGREEN.NS", "Inox Wind": "INOXWIND.NS",
        "Institute of Company Secretaries": "ICSI.NS", "Intellect Design Arena": "INTELLECT.NS",
        "IOB": "IOB.NS", "IRFC": "IRFC.NS",
        "ITI": "ITI.NS", "Ixigo": "IXIGO.NS",
        "J B Chemicals": "JBCHEPHARM.NS", "Jio Financial Services": "JIOFIN.NS",
        "JSW Infrastructure": "JSWINFRA.NS", "Just Dial": "JUSTDIAL.NS",
        "Kalpataru Projects": "KPIL.NS", "Kansai Nerolac Paints": "KANSAINER.NS",
        "Karnataka Bank": "KTKBANK.NS", "KEC International": "KEC.NS",
        "Kewal Kiran Clothing": "KEWAL.NS", "Kirloskar Brothers": "KIRLOSBROS.NS",
        "Kirloskar Oil Engines": "KIRLOSENG.NS", "KPIT Technologies": "KPITTECH.NS",
        "KSB": "KSB.NS", "Ksolves India": "KSOLVES.NS",
        "La Opala RG": "LAOPALA.NS", "Laxmi Organic Industries": "LXCHEM.NS",
        "Lloyds Metals": "LLOYDMETAL.NS", "Lotus Chocolate": "LOTUSCHOC.NS",
        "Mahindra Logistics": "MAHLOG.NS", "Manorama Industries": "MANORAMA.NS",
        "Matrimony.com": "MATRIMONY.NS", "MCX India": "MCX.NS",
        "Metro Brands": "METROBRAND.NS", "Minda Corporation": "MINDACORP.NS",
        "Mirae Asset": "MIRAEASSET.NS", "MMTC": "MMTC.NS",
        "Motherson Sumi Wiring": "MSUMI.NS", "Mtar Technologies": "MTARTECH.NS",
        "Multi Commodity Exchange": "MCX.NS", "Narayana Hrudayalaya": "NH.NS",
        "National Aluminium": "NATIONALUM.NS", "Nazara Technologies": "NAZARA.NS",
        "Neogen Chemicals": "NEOGEN.NS", "NHPC": "NHPC.NS",
        "NLC India": "NLCINDIA.NS", "NMDC Steel": "NMDCSTEEL.NS",
        "Nocil": "NOCIL.NS", "NSDL": "NSDL.NS",
        "NTPC Green Energy": "NTPCGREEN.NS", "Oberoi Realty": "OBEROIRLTY.NS",
        "Oil & Natural Gas Corporation": "ONGC.NS", "Olectra Greentech": "OLECTRA.NS",
        "One 97 Communications": "PAYTM.NS", "Orient Electric": "ORIENTELEC.NS",
        "Orient Technologies": "ORIENTTECH.NS", "Piramal Enterprises": "PEL.NS",
        "Piramal Pharma": "PPLPHARMA.NS", "PNB Housing Finance": "PNBHOUSING.NS",
        "Poly Medicure": "POLYMED.NS", "Praj Industries": "PRAJIND.NS",
        "Prince Pipes": "PRINCEPIPE.NS", "Prism Johnson": "PRSMJOHNSN.NS",
        "Procter & Gamble Hygiene": "PGHH.NS", "PSP Projects": "PSPPROJECT.NS",
        "Punjab & Sind Bank": "PSB.NS", "Radico Khaitan": "RADICO.NS",
        "Rainbow Childrens Medicare": "RAINBOW.NS", "Rallis India": "RALLIS.NS",
        "Rane Holdings": "RANEHOLDIN.NS", "Raymond": "RAYMOND.NS",
        "RBL Bank": "RBLBANK.NS", "Redington": "REDINGTON.NS",
        "Relaxo Footwears": "RELAXO.NS", "Rites": "RITES.NS",
        "Rossari Biotech": "ROSSARI.NS", "Route Mobile": "ROUTE.NS",
        "Safari Industries": "SAFARI.NS", "Samvardhana Motherson": "MOTHERSON.NS",
        "Sapphire Foods": "SAPPHIRE.NS", "Saregama India": "SAREGAMA.NS",
        "Sbi Cards And Payment": "SBICARD.NS", "Sequent Scientific": "SEQUENT.NS",
        "Shriram Finance": "SHRIRAMFIN.NS", "Signature Global": "SIGNATURE.NS",
        "Sintercom India": "SINTERCOM.NS", "SKF India": "SKFINDIA.NS",
        "Solar Industries India": "SOLARINDS.NS", "Solara Active Pharma": "SOLARA.NS",
        "Sona BLW Precision": "SONACOMS.NS", "Spandana Sphoorty": "SPANDANA.NS",
        "Speciality Restaurants": "SPECIALITY.NS", "Star Health Insurance": "STARHEALTH.NS",
        "Steel Authority of India": "SAIL.NS", "Sterlite Technologies": "STLTECH.NS",
        "Stylam Industries": "STYLAMIND.NS", "Sudarshan Chemical": "SUDARSCHEM.NS",
        "Suven Pharmaceuticals": "SUVENPHAR.NS", "Swan Energy": "SWANENERGY.NS",
        "Syngene International": "SYNGENE.NS", "Tamil Nadu Newsprint": "TNPL.NS",
        "Tanla Platforms": "TANLA.NS", "Tata Investment Corporation": "TATAINVEST.NS",
        "Tata Technologies": "TATATECH.NS", "Team Lease Services": "TEAMLEASE.NS",
        "Thomas Cook India": "THOMASCOOK.NS", "Timken India": "TIMKEN.NS",
        "Tips Industries": "TIPSINDLTD.NS", "Titagarh Rail Systems": "TITAGARH.NS",
        "Torrent Power": "TORNTPOWER.NS", "Trident": "TRIDENT.NS",
        "Triveni Engineering": "TRIVENI.NS", "Triveni Turbine": "TRITURBINE.NS",
        "UCO Bank": "UCOBANK.NS", "UFO Moviez": "UFOVMOVIEZ.NS",
        "Ugro Capital": "UGROCAP.NS", "Ujjivan Financial Services": "UJJIVAN.NS",
        "Ujjivan Small Finance Bank": "UJJIVANSFB.NS", "United Breweries": "UBL.NS",
        "United Spirits": "MCDOWELL-N.NS", "Uno Minda": "UNOMINDA.NS",
        "UTI AMC": "UTIAMC.NS", "VA Tech Wabag": "WABAG.NS",
        "Vardhman Textiles": "VTL.NS", "Varroc Engineering": "VARROC.NS",
        "Venus Pipes": "VENUSPIPES.NS", "Vijaya Diagnostic": "VIJAYA.NS",
        "Vinati Organics": "VINATIORGA.NS", "Vishnu Chemicals": "VISHNU.NS",
        "Vishal Mega Mart": "VISHALMEGA.NS", "Welspun Corp": "WELCORP.NS",
        "Welspun Living": "WELSPUNLIV.NS", "West Coast Paper": "WESTCOAST.NS",
        "Whirlpool India": "WHIRLPOOL.NS", "Wipro": "WIPRO.NS",
        "WNS Holdings": "WNS.NS", "Wockhardt": "WOCKPHARMA.NS",
        "Zensar Technologies": "ZENSARTECH.NS", "Zee Entertainment": "ZEEL.NS",
    }
    return {"stocks": stocks}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        df = fetch_stock_data(req.ticker, period=req.period)
        df = compute_returns(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch data for {req.ticker}. Yahoo Finance may not have data for this stock. Try a different ticker or period.")

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
                    "Be concise and clear. Plain language only. No markdown, no asterisks.\n"
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
            "Respond in this exact structure with NO asterisks or markdown:\n\n"
            "What this means\n"
            "[2-3 plain English sentences]\n\n"
            "Bull Case\n"
            "[2-3 reasons to consider buying/holding]\n\n"
            "Bear Case\n"
            "[2-3 reasons to be cautious]\n\n"
            "Signal\n"
            "[Buy / Hold / Sell - one sentence reason]\n\n"
            "Portfolio Tip\n"
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
                "Give a concise earnings analysis with these sections: Earnings Health, Strengths, Concerns, Valuation, Bottom Line.\n"
                "Simple language. No asterisks or markdown formatting."
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