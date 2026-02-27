import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import requests
from datetime import datetime, timedelta
import time

# ─────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Islamic Profit Benchmark System",
    page_icon="☪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Hide ALL Streamlit chrome (menu, footer, toolbar, deploy button) ──
st.markdown("""
<style>
  /* Top-right hamburger menu */
  #MainMenu { visibility: hidden !important; display: none !important; }

  /* "Made with Streamlit" footer */
  footer { visibility: hidden !important; display: none !important; }

  /* Top header bar (contains Deploy button, etc.) */
  header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; }

  /* Toolbar (View fullscreen, rerun, etc.) */
  [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

  /* Top-right action buttons (Share, star, etc.) */
  [data-testid="stActionButtonIcon"] { visibility: hidden !important; display: none !important; }
  .stActionButton { visibility: hidden !important; display: none !important; }

  /* Deploy / Manage app button */
  [data-testid="stAppDeployButton"] { visibility: hidden !important; display: none !important; }

  /* Bottom status bar */
  [data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }

  /* Floating bottom-right Streamlit badge */
  [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }

  /* Remove top padding that the hidden header would leave */
  .block-container { padding-top: 1rem !important; }
  [data-testid="stAppViewContainer"] > section:first-child { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #060e1a 0%, #0a1628 60%, #060e1a 100%);
    color: #e8d5a3;
}

/* ── Header ─────────── */
.main-header {
    background: linear-gradient(90deg, #071a10, #0d3b2e, #071a10);
    border: 1px solid #c9a84c;
    border-radius: 12px;
    padding: 22px 32px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 0 50px rgba(201,168,76,0.12);
}
.main-header h1 { font-family:'Amiri',serif; color:#c9a84c; font-size:2.2rem; margin:0; }
.main-header p  { color:#7ab890; font-size:0.9rem; margin:6px 0 0 0; }

/* ── Section titles ──── */
.sec-title {
    font-family:'Amiri',serif; color:#c9a84c; font-size:1.3rem;
    border-bottom:1px solid #2a6b47; padding-bottom:6px; margin:18px 0 12px 0;
}

/* ── KPI cards ─────── */
.kpi-card {
    background: linear-gradient(135deg,#0d2b1e,#143d2b);
    border:1px solid #2a6b47; border-radius:10px;
    padding:18px; text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.35);
}
.kpi-val  { font-size:2rem; font-weight:700; }
.kpi-lbl  { font-size:0.75rem; color:#7ab890; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }
.kpi-src  { font-size:0.68rem; color:#2a6b47; margin-top:3px; }

/* ── Info box ─────── */
.info-box {
    background:rgba(13,59,46,0.35); border-left:4px solid #c9a84c;
    border-radius:0 8px 8px 0; padding:12px 16px; margin:10px 0;
    color:#d4c4a0; font-size:0.88rem;
}
.warn-box {
    background:rgba(231,76,60,0.08); border-left:4px solid #e74c3c;
    border-radius:0 8px 8px 0; padding:12px 16px; margin:10px 0;
    color:#d4c4a0; font-size:0.88rem;
}
.good-box {
    background:rgba(46,204,113,0.08); border-left:4px solid #2ecc71;
    border-radius:0 8px 8px 0; padding:12px 16px; margin:10px 0;
    color:#d4c4a0; font-size:0.88rem;
}

/* ── Ayah / verse box ─ */
.ayah-box {
    background:linear-gradient(135deg,#060e1a,#0d2b1e);
    border:1px solid #c9a84c; border-radius:10px;
    padding:18px 24px; text-align:center; margin:12px 0;
}
.ayah-arabic { font-family:'Amiri',serif; font-size:1.4rem; color:#c9a84c; direction:rtl; line-height:2; }
.ayah-trans  { color:#a8c5b0; font-size:0.82rem; margin-top:6px; font-style:italic; }

/* ── Sidebar ─────────── */
section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#060e1a,#0a1f30);
    border-right:1px solid #2a6b47;
}
section[data-testid="stSidebar"] .stMarkdown h3 { color:#c9a84c; font-family:'Amiri',serif; }

/* ── Tabs ─────────────── */
.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid #2a6b47; }
.stTabs [data-baseweb="tab"]      { color:#7ab890; font-family:'Cairo',sans-serif; font-size:0.88rem; }
.stTabs [aria-selected="true"]    { color:#c9a84c !important; border-bottom:2px solid #c9a84c !important; }

/* ── Buttons ─────────── */
.stButton > button {
    background:linear-gradient(90deg,#1a5c40,#0d7a52);
    color:#fff; border:1px solid #c9a84c; border-radius:8px;
    font-family:'Cairo',sans-serif; font-weight:600;
    padding:9px 22px; transition:all 0.25s;
}
.stButton > button:hover {
    background:linear-gradient(90deg,#c9a84c,#a8882e);
    color:#060e1a; border-color:#c9a84c;
}

/* ── Sliders / selects ── */
.stSelectbox>div>div, .stMultiSelect>div>div, .stNumberInput>div>div {
    background:#0d2137 !important; border-color:#2a6b47 !important; color:#e8d5a3 !important;
}
.stSlider .rc-slider-track { background:#c9a84c !important; }
.stSlider .rc-slider-handle { background:#c9a84c !important; border-color:#c9a84c !important; }

/* ── Year badge ────── */
.year-badge {
    display:inline-block;
    background:linear-gradient(90deg,#0d3b2e,#1a5c40);
    border:1px solid #c9a84c; border-radius:20px;
    padding:4px 16px; color:#c9a84c; font-weight:700; font-size:1rem;
}

/* ── Metric delta ───── */
.delta-red  { color:#e74c3c; font-weight:700; }
.delta-grn  { color:#2ecc71; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
#  RESEARCH DATA  (Published figures, no API needed)
# ─────────────────────────────────────────────────────────────────────

SECTORS_DATA = [
    {"id":"wheat",   "name":"Wheat Farming",    "icon":"🌾","cat":"Agriculture",
     "islamic":20.56,"kibor":17.22,"real_return":6.25, "benchmark":7.75,
     "borrower":"Small Farmer",    "overcharge":12.81,
     "context":"Agriculture grew 6.25% in FY2024. Wheat output rose 11.6% to 31.44M tonnes. "
               "Yet farmers pay 20.56% — over 3× their sector's actual return.",
     "source":"Pakistan Economic Survey FY2024"},
    {"id":"textile", "name":"Textile Industry", "icon":"🧵","cat":"Industry",
     "islamic":21.25,"kibor":17.22,"real_return":12.00,"benchmark":13.50,
     "borrower":"SME Manufacturer","overcharge":7.75,
     "context":"Pakistan's largest export earner. Sector returns ~12% but SMEs are charged 21.25% — "
               "KIBOR+4.5%, identical to conventional bank rates.",
     "source":"SBP Islamic Banking Bulletin 2024"},
    {"id":"realestate","name":"Real Estate",    "icon":"🏗️","cat":"Real Estate",
     "islamic":20.56,"kibor":17.22,"real_return":14.00,"benchmark":15.50,
     "borrower":"Home Buyer",       "overcharge":5.06,
     "context":"Meezan Bank's Diminishing Musharakah home financing averages 20.56%. "
               "Real estate sector returns ~14% — gap is 6.5 percentage points.",
     "source":"Meezan Bank Profit Rate Disclosures Sep 2024"},
    {"id":"auto",    "name":"Car Financing",    "icon":"🚗","cat":"Consumer",
     "islamic":21.25,"kibor":17.22,"real_return":10.50,"benchmark":12.00,
     "borrower":"Consumer",         "overcharge":9.25,
     "context":"Average Islamic car financing at 21.25% aligns with conventional KIBOR+4.5%. "
               "Auto sector margin ~10.5% — proving no genuine differentiation.",
     "source":"Profit by Pakistan Today, Sep 2024"},
    {"id":"dairy",   "name":"Dairy & Livestock","icon":"🐄","cat":"Agriculture",
     "islamic":20.56,"kibor":17.22,"real_return":8.50, "benchmark":10.00,
     "borrower":"Livestock Farmer", "overcharge":10.56,
     "context":"Cattle industry expanded 4.72% in FY2025. Livestock farmers pay the same 20.56% "
               "as corporate clients regardless of their sector's actual performance.",
     "source":"Pakistan Economic Survey FY2025"},
    {"id":"sme",     "name":"SME / Trade",      "icon":"🏪","cat":"Services",
     "islamic":20.56,"kibor":17.22,"real_return":13.00,"benchmark":14.50,
     "borrower":"Small Business",   "overcharge":6.06,
     "context":"Services sector grew 2.91% of GDP in FY2025. SMEs are charged full KIBOR-linked "
               "rates with no sector-specific consideration.",
     "source":"SBP SME Finance Review 2024"},
]

HISTORY_DATA = [
    {"year":2020,"kibor":7.00, "islamic_avg":8.50, "sector_return":3.90, "gdp_growth":3.9,  "inflation":10.7},
    {"year":2021,"kibor":7.00, "islamic_avg":8.20, "sector_return":5.50, "gdp_growth":5.5,  "inflation":8.9},
    {"year":2022,"kibor":13.75,"islamic_avg":15.75,"sector_return":6.10, "gdp_growth":6.1,  "inflation":12.2},
    {"year":2023,"kibor":22.00,"islamic_avg":22.80,"sector_return":2.40, "gdp_growth":2.4,  "inflation":29.2},
    {"year":2024,"kibor":17.22,"islamic_avg":20.56,"sector_return":6.25, "gdp_growth":6.25, "inflation":23.4},
    {"year":2025,"kibor":10.50,"islamic_avg":13.50,"sector_return":4.50, "gdp_growth":4.5,  "inflation":7.2},
]

YAHOO_SECTORS = {
    "Agriculture":       {"Wheat & Grains":["ADM","INGR","MOS"],"Dairy & Livestock":["TSN","HRL","SAFM"]},
    "Industry":          {"Textile":["HBI","PVH","RL"],"Construction":["VMC","MLM","USCR"]},
    "Technology":        {"Software & SaaS":["MSFT","CRM","NOW"],"IT Services":["ACN","INFY","WIT"]},
    "Healthcare":        {"Pharma":["JNJ","PFE","ABBV"],"Devices":["MDT","ABT","SYK"]},
    "Real Estate":       {"Residential":["DHI","LEN","PHM"],"Commercial":["SPG","O","PLD"]},
    "Energy":            {"Renewables":["ENPH","FSLR","RUN"],"Power":["NEE","DUK","SO"]},
    "Trade & Retail":    {"Consumer":["PG","KO","UL"],"Retail":["WMT","TGT","COST"]},
}

REASONS_WHY = [
    ("The IIBR Attempt Failed (2011–2015)",
     "In 2011, Thomson Reuters and 17 Islamic banks launched the Islamic Interbank Benchmark Rate (IIBR). "
     "Research proved it 'fails to decouple from LIBOR' — it was statistically identical to conventional rates "
     "and was quietly discontinued by 2015."),
    ("Trapped in Conventional Infrastructure",
     "Islamic banks were born inside conventional banking systems — same central bank accounts, interbank "
     "payment rails, and regulatory frameworks. Building an independent system required sovereign commitment "
     "that no Muslim-majority government delivered."),
    ("Scholars 'Halalized' the Problem",
     "Rather than demanding reform, many Shariah board scholars approved KIBOR-linked pricing as permissible. "
     "With a theological cover provided, banks had no urgency to innovate."),
    ("Competitive Market Pressure",
     "If an Islamic bank charges 8% (true sector rate) while conventional banks offer depositors 18–20%, "
     "depositors flee. Banks are forced to match conventional rates to survive commercially."),
    ("No Political Will",
     "Despite growing to $4 trillion globally, no Muslim-majority government mandated an independent "
     "benchmark — until Pakistan's Federal Shariat Court set the 2027 deadline."),
    ("Data Infrastructure Was Missing",
     "Until recently there was no system to aggregate real-time sector returns to generate credible "
     "alternative benchmarks. Online data availability now makes this fully viable."),
]

# ─────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────

def monthly_payment(principal, annual_rate, months):
    r = annual_rate / 100 / 12
    if r == 0:
        return principal / months
    return principal * (r * (1 + r)**months) / ((1 + r)**months - 1)

def total_profit(principal, annual_rate, months):
    return monthly_payment(principal, annual_rate, months) * months - principal

def make_chart_layout(height=400, margin=None):
    m = margin or dict(t=30, b=40, l=10, r=10)
    return dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8d5a3', family='Cairo'),
        height=height,
        margin=m,
        xaxis=dict(gridcolor='#1a3a2a', tickfont=dict(color='#7ab890')),
        yaxis=dict(gridcolor='#1a3a2a', tickfont=dict(color='#7ab890')),
        legend=dict(bgcolor='rgba(10,22,40,0.8)', bordercolor='#2a6b47', borderwidth=1,
                    font=dict(color='#e8d5a3')),
    )

@st.cache_data(ttl=3600)
def fetch_sector_live(tickers, period="1y"):
    results = {}
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period=period)
            if len(hist) > 20:
                ret = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                vol = hist['Close'].pct_change().dropna().std() * np.sqrt(252) * 100
                results[ticker] = {"return": ret, "volatility": vol, "price": hist['Close'].iloc[-1]}
        except:
            pass
    return results

@st.cache_data(ttl=3600)
def fetch_world_bank(indicator, country="PK"):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv=6"
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
        if len(data) > 1 and data[1]:
            return [(d['date'], d['value']) for d in data[1] if d['value'] is not None]
    except:
        pass
    return []

# ─────────────────────────────────────────────────────────────────────
#  PLOTLY CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────

def build_comparison_chart(sectors, show_kibor=True):
    labels = [s['name'] for s in sectors]
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Islamic Bank Rate", x=labels,
        y=[s['islamic'] for s in sectors],
        marker_color='#e74c3c', marker_line_width=0,
        text=[f"{s['islamic']:.1f}%" for s in sectors],
        textposition='outside', textfont=dict(color='#ff9999', size=10),
    ))
    fig.add_trace(go.Bar(
        name="Real Sector Return", x=labels,
        y=[s['real_return'] for s in sectors],
        marker_color='#2ecc71', marker_line_width=0,
        text=[f"{s['real_return']:.1f}%" for s in sectors],
        textposition='outside', textfont=dict(color='#a8e8b8', size=10),
    ))
    fig.add_trace(go.Bar(
        name="Proposed Benchmark", x=labels,
        y=[s['benchmark'] for s in sectors],
        marker_color='#c9a84c', marker_line_width=0,
        text=[f"{s['benchmark']:.1f}%" for s in sectors],
        textposition='outside', textfont=dict(color='#e8d5a3', size=10),
    ))

    if show_kibor:
        fig.add_hline(y=17.22, line_dash="dash", line_color="#e67e22", line_width=1.5,
                      annotation_text="KIBOR 17.22%",
                      annotation_font_color="#e67e22", annotation_font_size=10)

    layout = make_chart_layout(400)
    layout['barmode'] = 'group'
    layout['yaxis']['title'] = "Rate (%)"
    layout['yaxis']['range'] = [0, 28]
    layout['bargap'] = 0.25
    layout['bargroupgap'] = 0.08
    fig.update_layout(**layout)
    return fig


def build_history_chart(years, show_multiplier=False):
    df = pd.DataFrame([h for h in HISTORY_DATA if h['year'] in years])
    if df.empty:
        return go.Figure()

    if show_multiplier:
        df['multiplier'] = df['islamic_avg'] / df['sector_return']
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Rates Over Time", "Bank Rate / Sector Return (Multiplier)"])
        fig.add_trace(go.Scatter(x=df['year'], y=df['islamic_avg'], name="Islamic Bank Rate",
                                 line=dict(color='#e74c3c', width=2.5), mode='lines+markers',
                                 marker=dict(size=7)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['year'], y=df['kibor'], name="KIBOR",
                                 line=dict(color='#e67e22', width=2, dash='dot'), mode='lines+markers',
                                 marker=dict(size=5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['year'], y=df['sector_return'], name="Real Sector Return",
                                 line=dict(color='#2ecc71', width=2.5), mode='lines+markers',
                                 marker=dict(size=7)), row=1, col=1)
        fig.add_trace(go.Bar(x=df['year'], y=df['multiplier'], name="Multiplier",
                             marker_color=['#e74c3c' if v > 3 else '#e67e22' if v > 2 else '#2ecc71'
                                          for v in df['multiplier']],
                             text=[f"{v:.1f}×" for v in df['multiplier']],
                             textposition='outside', textfont=dict(color='#e8d5a3')), row=1, col=2)
        fig.add_hline(y=1.0, line_dash="dash", line_color="#2ecc71", row=1, col=2,
                      annotation_text="Fair (1×)", annotation_font_color="#2ecc71")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['year'], y=df['islamic_avg'], name="Islamic Bank Rate",
                                 line=dict(color='#e74c3c', width=2.5), mode='lines+markers',
                                 marker=dict(size=8, symbol='circle')))
        fig.add_trace(go.Scatter(x=df['year'], y=df['kibor'], name="KIBOR",
                                 line=dict(color='#e67e22', width=2, dash='dot'), mode='lines+markers',
                                 marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=df['year'], y=df['sector_return'], name="Real Sector Return",
                                 line=dict(color='#2ecc71', width=2.5), mode='lines+markers',
                                 fill='tozeroy', fillcolor='rgba(46,204,113,0.06)',
                                 marker=dict(size=8, symbol='circle')))
        fig.add_trace(go.Scatter(x=df['year'], y=df['inflation'], name="Inflation",
                                 line=dict(color='#9b59b6', width=1.5, dash='dash'), mode='lines+markers',
                                 marker=dict(size=5)))

    layout = make_chart_layout(380, margin=dict(t=40, b=40, l=10, r=10))
    fig.update_layout(**layout)
    return fig


def build_borrower_impact(sectors, principal, months):
    data = []
    for s in sectors:
        m_islamic = monthly_payment(principal, s['islamic'], months)
        m_bench   = monthly_payment(principal, s['benchmark'], months)
        saving    = (m_islamic - m_bench) * months
        data.append({"Sector": s['name'],
                     "Islamic Bank Total": m_islamic * months,
                     "Benchmark Total":   m_bench   * months,
                     "Saving": saving})

    fig = go.Figure()
    labels = [d['Sector'] for d in data]
    fig.add_trace(go.Bar(name="Islamic Bank Total", x=labels,
                         y=[d['Islamic Bank Total'] for d in data],
                         marker_color='#e74c3c',
                         text=[f"PKR {d['Islamic Bank Total']:,.0f}" for d in data],
                         textposition='outside', textfont=dict(color='#ff9999', size=9)))
    fig.add_trace(go.Bar(name="Benchmark Total", x=labels,
                         y=[d['Benchmark Total'] for d in data],
                         marker_color='#2ecc71',
                         text=[f"PKR {d['Benchmark Total']:,.0f}" for d in data],
                         textposition='outside', textfont=dict(color='#a8e8b8', size=9)))

    layout = make_chart_layout(380)
    layout['barmode'] = 'group'
    layout['yaxis']['title'] = "Total Repayment (PKR)"
    layout['yaxis']['tickformat'] = ",.0f"
    layout['bargap'] = 0.25
    fig.update_layout(**layout)
    return fig, data


def build_overcharge_gauge(avg_overcharge):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_overcharge,
        number={'suffix': "%", 'font': {'color': '#e74c3c', 'size': 36}},
        delta={'reference': 0, 'valueformat': ".1f", 'suffix': "% above fair rate",
               'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 20], 'tickcolor': '#7ab890'},
            'bar': {'color': '#e74c3c'},
            'bgcolor': '#0d2137',
            'bordercolor': '#2a6b47',
            'steps': [
                {'range': [0,   5],  'color': '#0a2b1e'},
                {'range': [5,  10],  'color': '#1a3b10'},
                {'range': [10, 15],  'color': '#3b1a0a'},
                {'range': [15, 20],  'color': '#3b0a0a'},
            ],
            'threshold': {'line': {'color': '#c9a84c', 'width': 3}, 'value': avg_overcharge},
        },
        title={'text': "Avg. Overcharge Above Fair Rate", 'font': {'color': '#c9a84c', 'size': 13}},
    ))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      height=240, margin=dict(t=30, b=10, l=30, r=30),
                      font=dict(color='#e8d5a3'))
    return fig


# ─────────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>☪️ Islamic Profit Benchmark System</h1>
  <p>Real-Time, Data-Driven Halal Finance — Independent of Interest-Based Rates | Pakistan 2024–25</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
#  SIDEBAR — GLOBAL CONTROLS
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☪️ Global Controls")
    st.markdown("---")

    st.markdown("#### 🏭 Sector Filter")
    all_sector_names = [s['name'] for s in SECTORS_DATA]
    selected_sectors = st.multiselect(
        "Select sectors to display",
        options=all_sector_names,
        default=all_sector_names,
        key="sector_filter"
    )
    if not selected_sectors:
        selected_sectors = all_sector_names

    st.markdown("#### 📅 Year Range")
    all_years = [h['year'] for h in HISTORY_DATA]
    year_range = st.select_slider(
        "Historical period",
        options=all_years,
        value=(all_years[0], all_years[-1]),
        key="year_range"
    )
    selected_years = list(range(year_range[0], year_range[1] + 1))

    st.markdown("#### 💰 Financing Parameters")
    loan_amount = st.number_input("Loan Amount (PKR)", min_value=100000,
                                   max_value=50000000, value=1000000, step=100000,
                                   format="%d")
    loan_tenure = st.slider("Tenure (Months)", 12, 240, 60, 6)
    admin_buffer = st.slider("Admin Buffer (%)", 0.5, 3.0, 1.5, 0.1)

    st.markdown("#### 📊 Chart Options")
    show_kibor_line = st.checkbox("Show KIBOR reference line", value=True)
    show_multiplier = st.checkbox("Show overcharge multiplier chart", value=True)

    st.markdown("---")
    st.markdown("""
    <div class="ayah-box">
      <div class="ayah-arabic">وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا</div>
      <div class="ayah-trans">"Allah has permitted trade and forbidden interest" — Al-Baqarah 2:275</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🌍 Live Data Settings")
    api_period = st.selectbox("API data period", ["3mo","6mo","1y","2y"], index=2)
    country_code = st.selectbox("World Bank country", ["PK","MY","SA","AE","BD","WLD"], index=0)


# ─────────────────────────────────────────────────────────────────────
#  FILTER DATA BY SIDEBAR SELECTIONS
# ─────────────────────────────────────────────────────────────────────
filtered_sectors = [s for s in SECTORS_DATA if s['name'] in selected_sectors]
filtered_history = [h for h in HISTORY_DATA if h['year'] in selected_years]

avg_islamic   = np.mean([s['islamic']     for s in filtered_sectors])
avg_return    = np.mean([s['real_return'] for s in filtered_sectors])
avg_benchmark = np.mean([s['benchmark']   for s in filtered_sectors])
avg_overcharge= avg_islamic - avg_benchmark


# ─────────────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Full Report",
    "📅 Year Analysis",
    "📊 Live Benchmarks",
    "🔍 Sector Deep Dive",
    "💰 Calculator",
    "📖 Islamic Finance Guide",
])


# ═══════════════════════════════════════════════════════════════════
#  TAB 1 — FULL REPORT  (Responds to all sidebar controls)
# ═══════════════════════════════════════════════════════════════════
with tab1:

    # ── KPI Row ──────────────────────────────────────────────────
    st.markdown('<div class="sec-title">📊 Executive Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (f"{avg_islamic:.2f}%",   "Avg Islamic Bank Rate",  "#e74c3c", "KIBOR-linked financing rate"),
        (f"{17.22:.2f}%",         "KIBOR Reference",         "#e67e22", "Jul 2024 Ijarah Sukuk"),
        (f"{avg_return:.2f}%",    "Avg Sector Return",       "#2ecc71", "Actual economic performance"),
        (f"{avg_benchmark:.2f}%", "Proposed Benchmark",      "#c9a84c", "Sector return + admin buffer"),
        (f"+{avg_overcharge:.2f}%","Avg Overcharge Gap",     "#ff6b6b", "Bank rate minus fair rate"),
    ]
    for col, (val, lbl, color, src) in zip([c1,c2,c3,c4,c5], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-val" style="color:{color}">{val}</div>
              <div class="kpi-lbl">{lbl}</div>
              <div class="kpi-src">{src}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Warning banner ───────────────────────────────────────────
    st.markdown(f"""
    <div class="warn-box">
    <b>🔬 Research-Proven Finding:</b>
    A 100 basis point rise in KIBOR leads to a 100 basis point increase in Islamic bank lending rates —
    <b>complete pass-through</b> (Emerald IMEFM Journal, 2025).
    This means Islamic bank profit rates are structurally <i>identical</i> to conventional interest rates.
    Currently showing <b>{len(filtered_sectors)} sector(s)</b> for years <b>{year_range[0]}–{year_range[1]}</b>.
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: Rate Comparison Chart ────────────────────────
    st.markdown('<div class="sec-title">1. Rate Comparison by Sector</div>', unsafe_allow_html=True)

    col_chart, col_gauge = st.columns([2, 1])
    with col_chart:
        fig_comp = build_comparison_chart(filtered_sectors, show_kibor=show_kibor_line)
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_gauge:
        st.markdown("<br>", unsafe_allow_html=True)
        fig_gauge = build_overcharge_gauge(avg_overcharge)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"""
        <div class="warn-box" style="text-align:center">
          <b style="font-size:1.1rem; color:#e74c3c">{avg_overcharge:.1f}%</b><br>
          <span style="font-size:0.8rem">Average extra cost paid by borrowers<br>above a fair sector benchmark</span>
        </div>""", unsafe_allow_html=True)

    # ── Section 2: Detailed Comparison Table ────────────────────
    st.markdown('<div class="sec-title">2. Sector-by-Sector Detailed Comparison</div>',
                unsafe_allow_html=True)

    df_display = pd.DataFrame([{
        "Sector":            f"{s['icon']} {s['name']}",
        "Category":          s['cat'],
        "Borrower Type":     s['borrower'],
        "Islamic Bank Rate": s['islamic'],
        "KIBOR Ref.":        s['kibor'],
        "Real Sector Return":s['real_return'],
        "Proposed Benchmark":s['benchmark'],
        "Overcharge (+%)":   s['overcharge'],
    } for s in filtered_sectors])

    # Color the dataframe
    def color_rate(val):
        if isinstance(val, float):
            if val > 18:  return 'color: #e74c3c; font-weight: bold'
            elif val > 12: return 'color: #e67e22'
            else:          return 'color: #2ecc71; font-weight: bold'
        return ''

    def color_overcharge(val):
        if isinstance(val, float) and val > 0:
            return f'color: #e74c3c; font-weight: bold'
        return 'color: #2ecc71'

    styled = (df_display.style
              .applymap(color_rate, subset=['Islamic Bank Rate','Real Sector Return','Proposed Benchmark'])
              .applymap(color_overcharge, subset=['Overcharge (+%)'])
              .format({
                  'Islamic Bank Rate':  '{:.2f}%',
                  'KIBOR Ref.':         '{:.2f}%',
                  'Real Sector Return': '{:.2f}%',
                  'Proposed Benchmark': '{:.2f}%',
                  'Overcharge (+%)':    '+{:.2f}%',
              })
              .set_properties(**{'background-color': '#0a1628', 'color': '#e8d5a3',
                                 'border-color': '#2a6b47'})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Average row
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div style="background:#1a0808;border:1px solid #e74c3c;border-radius:8px;
                    padding:12px;text-align:center">
          <div style="color:#e74c3c;font-size:1.5rem;font-weight:700">{avg_islamic:.2f}%</div>
          <div style="color:#a87070;font-size:0.78rem">Average Islamic Bank Rate</div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div style="background:#081a08;border:1px solid #2ecc71;border-radius:8px;
                    padding:12px;text-align:center">
          <div style="color:#2ecc71;font-size:1.5rem;font-weight:700">{avg_return:.2f}%</div>
          <div style="color:#6a9070;font-size:0.78rem">Average Real Sector Return</div>
        </div>""", unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div style="background:#1a1505;border:1px solid #c9a84c;border-radius:8px;
                    padding:12px;text-align:center">
          <div style="color:#c9a84c;font-size:1.5rem;font-weight:700">{avg_benchmark:.2f}%</div>
          <div style="color:#8a7050;font-size:0.78rem">Average Proposed Benchmark</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 3: Historical Trend ──────────────────────────────
    st.markdown('<div class="sec-title">3. Historical Rate Trends</div>', unsafe_allow_html=True)

    if filtered_history:
        fig_hist = build_history_chart(selected_years, show_multiplier=show_multiplier)
        st.plotly_chart(fig_hist, use_container_width=True)

        # Historical table
        df_hist = pd.DataFrame(filtered_history)
        df_hist['gap']        = df_hist['islamic_avg'] - df_hist['sector_return']
        df_hist['multiplier'] = (df_hist['islamic_avg'] / df_hist['sector_return']).round(1)
        df_hist.columns = ['Year','KIBOR','Islamic Avg Rate','Sector Return','GDP Growth','Inflation',
                            'Gap (Bank−Sector)','Multiplier']
        df_hist_styled = (df_hist.style
            .applymap(lambda v: 'color:#e74c3c;font-weight:bold' if isinstance(v,float) and v>=20 else
                                'color:#e67e22' if isinstance(v,float) and v>=15 else
                                'color:#2ecc71' if isinstance(v,float) and v<=8 else '',
                      subset=['KIBOR','Islamic Avg Rate','Sector Return'])
            .applymap(lambda v: 'color:#e74c3c;font-weight:bold' if isinstance(v,(int,float)) and v>=3 else
                                'color:#e67e22' if isinstance(v,(int,float)) and v>=2 else
                                'color:#2ecc71',
                      subset=['Multiplier'])
            .format({c:'{:.2f}%' for c in ['KIBOR','Islamic Avg Rate','Sector Return',
                                             'GDP Growth','Inflation','Gap (Bank−Sector)']}
                    | {'Multiplier':'{:.1f}×'})
            .set_properties(**{'background-color':'#0a1628','color':'#e8d5a3','border-color':'#2a6b47'})
        )
        st.dataframe(df_hist_styled, use_container_width=True, hide_index=True)

        # Crisis callout
        max_mult_row = max(filtered_history, key=lambda h: h['islamic_avg']/h['sector_return'])
        mult = max_mult_row['islamic_avg'] / max_mult_row['sector_return']
        st.markdown(f"""
        <div class="warn-box">
        <b>⚠️ Worst Year in Selected Range — {max_mult_row['year']}:</b>
        KIBOR was {max_mult_row['kibor']:.1f}%, Islamic banks charged {max_mult_row['islamic_avg']:.1f}%,
        while Pakistan's real sector return was only {max_mult_row['sector_return']:.1f}%.
        Banks were charging <b>{mult:.1f}×</b> the actual economic return rate —
        devastating farmers, SMEs, and home buyers.
        </div>""", unsafe_allow_html=True)
    else:
        st.info("No historical data for the selected year range.")

    # ── Section 4: Borrower Impact ───────────────────────────────
    st.markdown('<div class="sec-title">4. Real Money Impact on Borrowers</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
    Showing total repayment on <b>PKR {loan_amount:,.0f}</b> over <b>{loan_tenure} months</b>
    comparing Islamic bank rates vs. proposed sector benchmarks.
    Adjust loan parameters in the sidebar.
    </div>""", unsafe_allow_html=True)

    fig_impact, impact_data = build_borrower_impact(filtered_sectors, loan_amount, loan_tenure)
    st.plotly_chart(fig_impact, use_container_width=True)

    # Impact detail cards
    cols = st.columns(min(len(filtered_sectors), 3))
    for i, (s, imp) in enumerate(zip(filtered_sectors, impact_data)):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom:12px">
              <div style="font-size:1.4rem">{s['icon']}</div>
              <div style="color:#a8c5b0;font-size:0.8rem;margin:4px 0">{s['name']}</div>
              <div style="color:#e74c3c;font-size:1.1rem;font-weight:700">
                PKR {imp['Islamic Bank Total']:,.0f}
              </div>
              <div style="color:#7ab890;font-size:0.7rem">Current (Islamic bank)</div>
              <div style="color:#2ecc71;font-size:1.1rem;font-weight:700;margin-top:4px">
                PKR {imp['Benchmark Total']:,.0f}
              </div>
              <div style="color:#7ab890;font-size:0.7rem">With sector benchmark</div>
              <div style="background:#2ecc7115;border:1px solid #2ecc71;border-radius:10px;
                          padding:3px 10px;margin-top:8px;color:#2ecc71;font-size:0.85rem;font-weight:700">
                Save PKR {imp['Saving']:,.0f}
              </div>
            </div>""", unsafe_allow_html=True)

    # Total savings
    total_saving = sum(d['Saving'] for d in impact_data)
    st.markdown(f"""
    <div class="good-box" style="text-align:center;padding:20px">
      <div style="color:#2ecc71;font-size:2rem;font-weight:700">PKR {total_saving:,.0f}</div>
      <div style="color:#7ab890">Total savings across {len(filtered_sectors)} sectors on PKR {loan_amount:,.0f}
      each over {loan_tenure} months</div>
    </div>""", unsafe_allow_html=True)

    # ── Section 5: Why Banks Have Not Reformed ───────────────────
    st.markdown('<div class="sec-title">5. Why Islamic Banks Have Not Set Their Own Benchmark</div>',
                unsafe_allow_html=True)

    for i, (title, body) in enumerate(REASONS_WHY):
        with st.expander(f"**{i+1}. {title}**", expanded=(i==0)):
            st.markdown(f'<div class="info-box">{body}</div>', unsafe_allow_html=True)

    # ── Section 6: The Solution ──────────────────────────────────
    st.markdown('<div class="sec-title">6. The Proposed Solution</div>', unsafe_allow_html=True)

    steps = [
        ("Step 1 — Data Collection",    "#c9a84c",
         "Aggregate real-time sector returns from PSX stock exchange, World Bank APIs, "
         "SBP agricultural finance data, industry association reports, and SME databases."),
        ("Step 2 — Cluster Classification", "#2ecc71",
         "Organize data by economic cluster: Agriculture (wheat, dairy, rice), Industry "
         "(textile, construction, food processing), Technology, Healthcare, Real Estate, Energy."),
        ("Step 3 — Benchmark Calculation", "#3498db",
         f"Calculate trimmed-mean returns per cluster + {admin_buffer:.1f}% administrative buffer. "
         "Output: 'Wheat Punjab Q1 2025 = 7.75%'. Fully auditable, transparent, manipulation-resistant."),
        ("Step 4 — Bank Integration",    "#e67e22",
         "Islamic banks adopt sector benchmarks for corresponding financing products. "
         "A wheat farmer's Murabaha uses the wheat benchmark — not KIBOR."),
        ("Step 5 — Shariah Validation",  "#9b59b6",
         "Benchmarks derived from real trade activity satisfy scholars' requirement for "
         "'real economy-based pricing' — genuinely fulfilling Al-Baqarah 2:275."),
    ]

    step_cols = st.columns(len(steps))
    for col, (title, color, body) in zip(step_cols, steps):
        with col:
            st.markdown(f"""
            <div style="background:#0d2137;border:1px solid {color}55;border-top:3px solid {color};
                        border-radius:8px;padding:14px;height:180px">
              <div style="color:{color};font-weight:700;font-size:0.82rem;margin-bottom:8px">{title}</div>
              <div style="color:#d4c4a0;font-size:0.78rem;line-height:1.6">{body}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(90deg,#0a2b1e,#1a5c40,#0a2b1e);
                border:2px solid #c9a84c;border-radius:10px;padding:20px;text-align:center">
      <div style="color:#c9a84c;font-size:1rem;font-weight:700">🚀 The Opportunity Window is Open NOW</div>
      <div style="color:#d4c4a0;font-size:0.88rem;margin-top:8px;line-height:1.8">
        Pakistan's Federal Shariat Court has mandated full Islamic banking conversion by <b>2027</b>.
        LIBOR has been scrapped. The State Bank acknowledges the need for a new benchmark.
        The data infrastructure is available online. Academic research calls for exactly this solution.
        <br><b style="color:#c9a84c">There has never been a better — or more urgent — time.</b>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Sources ──────────────────────────────────────────────────
    with st.expander("📚 Sources & References"):
        sources = [
            "Pakistan Economic Survey FY2024 — Ministry of Finance (agriculture 6.25%, wheat +11.6%)",
            "Pakistan Economic Survey FY2025 — Ministry of Finance (SBP policy rate, LSM data)",
            "Profit by Pakistan Today, Sep 2024 — Islamic bank rates: car 21.25%, housing 20.56%",
            "SBP Islamic Banking Bulletin 2024 — Meezan Bank / BankIslami profit rate filings",
            "Hussain SZ (2025) — 'Interest rate pass-through for Islamic banks' — Emerald IMEFM Journal",
            "Azad et al. (2018) — 'Can Islamic banks have their own benchmark?' — Emerging Markets Review",
            "Nechi & Smaoui (2019) — 'Interbank offered rates in Islamic countries' — QR of Economics & Finance",
            "PMC / PLOS ONE (2022) — 'Interest rate volatility and Islamic banks' — Pakistan evidence",
            "Express Tribune, Feb 2024 — 'Developing an Islamic finance benchmark'",
            "Wahed Invest — 'Benchmark in Islamic Finance' — Analysis of IIBR failure",
            "State Bank of Pakistan — KIBOR historical rates & SBP policy rate announcements 2020–2025",
            "Federal Shariat Court — Decision on full Islamic banking conversion by 2027",
        ]
        for i, src in enumerate(sources):
            st.markdown(f"**[{i+1}]** {src}")


# ═══════════════════════════════════════════════════════════════════
#  TAB 2 — YEAR-BY-YEAR ANALYSIS
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-title">📅 Year-by-Year Deep Dive</div>', unsafe_allow_html=True)

    selected_year = st.select_slider(
        "Select Year", options=[h['year'] for h in HISTORY_DATA],
        value=2024, key="single_year"
    )

    yr_data = next((h for h in HISTORY_DATA if h['year'] == selected_year), None)

    if yr_data:
        mult = yr_data['islamic_avg'] / yr_data['sector_return']
        severity = "🔴 Crisis Level" if mult > 5 else "🟠 High" if mult > 3 else "🟡 Elevated" if mult > 2 else "🟢 Moderate"

        st.markdown(f'<div style="text-align:center"><span class="year-badge">{selected_year}</span></div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        yr_kpis = [
            (f"{yr_data['kibor']:.2f}%",        "KIBOR",               "#e67e22"),
            (f"{yr_data['islamic_avg']:.2f}%",   "Islamic Bank Rate",   "#e74c3c"),
            (f"{yr_data['sector_return']:.2f}%", "Sector Return",       "#2ecc71"),
            (f"{yr_data['inflation']:.1f}%",     "Inflation",           "#9b59b6"),
            (f"{mult:.1f}×",                     f"Overcharge {severity}","#ff6b6b"),
        ]
        for col, (val, lbl, color) in zip([c1,c2,c3,c4,c5], yr_kpis):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-val" style="color:{color}">{val}</div>
                  <div class="kpi-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Year narrative
        narratives = {
            2020: "COVID year — SBP cut rates to 7% to stimulate economy. Islamic banks at 8.5%, "
                  "relatively close to sector returns of 3.9%. Most contained overcharge of the decade.",
            2021: "Recovery year — Rates held at 7%. Sector returns improved to 5.5%. Islamic banks "
                  "still at 8.2% — 1.49× multiplier, the most 'fair' the system has been.",
            2022: "Rate shock begins — SBP raised KIBOR to 13.75% to fight surging inflation (12.2%). "
                  "Islamic banks immediately jumped to 15.75%, charging 2.58× sector returns of 6.1%.",
            2023: "The Crisis Peak — KIBOR hit 22%, Islamic banks charged 22.8%, while Pakistan's "
                  "GDP growth collapsed to 2.4%. Banks charged 9.5× the actual economic return — "
                  "the most unjust year on record for Islamic finance.",
            2024: "Partial recovery — KIBOR reduced to 17.22%, banks at 20.56%. Agriculture rebounded "
                  "6.25% but financing rates remained 3.3× sector returns. Senate challenged SBP.",
            2025: "SBP rate cuts accelerating — Policy rate at 10.5%, Islamic banks following down "
                  "to ~13.5%. Inflation falling to ~7%. Best environment yet for benchmark reform.",
        }

        narrative = narratives.get(selected_year, "")
        color_box = "warn-box" if mult > 3 else "info-box" if mult > 2 else "good-box"
        st.markdown(f'<div class="{color_box}"><b>📖 {selected_year} Analysis:</b> {narrative}</div>',
                    unsafe_allow_html=True)

        # Year comparison bar chart
        fig_yr = go.Figure()
        categories = ['KIBOR', 'Islamic Bank Rate', 'Sector Return', 'Inflation']
        values = [yr_data['kibor'], yr_data['islamic_avg'], yr_data['sector_return'], yr_data['inflation']]
        colors_yr = ['#e67e22', '#e74c3c', '#2ecc71', '#9b59b6']

        fig_yr.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors_yr,
            text=[f"{v:.2f}%" for v in values],
            textposition='outside', textfont=dict(color='#e8d5a3', size=12),
            width=0.5,
        ))
        layout_yr = make_chart_layout(340)
        layout_yr['yaxis']['title'] = "Rate / Return (%)"
        layout_yr['showlegend'] = False
        layout_yr['title'] = dict(text=f"Key Rates — {selected_year}", font=dict(color='#c9a84c', size=14))
        fig_yr.update_layout(**layout_yr)
        st.plotly_chart(fig_yr, use_container_width=True)

        # Sector impact in that year
        st.markdown(f'<div class="sec-title">Sector Impact — {selected_year}</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
        In <b>{selected_year}</b>, Islamic bank rate was <b>{yr_data['islamic_avg']:.1f}%</b>.
        Using our proposed sector benchmarks instead, here's what each sector's borrowers would have paid:
        </div>""", unsafe_allow_html=True)

        cols = st.columns(3)
        for i, s in enumerate(filtered_sectors):
            m_bank   = monthly_payment(loan_amount, yr_data['islamic_avg'], loan_tenure)
            m_bench  = monthly_payment(loan_amount, s['benchmark'], loan_tenure)
            yr_save  = (m_bank - m_bench) * loan_tenure
            with cols[i % 3]:
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom:12px">
                  <div style="font-size:1.1rem">{s['icon']} <b style="color:#c9a84c">{s['name']}</b></div>
                  <div style="margin-top:8px">
                    <span style="color:#e74c3c">Bank: {yr_data['islamic_avg']:.1f}%</span>
                    &nbsp;→&nbsp;
                    <span style="color:#c9a84c">Benchmark: {s['benchmark']:.1f}%</span>
                  </div>
                  <div style="color:#2ecc71;font-weight:700;margin-top:6px">
                    Saves PKR {yr_save:,.0f}
                  </div>
                </div>""", unsafe_allow_html=True)

    # Full progression animation table
    st.markdown('<div class="sec-title">Full Historical Progression</div>', unsafe_allow_html=True)

    prog_data = []
    for h in HISTORY_DATA:
        mult_v = h['islamic_avg'] / h['sector_return']
        prog_data.append({
            "Year": h['year'],
            "KIBOR %": h['kibor'],
            "Islamic Rate %": h['islamic_avg'],
            "Sector Return %": h['sector_return'],
            "GDP Growth %": h['gdp_growth'],
            "Inflation %": h['inflation'],
            "Multiplier": round(mult_v, 2),
            "Gap %": round(h['islamic_avg'] - h['sector_return'], 2),
        })

    df_prog = pd.DataFrame(prog_data)

    def highlight_year(row):
        if row['Year'] == selected_year:
            return ['background-color: #1a3b1e; color: #c9a84c; font-weight: bold'] * len(row)
        elif row['Multiplier'] == max(r['Multiplier'] for r in prog_data):
            return ['background-color: #1a0808'] * len(row)
        return [''] * len(row)

    styled_prog = (df_prog.style
        .apply(highlight_year, axis=1)
        .format({
            'KIBOR %': '{:.2f}%',
            'Islamic Rate %': '{:.2f}%',
            'Sector Return %': '{:.2f}%',
            'GDP Growth %': '{:.2f}%',
            'Inflation %': '{:.1f}%',
            'Multiplier': '{:.2f}×',
            'Gap %': '+{:.2f}%',
        })
        .set_properties(**{'background-color': '#0a1628', 'color': '#e8d5a3', 'border-color': '#2a6b47'})
    )
    st.dataframe(styled_prog, use_container_width=True, hide_index=True)
    st.caption("🟩 Gold row = selected year above. Dark red row = worst overcharge year.")


# ═══════════════════════════════════════════════════════════════════
#  TAB 3 — LIVE BENCHMARKS
# ═══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-title">📊 Live Sector Benchmarks (Real-Time Data)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    These benchmarks are calculated from <b>live stock market data</b> via Yahoo Finance.
    They represent actual sector returns — not KIBOR. Use these as the foundation for genuine
    Islamic profit rates. Data is cached for 1 hour.
    </div>""", unsafe_allow_html=True)

    sector_choice = st.selectbox("Select sector to benchmark", list(YAHOO_SECTORS.keys()))
    cluster_choice = st.selectbox("Select cluster", list(YAHOO_SECTORS[sector_choice].keys()))
    tickers = YAHOO_SECTORS[sector_choice][cluster_choice]

    if st.button(f"🔄 Fetch Live Benchmark for {cluster_choice}", use_container_width=True):
        with st.spinner("Fetching real-time data..."):
            live_data = fetch_sector_live(tickers, api_period)

        if live_data:
            returns = [v['return'] for v in live_data.values() if v['return'] > -80]
            if returns:
                trimmed = sorted(returns)[1:-1] if len(returns) > 2 else returns
                live_benchmark = np.mean(trimmed) + admin_buffer
                avg_vol = np.mean([v['volatility'] for v in live_data.values()])

                # Headline
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0d3b2e,#1a5c40);
                            border:1px solid #c9a84c;border-radius:12px;
                            padding:24px;text-align:center;margin:16px 0">
                  <div style="color:#7ab890;font-size:0.85rem">{sector_choice} → {cluster_choice}</div>
                  <div style="color:#c9a84c;font-family:'Amiri',serif;font-size:1.6rem;font-weight:700">
                    Live Islamic Profit Benchmark
                  </div>
                  <div style="color:#fff;font-size:3rem;font-weight:700;margin:8px 0">
                    {live_benchmark:.2f}%
                  </div>
                  <div style="color:#a8c5b0;font-size:0.82rem">
                    Based on real {api_period} returns | Admin buffer: +{admin_buffer:.1f}%
                  </div>
                </div>""", unsafe_allow_html=True)

                # Tickers
                c1, c2, c3 = st.columns(len(live_data))
                for col, (ticker, vals) in zip([c1, c2, c3], live_data.items()):
                    with col:
                        color = "#2ecc71" if vals['return'] > 0 else "#e74c3c"
                        st.markdown(f"""
                        <div class="kpi-card">
                          <div style="color:#7ab890;font-size:0.85rem">{ticker}</div>
                          <div class="kpi-val" style="color:{color};font-size:1.5rem">
                            {vals['return']:+.1f}%
                          </div>
                          <div class="kpi-lbl">Return ({api_period})</div>
                          <div class="kpi-src">Vol: {vals['volatility']:.1f}% | ${vals['price']:.2f}</div>
                        </div>""", unsafe_allow_html=True)

                # Price history
                st.markdown('<div class="sec-title">Price Performance (Normalized)</div>',
                            unsafe_allow_html=True)
                fig_live = go.Figure()
                colors_l = ['#c9a84c','#2ecc71','#3498db']
                for i, ticker in enumerate(tickers):
                    try:
                        hist = yf.Ticker(ticker).history(period=api_period)
                        if len(hist) > 5:
                            norm = (hist['Close'] / hist['Close'].iloc[0]) * 100
                            fig_live.add_trace(go.Scatter(
                                x=hist.index, y=norm, name=ticker,
                                line=dict(color=colors_l[i % 3], width=2),
                            ))
                    except:
                        pass
                fig_live.add_hline(y=100, line_dash="dot", line_color="#555",
                                   annotation_text="Base 100")
                fig_live.update_layout(**make_chart_layout(350))
                st.plotly_chart(fig_live, use_container_width=True)
        else:
            st.warning("Could not fetch live data. Check internet connection or try again.")

    # Live benchmark vs Islamic bank comparison
    if st.button("📊 Load All Sectors Benchmark", use_container_width=False):
        all_live = {}
        prog = st.progress(0)
        sectors_list = list(YAHOO_SECTORS.items())
        for i, (sec_name, clusters) in enumerate(sectors_list):
            all_tickers = [t for cl in clusters.values() for t in cl]
            d = fetch_sector_live(all_tickers[:6], api_period)
            if d:
                rets = [v['return'] for v in d.values() if v['return'] > -80]
                if rets:
                    all_live[sec_name] = round(np.mean(rets) + admin_buffer, 2)
            prog.progress((i+1) / len(sectors_list))
        prog.empty()

        if all_live:
            st.session_state['all_live_benchmarks'] = all_live

    if 'all_live_benchmarks' in st.session_state:
        live_bm = st.session_state['all_live_benchmarks']
        fig_all = go.Figure()
        sec_names = list(live_bm.keys())
        fig_all.add_trace(go.Bar(
            x=sec_names, y=list(live_bm.values()),
            marker_color=['#2ecc71' if v > 0 else '#e74c3c' for v in live_bm.values()],
            text=[f"{v:.1f}%" for v in live_bm.values()],
            textposition='outside', name="Live Benchmark"
        ))
        fig_all.add_hline(y=20.56, line_dash="dash", line_color="#e74c3c",
                          annotation_text="Current Islamic Bank Rate (20.56%)",
                          annotation_font_color="#e74c3c")
        fig_all.update_layout(**make_chart_layout(380))
        st.plotly_chart(fig_all, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  TAB 4 — SECTOR DEEP DIVE
# ═══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-title">🔍 Sector Deep Dive</div>', unsafe_allow_html=True)

    sel_sector = st.selectbox("Choose sector", [s['name'] for s in SECTORS_DATA], key="deep_sector")
    s = next(s for s in SECTORS_DATA if s['name'] == sel_sector)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d3b2e,#1a5c40);
                    border:1px solid #c9a84c;border-radius:10px;padding:20px;margin-bottom:12px">
          <div style="font-size:2.5rem;text-align:center">{s['icon']}</div>
          <div style="color:#c9a84c;font-family:'Amiri',serif;font-size:1.4rem;
                      text-align:center;margin:6px 0">{s['name']}</div>
          <div style="color:#7ab890;text-align:center;font-size:0.85rem">{s['cat']} | {s['borrower']}</div>
        </div>""", unsafe_allow_html=True)

        for label, val, color, desc in [
            ("Islamic Bank Charges", f"{s['islamic']:.2f}%", "#e74c3c", "KIBOR-based — sector-blind"),
            ("KIBOR Reference",      f"{s['kibor']:.2f}%",   "#e67e22", "SBP Ijarah Sukuk Jul 2024"),
            ("Real Sector Return",   f"{s['real_return']:.2f}%","#2ecc71","Actual economic performance"),
            ("Proposed Benchmark",   f"{s['benchmark']:.2f}%","#c9a84c", f"Sector return + {admin_buffer:.1f}% admin"),
        ]:
            st.markdown(f"""
            <div style="background:#0d1f2b;border-left:4px solid {color};
                        border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:8px;
                        display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="color:#a8c5b0;font-size:0.82rem">{label}</div>
                <div style="color:#7ab890;font-size:0.72rem;margin-top:2px">{desc}</div>
              </div>
              <div style="color:{color};font-size:1.7rem;font-weight:700">{val}</div>
            </div>""", unsafe_allow_html=True)

        overcharge_color = "#e74c3c" if s['overcharge'] > 8 else "#e67e22" if s['overcharge'] > 5 else "#f39c12"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#3b0d0d,#2b0808);
                    border:2px solid #e74c3c;border-radius:10px;
                    padding:16px;text-align:center;margin-top:8px">
          <div style="color:#ff8080;font-size:0.82rem">Overcharge Gap</div>
          <div style="color:#e74c3c;font-size:2.5rem;font-weight:700">+{s['overcharge']:.2f}%</div>
          <div style="color:#a87070;font-size:0.78rem">
            Bank charges {s['overcharge']:.1f}% more than sector earns
          </div>
        </div>""", unsafe_allow_html=True)

    with col_r:
        # Radar/spider chart
        categories = ['Islamic Rate','KIBOR','Sector Return','Benchmark','Inflation\n(2024)']
        values_radar = [s['islamic'], s['kibor'], s['real_return'], s['benchmark'], 23.4]

        fig_radar = go.Figure(go.Scatterpolar(
            r=values_radar + [values_radar[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(201,168,76,0.15)',
            line=dict(color='#c9a84c', width=2),
            name=s['name'],
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[20.56, 17.22, s['real_return'], s['benchmark'], 23.4, 20.56],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(231,76,60,0.08)',
            line=dict(color='#e74c3c', width=1.5, dash='dot'),
            name="Avg Islamic Bank",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(gridcolor='#1a3a2a', tickfont=dict(color='#7ab890'), range=[0, 28]),
                angularaxis=dict(gridcolor='#1a3a2a', tickfont=dict(color='#a8c5b0')),
            ),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8d5a3'), height=320,
            margin=dict(t=30,b=10,l=30,r=30),
            legend=dict(bgcolor='rgba(10,22,40,0.8)', bordercolor='#2a6b47'),
            showlegend=True,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown(f'<div class="info-box"><b>📖 Context:</b> {s["context"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="info-box"><b>📌 Source:</b> {s["source"]}</div>',
                    unsafe_allow_html=True)

    # Financing comparison for this sector
    st.markdown(f'<div class="sec-title">Financing Comparison — {s["name"]}</div>',
                unsafe_allow_html=True)

    m_islamic = monthly_payment(loan_amount, s['islamic'], loan_tenure)
    m_bench   = monthly_payment(loan_amount, s['benchmark'], loan_tenure)
    saving    = (m_islamic - m_bench) * loan_tenure

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#2b0808,#1a0505);
                    border:1px solid #e74c3c;border-radius:10px;padding:20px">
          <div style="color:#e74c3c;font-size:0.8rem;letter-spacing:2px;text-transform:uppercase">
            ❌ Current Islamic Bank ({s['islamic']:.1f}%)
          </div>
          <div style="color:#ff8080;font-size:2rem;font-weight:700;margin:8px 0">
            PKR {m_islamic:,.0f}
          </div>
          <div style="color:#a87070;font-size:0.78rem">Monthly payment</div>
          <div style="color:#e74c3c;font-size:1.1rem;font-weight:700;margin-top:10px">
            PKR {m_islamic*loan_tenure:,.0f}
          </div>
          <div style="color:#a87070;font-size:0.78rem">Total over {loan_tenure} months</div>
        </div>""", unsafe_allow_html=True)
    with cc2:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#082b10,#051a08);
                    border:1px solid #2ecc71;border-radius:10px;padding:20px">
          <div style="color:#2ecc71;font-size:0.8rem;letter-spacing:2px;text-transform:uppercase">
            ✅ Proposed Benchmark ({s['benchmark']:.1f}%)
          </div>
          <div style="color:#a8e8b8;font-size:2rem;font-weight:700;margin:8px 0">
            PKR {m_bench:,.0f}
          </div>
          <div style="color:#6a9070;font-size:0.78rem">Monthly payment</div>
          <div style="color:#2ecc71;font-size:1.1rem;font-weight:700;margin-top:10px">
            PKR {m_bench*loan_tenure:,.0f}
          </div>
          <div style="color:#6a9070;font-size:0.78rem">Total over {loan_tenure} months</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="good-box" style="text-align:center;padding:16px;margin-top:10px">
      <b style="color:#2ecc71;font-size:1.4rem">Save PKR {saving:,.0f}</b>
      <div style="color:#7ab890;font-size:0.82rem">
        On PKR {loan_amount:,.0f} over {loan_tenure} months —
        a {s['borrower']} with sector-based Islamic benchmark
      </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  TAB 5 — CALCULATOR
# ═══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-title">💰 Islamic Financing Calculator</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        calc_sector = st.selectbox("Sector", [s['name'] for s in SECTORS_DATA], key="cs")
        cs = next(s for s in SECTORS_DATA if s['name'] == calc_sector)
        calc_mode = st.selectbox("Financing Mode",
                                  ["Murabaha (Cost+Profit)","Diminishing Musharakah","Ijara (Leasing)"])
        use_custom = st.checkbox("Use custom rate")
        custom_rate = st.number_input("Custom Rate (%)", 1.0, 50.0, cs['benchmark'], 0.1) if use_custom else cs['benchmark']
        calc_amt = st.number_input("Amount (PKR)", 100000, 50000000, loan_amount, 50000)
        calc_ten = st.slider("Tenure (months)", 12, 240, loan_tenure)

    with c2:
        rate = custom_rate if use_custom else cs['benchmark']
        m_pay = monthly_payment(calc_amt, rate, calc_ten)
        t_pay = m_pay * calc_ten
        t_prof = t_pay - calc_amt

        m_conv = monthly_payment(calc_amt, cs['islamic'], calc_ten)
        t_conv = m_conv * calc_ten
        save_vs_bank = t_conv - t_pay

        st.markdown(f"""
        <div style="background:#0d2137;border:1px solid #c9a84c;border-radius:10px;padding:20px">
          <div style="color:#c9a84c;font-weight:700;margin-bottom:12px">
            📊 {calc_mode} — {cs['name']}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            <div style="text-align:center">
              <div style="color:#7ab890;font-size:0.75rem">Benchmark Rate</div>
              <div style="color:#c9a84c;font-size:1.6rem;font-weight:700">{rate:.2f}%</div>
            </div>
            <div style="text-align:center">
              <div style="color:#7ab890;font-size:0.75rem">Monthly Payment</div>
              <div style="color:#2ecc71;font-size:1.6rem;font-weight:700">PKR {m_pay:,.0f}</div>
            </div>
            <div style="text-align:center">
              <div style="color:#7ab890;font-size:0.75rem">Total Repayment</div>
              <div style="color:#e8d5a3;font-size:1.2rem;font-weight:700">PKR {t_pay:,.0f}</div>
            </div>
            <div style="text-align:center">
              <div style="color:#7ab890;font-size:0.75rem">Total Profit</div>
              <div style="color:#c9a84c;font-size:1.2rem;font-weight:700">PKR {t_prof:,.0f}</div>
            </div>
          </div>
          <div style="border-top:1px solid #2a6b47;margin-top:14px;padding-top:12px;text-align:center">
            <div style="color:#2ecc71;font-size:0.82rem">vs Current Islamic Bank ({cs['islamic']:.1f}%)</div>
            <div style="color:#2ecc71;font-size:1.5rem;font-weight:700">Save PKR {save_vs_bank:,.0f}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Amortization schedule
    if st.checkbox("Show full amortization schedule"):
        bal = calc_amt
        r_m = rate / 100 / 12
        schedule = []
        for mo in range(1, calc_ten + 1):
            prof_pay = bal * r_m
            prin_pay = m_pay - prof_pay
            bal = max(0, bal - prin_pay)
            schedule.append({"Month": mo, "Principal": round(prin_pay),
                              "Profit": round(prof_pay), "Balance": round(bal)})
        df_amort = pd.DataFrame(schedule)

        fig_amort = make_subplots(rows=1, cols=2,
                                   subplot_titles=["Payment Breakdown", "Remaining Balance"])
        fig_amort.add_trace(go.Bar(x=df_amort['Month'], y=df_amort['Principal'],
                                    name='Principal', marker_color='#2ecc71'), row=1, col=1)
        fig_amort.add_trace(go.Bar(x=df_amort['Month'], y=df_amort['Profit'],
                                    name='Profit', marker_color='#c9a84c'), row=1, col=1)
        fig_amort.add_trace(go.Scatter(x=df_amort['Month'], y=df_amort['Balance'],
                                        name='Balance', line=dict(color='#3498db', width=2),
                                        fill='tozeroy', fillcolor='rgba(52,152,219,0.1)'), row=1, col=2)
        fig_amort.update_layout(barmode='stack', **make_chart_layout(320,
                                margin=dict(t=40,b=30,l=10,r=10)))
        for ax in ['xaxis','xaxis2','yaxis','yaxis2']:
            fig_amort.update_layout(**{ax: dict(gridcolor='#1a3a2a', tickfont=dict(color='#7ab890'))})
        st.plotly_chart(fig_amort, use_container_width=True)

        with st.expander("📋 Full Schedule (first 24 months)"):
            st.dataframe(df_amort.head(24), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  TAB 6 — ISLAMIC FINANCE GUIDE
# ═══════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec-title">📖 Islamic Finance Principles</div>', unsafe_allow_html=True)

    verses = [
        ("Al-Baqarah 2:275",
         "وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا",
         "Allah has permitted trade and forbidden Riba (interest)",
         "All financing must be trade/asset-based. Profit from real economic activity is halal; "
         "guaranteed return on money lent without risk is haram."),
        ("Al-Baqarah 2:279",
         "فَلَكُمْ رُءُوسُ أَمْوَالِكُمْ لَا تَظْلِمُونَ وَلَا تُظْلَمُونَ",
         "You shall have your principal — neither wronging nor being wronged",
         "Capital preservation without exploitation. This verse directly condemns charging a "
         "wheat farmer 20% when his sector only earns 6% — that is the very zulm (injustice) prohibited."),
        ("Al-Baqarah 2:282",
         "إِذَا تَدَايَنتُم بِدَيْنٍ إِلَىٰ أَجَلٍ مُّسَمًّى فَاكْتُبُوهُ",
         "When you contract a debt for a fixed term, write it down",
         "Transparency and documentation are obligations. Our system's public, auditable benchmarks "
         "directly fulfill this — unlike opaque KIBOR-linked pricing."),
        ("Al-Baqarah 2:245",
         "مَّن ذَا الَّذِي يُقْرِضُ اللَّهَ قَرْضًا حَسَنًا",
         "Who will lend Allah a goodly loan (Qard-e-Hasana)?",
         "Interest-free lending to the needy is a religious obligation. Sector-based benchmarks "
         "enable lower-cost financing that makes Qard-e-Hasana feasible for banks."),
    ]

    for ref, arabic, translation, implication in verses:
        st.markdown(f"""
        <div class="ayah-box" style="text-align:left;margin-bottom:14px">
          <div style="color:#c9a84c;font-size:0.78rem;margin-bottom:8px;letter-spacing:1px">
            📖 {ref}
          </div>
          <div class="ayah-arabic">{arabic}</div>
          <div class="ayah-trans">"{translation}"</div>
          <div style="color:#c9a84c;font-size:0.82rem;margin-top:10px;
                      border-top:1px solid #2a6b47;padding-top:8px">
            💡 <b>Economic Implication:</b> {implication}
          </div>
        </div>""", unsafe_allow_html=True)

    # Comparison table
    st.markdown('<div class="sec-title">Islamic vs. Conventional Banking</div>', unsafe_allow_html=True)

    comparison_df = pd.DataFrame({
        "Feature": [
            "Benchmark Source","Rate Setting","Risk Distribution",
            "Asset Requirement","Poor Protection","Accountability",
            "Wealth Distribution","Crisis Behavior",
        ],
        "✅ Islamic (This System)": [
            "Real sector economic returns","Tied to actual sector performance",
            "Shared bank & client","Must be real tangible asset",
            "Rate based on sector — farmer pays agri rate",
            "To Allah + Legal system","Zakat redistributes wealth",
            "Share losses with borrower in bad times",
        ],
        "❌ Conventional / Fake Islamic": [
            "KIBOR/LIBOR (interest-based)","Central bank policy rate",
            "Client bears all risk","Paper transaction only",
            "Same rate regardless of sector performance",
            "Legal system only","Concentration of wealth",
            "Client owes in full even if sector collapses",
        ]
    })
    st.dataframe(comparison_df.style
                 .set_properties(**{'background-color':'#0a1628','color':'#e8d5a3','border-color':'#2a6b47'})
                 .applymap(lambda v: 'color:#2ecc71' if '✅' in str(v) or 'Real' in str(v) or 'Share' in str(v) else
                                     'color:#e74c3c' if 'KIBOR' in str(v) or 'Paper' in str(v) else '',
                           subset=["✅ Islamic (This System)","❌ Conventional / Fake Islamic"]),
                 use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:28px;color:#2a6b47;
            font-size:0.78rem;border-top:1px solid #1a3a2a;margin-top:40px">
  <div style="font-family:'Amiri',serif;color:#c9a84c;font-size:1.1rem">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ</div>
  <div style="margin-top:6px">
    Islamic Profit Benchmark System — Building a Just Financial Economy Based on Quran &amp; Real Data<br>
    Data: Pakistan Economic Survey FY2024–25 | SBP Bulletin | Profit by Pakistan Today | Yahoo Finance | World Bank API
  </div>
</div>
""", unsafe_allow_html=True)
