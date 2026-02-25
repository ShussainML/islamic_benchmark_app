import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import time

# ─────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Islamic Profit Benchmark System",
    page_icon="☪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  Custom CSS — Dark emerald / gold theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
    color: #e8d5a3;
}

/* Header */
.main-header {
    background: linear-gradient(90deg, #0d3b2e, #1a5c40, #0d3b2e);
    border: 1px solid #c9a84c;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 0 40px rgba(201,168,76,0.15);
}
.main-header h1 {
    font-family: 'Amiri', serif;
    color: #c9a84c;
    font-size: 2.6rem;
    margin: 0;
    letter-spacing: 1px;
}
.main-header p {
    color: #a8c5b0;
    font-size: 1rem;
    margin: 8px 0 0 0;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d2b1e, #143d2b);
    border: 1px solid #2a6b47;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #c9a84c;
}
.metric-card .label {
    font-size: 0.85rem;
    color: #7ab890;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Section headers */
.section-title {
    font-family: 'Amiri', serif;
    color: #c9a84c;
    font-size: 1.5rem;
    border-bottom: 1px solid #2a6b47;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

/* Benchmark pill */
.benchmark-badge {
    display: inline-block;
    background: linear-gradient(90deg, #1a5c40, #0d3b2e);
    border: 1px solid #c9a84c;
    border-radius: 20px;
    padding: 6px 18px;
    color: #c9a84c;
    font-size: 1.1rem;
    font-weight: 700;
}

/* Info box */
.info-box {
    background: rgba(13, 59, 46, 0.4);
    border-left: 4px solid #c9a84c;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
    color: #d4c4a0;
    font-size: 0.9rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071220 0%, #0a1f30 100%);
    border-right: 1px solid #2a6b47;
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    color: #c9a84c;
    font-family: 'Amiri', serif;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #1a5c40, #0d7a52);
    color: #fff;
    border: 1px solid #c9a84c;
    border-radius: 8px;
    font-family: 'Cairo', sans-serif;
    font-weight: 600;
    padding: 10px 24px;
    transition: all 0.3s;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #c9a84c, #a8882e);
    color: #0a1628;
    border-color: #c9a84c;
}

/* Selectbox, inputs */
.stSelectbox > div > div, .stNumberInput > div > div {
    background: #0d2137 !important;
    border-color: #2a6b47 !important;
    color: #e8d5a3 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #2a6b47;
}
.stTabs [data-baseweb="tab"] {
    color: #7ab890;
    font-family: 'Cairo', sans-serif;
}
.stTabs [aria-selected="true"] {
    color: #c9a84c !important;
    border-bottom: 2px solid #c9a84c !important;
}

.ayah-box {
    background: linear-gradient(135deg, #071220, #0d2b1e);
    border: 1px solid #c9a84c;
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
    margin: 16px 0;
}
.ayah-arabic {
    font-family: 'Amiri', serif;
    font-size: 1.4rem;
    color: #c9a84c;
    direction: rtl;
    line-height: 2;
}
.ayah-translation {
    color: #a8c5b0;
    font-size: 0.85rem;
    margin-top: 8px;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Sector Definitions with Yahoo Finance tickers
# ─────────────────────────────────────────────
SECTORS = {
    "Agriculture": {
        "icon": "🌾",
        "clusters": {
            "Wheat & Grains": ["ADM", "INGR", "MOS"],
            "Dairy & Livestock": ["SAFM", "TSN", "HRL"],
            "Fruits & Horticulture": ["DOLE", "FDP", "JBSS"],
            "Fertilizers & Agri-Input": ["MOS", "NTR", "CF"],
        }
    },
    "Industry & Manufacturing": {
        "icon": "🏭",
        "clusters": {
            "Textile & Garments": ["HBI", "PVH", "RL"],
            "Construction Materials": ["VMC", "MLM", "USCR"],
            "Food Processing": ["GIS", "CPB", "CAG"],
            "Chemicals": ["LYB", "DD", "EMN"],
        }
    },
    "Technology & IT": {
        "icon": "💻",
        "clusters": {
            "Software & SaaS": ["MSFT", "CRM", "NOW"],
            "IT Services": ["ACN", "INFY", "WIT"],
            "E-Commerce": ["AMZN", "SHOP", "MELI"],
            "Fintech": ["PYPL", "SQ", "ADYEY"],
        }
    },
    "Healthcare": {
        "icon": "🏥",
        "clusters": {
            "Pharmaceuticals": ["JNJ", "PFE", "ABBV"],
            "Medical Devices": ["MDT", "ABT", "SYK"],
            "Healthcare Services": ["UNH", "CVS", "HUM"],
        }
    },
    "Real Estate": {
        "icon": "🏢",
        "clusters": {
            "Residential": ["DHI", "LEN", "PHM"],
            "Commercial": ["SPG", "O", "PLD"],
            "Infrastructure": ["AMT", "CCI", "EQIX"],
        }
    },
    "Energy": {
        "icon": "⚡",
        "clusters": {
            "Solar & Renewable": ["ENPH", "FSLR", "RUN"],
            "Oil & Gas (Downstream)": ["VLO", "PSX", "MPC"],
            "Power Generation": ["NEE", "DUK", "SO"],
        }
    },
    "Trade & Retail": {
        "icon": "🛒",
        "clusters": {
            "Consumer Goods": ["PG", "KO", "UL"],
            "General Retail": ["WMT", "TGT", "COST"],
            "Export Trade": ["FDX", "UPS", "XPO"],
        }
    }
}

# ─────────────────────────────────────────────
#  Data Fetching Functions
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_sector_returns(tickers, period="1y"):
    """Fetch stock data and calculate annualized returns"""
    results = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if len(hist) > 20:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                annual_return = ((end_price / start_price) - 1) * 100
                # Calculate volatility
                daily_returns = hist['Close'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100
                results[ticker] = {
                    'return': annual_return,
                    'volatility': volatility,
                    'current_price': end_price
                }
        except Exception:
            pass
    return results

@st.cache_data(ttl=3600)
def fetch_world_bank_data(indicator, country="PK"):
    """Fetch World Bank economic indicators"""
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv=5"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if len(data) > 1 and data[1]:
            values = [d['value'] for d in data[1] if d['value'] is not None]
            return values
    except:
        pass
    return None

def calculate_benchmark(tickers, risk_buffer=0.02):
    """Core benchmark calculation from real market data"""
    data = fetch_sector_returns(tickers)
    if not data:
        return None, None, None
    
    returns = [v['return'] for v in data.values() if v['return'] > -50]
    volatilities = [v['volatility'] for v in data.values()]
    
    if not returns:
        return None, None, None
    
    avg_return = np.mean(returns)
    avg_vol = np.mean(volatilities)
    
    # Islamic benchmark = Trimmed mean of sector returns + small buffer for admin costs
    # Remove outliers (top and bottom 10%)
    if len(returns) >= 3:
        returns_sorted = sorted(returns)
        trim = max(1, len(returns_sorted) // 5)
        trimmed = returns_sorted[trim:-trim] if trim > 0 else returns_sorted
        benchmark = np.mean(trimmed) + (risk_buffer * 100)
    else:
        benchmark = avg_return + (risk_buffer * 100)
    
    return round(benchmark, 2), round(avg_vol, 2), data

def get_risk_category(volatility):
    if volatility < 20:
        return "Low Risk", "#2ecc71"
    elif volatility < 35:
        return "Moderate Risk", "#f39c12"
    elif volatility < 50:
        return "High Risk", "#e67e22"
    else:
        return "Very High Risk", "#e74c3c"

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>☪️ Islamic Profit Benchmark System</h1>
    <p>Real-Time, Data-Driven Halal Finance Benchmarks — Independent of Interest-Based Rates</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    st.markdown("### 📅 Analysis Period")
    period_map = {"3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y"}
    selected_period_label = st.selectbox("Historical Period", list(period_map.keys()), index=2)
    selected_period = period_map[selected_period_label]
    
    st.markdown("### 🏦 Financing Parameters")
    admin_buffer = st.slider("Admin Cost Buffer (%)", 0.5, 3.0, 1.5, 0.1)
    finance_amount = st.number_input("Financing Amount ($)", min_value=1000, value=100000, step=5000)
    finance_tenure = st.slider("Tenure (Months)", 3, 120, 24)
    
    st.markdown("### 🌍 Country Context")
    country = st.selectbox("Country", ["Pakistan", "Malaysia", "Saudi Arabia", "UAE", "Bangladesh", "Global"])
    
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
    <b>📌 About Benchmarks</b><br>
    This system calculates profit benchmarks from <b>actual sector returns</b> — not from KIBOR/LIBOR or any interest-based rate.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ayah-box">
        <div class="ayah-arabic">وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا</div>
        <div class="ayah-translation">"Allah has permitted trade and forbidden interest" — Al-Baqarah 2:275</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Main Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Benchmark Dashboard",
    "🔍 Sector Deep Dive",
    "💰 Financing Calculator",
    "📈 Market Trends",
    "📖 Islamic Finance Guide"
])

# ═══════════════════════════════════════════
#  TAB 1: BENCHMARK DASHBOARD
# ═══════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📊 Live Sector Benchmark Rates</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    🔄 Benchmarks are calculated from real-time market data across sector companies. 
    These represent <b>actual economic returns</b> — not artificial interest rates. 
    Islamic banks can use these as their Murabaha / Musharakah profit reference rates.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Fetch Live Benchmarks for All Sectors", use_container_width=True):
        
        all_benchmarks = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        sectors_list = list(SECTORS.items())
        for i, (sector_name, sector_data) in enumerate(sectors_list):
            status_text.text(f"Fetching data for {sector_name}...")
            
            # Collect all tickers for this sector
            all_tickers = []
            for cluster_tickers in sector_data["clusters"].values():
                all_tickers.extend(cluster_tickers)
            
            benchmark, volatility, raw_data = calculate_benchmark(all_tickers, admin_buffer/100)
            
            if benchmark is not None:
                risk_label, risk_color = get_risk_category(volatility)
                all_benchmarks[sector_name] = {
                    "benchmark": benchmark,
                    "volatility": volatility,
                    "risk_label": risk_label,
                    "risk_color": risk_color,
                    "icon": sector_data["icon"]
                }
            
            progress_bar.progress((i + 1) / len(sectors_list))
            time.sleep(0.1)
        
        status_text.text("✅ All benchmarks loaded!")
        st.session_state['all_benchmarks'] = all_benchmarks
        progress_bar.empty()
        status_text.empty()
    
    # Display benchmarks if available
    if 'all_benchmarks' in st.session_state:
        benchmarks = st.session_state['all_benchmarks']
        
        # Summary metrics
        valid_benchmarks = [v['benchmark'] for v in benchmarks.values() if v['benchmark'] > 0]
        if valid_benchmarks:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{np.mean(valid_benchmarks):.1f}%</div>
                    <div class="label">Avg Economy Return</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{max(valid_benchmarks):.1f}%</div>
                    <div class="label">Highest Sector</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value">{min(valid_benchmarks):.1f}%</div>
                    <div class="label">Lowest Sector</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                kibor_est = 22.0  # approximate KIBOR
                avg_bench = np.mean(valid_benchmarks)
                diff = kibor_est - avg_bench
                st.markdown(f"""
                <div class="metric-card">
                    <div class="value" style="color:#{'e74c3c' if diff > 0 else '2ecc71'}">{diff:+.1f}%</div>
                    <div class="label">vs KIBOR (~22%)</div>
                </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Benchmark cards
        cols = st.columns(3)
        for idx, (sector_name, data) in enumerate(benchmarks.items()):
            with cols[idx % 3]:
                color = "#2ecc71" if data['benchmark'] > 0 else "#e74c3c"
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:16px;">
                    <div style="font-size:2rem">{data['icon']}</div>
                    <div style="color:#a8c5b0; font-size:0.9rem; margin:4px 0">{sector_name}</div>
                    <div class="value" style="color:{color}">{data['benchmark']:.1f}%</div>
                    <div style="margin-top:6px">
                        <span style="background:{data['risk_color']}22; color:{data['risk_color']}; 
                              border:1px solid {data['risk_color']}; border-radius:12px; 
                              padding:2px 10px; font-size:0.75rem">
                            {data['risk_label']}
                        </span>
                    </div>
                    <div style="color:#7ab890; font-size:0.78rem; margin-top:4px">
                        Volatility: {data['volatility']:.1f}%
                    </div>
                </div>""", unsafe_allow_html=True)
        
        # Benchmark comparison chart
        st.markdown('<div class="section-title">📊 Benchmark Comparison Chart</div>', unsafe_allow_html=True)
        
        sector_names = list(benchmarks.keys())
        benchmark_values = [benchmarks[s]['benchmark'] for s in sector_names]
        colors = ['#c9a84c' if v > 0 else '#e74c3c' for v in benchmark_values]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sector_names,
            y=benchmark_values,
            marker_color=colors,
            text=[f"{v:.1f}%" for v in benchmark_values],
            textposition='outside',
            textfont=dict(color='#e8d5a3'),
            name="Islamic Benchmark"
        ))
        # Add KIBOR reference line
        fig.add_hline(y=22, line_dash="dash", line_color="#e74c3c", 
                     annotation_text="KIBOR (~22%)", annotation_font_color="#e74c3c")
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8d5a3', family='Cairo'),
            xaxis=dict(gridcolor='#1a3a2a', tickangle=-30),
            yaxis=dict(gridcolor='#1a3a2a', title="Benchmark Rate (%)"),
            showlegend=False,
            height=420,
            margin=dict(t=20, b=80)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.markdown("""
        <div class="info-box" style="text-align:center; padding:40px">
            <div style="font-size:3rem">📊</div>
            <div style="font-size:1.1rem; margin-top:8px">Click <b>"Fetch Live Benchmarks"</b> above to load real-time sector data</div>
            <div style="font-size:0.85rem; color:#7ab890; margin-top:8px">Data is fetched from global stock markets and cached for 1 hour</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  TAB 2: SECTOR DEEP DIVE
# ═══════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🔍 Sector & Cluster Deep Dive</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        selected_sector = st.selectbox("Select Sector", list(SECTORS.keys()))
    with col2:
        clusters = list(SECTORS[selected_sector]["clusters"].keys())
        selected_cluster = st.selectbox("Select Cluster / Sub-Sector", clusters)
    
    tickers = SECTORS[selected_sector]["clusters"][selected_cluster]
    
    if st.button(f"📡 Analyze {selected_cluster}", use_container_width=True):
        with st.spinner(f"Fetching real-time data for {selected_cluster}..."):
            benchmark, volatility, raw_data = calculate_benchmark(tickers, admin_buffer/100)
        
        if benchmark is not None and raw_data:
            # Benchmark headline
            risk_label, risk_color = get_risk_category(volatility)
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d3b2e,#1a5c40);border:1px solid #c9a84c;
                        border-radius:12px;padding:24px;text-align:center;margin:16px 0">
                <div style="color:#7ab890;font-size:0.9rem">Islamic Profit Benchmark for</div>
                <div style="color:#c9a84c;font-family:Amiri,serif;font-size:1.8rem;font-weight:700">
                    {selected_sector} → {selected_cluster}
                </div>
                <div style="color:#fff;font-size:3rem;font-weight:700;margin:8px 0">{benchmark:.2f}%</div>
                <div style="color:#a8c5b0;font-size:0.85rem">
                    Annualized | Based on real market returns | {selected_period_label} period
                </div>
                <div style="margin-top:10px">
                    <span style="background:{risk_color}22;color:{risk_color};border:1px solid {risk_color};
                                 border-radius:12px;padding:4px 16px;font-size:0.85rem">{risk_label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual company data
            st.markdown('<div class="section-title">📋 Company-Level Returns</div>', unsafe_allow_html=True)
            
            company_data = []
            for ticker, metrics in raw_data.items():
                try:
                    info = yf.Ticker(ticker).info
                    name = info.get('longName', ticker)
                except:
                    name = ticker
                company_data.append({
                    "Company": name[:30],
                    "Ticker": ticker,
                    "Annual Return (%)": round(metrics['return'], 2),
                    "Volatility (%)": round(metrics['volatility'], 2),
                    "Current Price ($)": round(metrics['current_price'], 2)
                })
            
            df = pd.DataFrame(company_data)
            
            # Color the return column
            def color_return(val):
                color = '#2ecc71' if val > 0 else '#e74c3c'
                return f'color: {color}'
            
            st.dataframe(
                df.style.applymap(color_return, subset=['Annual Return (%)']),
                use_container_width=True,
                hide_index=True
            )
            
            # Price history chart
            st.markdown('<div class="section-title">📈 Price Performance (Normalized)</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            colors_chart = ['#c9a84c', '#2ecc71', '#3498db', '#e67e22', '#9b59b6']
            
            for i, ticker in enumerate(tickers):
                try:
                    hist = yf.Ticker(ticker).history(period=selected_period)
                    if len(hist) > 5:
                        normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=normalized,
                            name=ticker,
                            line=dict(color=colors_chart[i % len(colors_chart)], width=2),
                            hovertemplate=f"<b>{ticker}</b><br>Normalized: %{{y:.1f}}<br>Date: %{{x}}<extra></extra>"
                        ))
                except:
                    pass
            
            fig.add_hline(y=100, line_dash="dot", line_color="#666",
                         annotation_text="Base (100)", annotation_font_color="#666")
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8d5a3', family='Cairo'),
                xaxis=dict(gridcolor='#1a3a2a'),
                yaxis=dict(gridcolor='#1a3a2a', title="Normalized Price (Base=100)"),
                legend=dict(bgcolor='rgba(13,33,55,0.8)', bordercolor='#2a6b47'),
                height=380
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # How to use this benchmark
            st.markdown(f"""
            <div class="info-box">
            <b>📌 How to Use This Benchmark in Islamic Finance:</b><br><br>
            If an Islamic bank wants to finance a business in <b>{selected_cluster}</b>:<br>
            • <b>Murabaha Rate</b>: Use <span style="color:#c9a84c;font-weight:700">{benchmark:.2f}%</span> as profit rate on cost-plus financing<br>
            • <b>Musharakah</b>: Share profits/losses based on actual sector performance ({benchmark:.2f}%)<br>
            • <b>Ijara</b>: Set rental rate linked to <span style="color:#c9a84c">{benchmark:.2f}%</span> sector benchmark<br>
            • <b>Risk Sharing</b>: Both bank and client accept <span style="color:{risk_color}">{risk_label}</span> profile of this sector
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  TAB 3: FINANCING CALCULATOR
# ═══════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">💰 Islamic Financing Calculator</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Calculate your Murabaha, Musharakah, or Ijara financing using real sector benchmarks — 
    not interest-based rates. Compare with conventional bank loans to see the difference.
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 🏦 Financing Details")
        calc_sector = st.selectbox("Business Sector", list(SECTORS.keys()), key="calc_sector")
        calc_cluster = st.selectbox("Sub-Sector / Cluster", 
                                     list(SECTORS[calc_sector]["clusters"].keys()), key="calc_cluster")
        calc_amount = st.number_input("Financing Amount ($)", min_value=1000, value=finance_amount, step=1000)
        calc_tenure = st.slider("Tenure (Months)", 3, 120, finance_tenure, key="calc_tenure")
        financing_type = st.selectbox("Financing Mode", 
                                       ["Murabaha (Cost+Profit)", "Diminishing Musharakah", "Ijara (Leasing)"])
        
        # Manual benchmark or auto
        use_manual = st.checkbox("Use Manual Benchmark Rate")
        if use_manual:
            manual_rate = st.number_input("Manual Benchmark Rate (%)", 1.0, 50.0, 12.0, 0.1)
        
    with c2:
        st.markdown("#### 📊 Calculation Results")
        
        if st.button("⚡ Calculate Now", use_container_width=True):
            
            # Get benchmark
            if use_manual:
                used_rate = manual_rate
            else:
                with st.spinner("Fetching sector benchmark..."):
                    tickers = SECTORS[calc_sector]["clusters"][calc_cluster]
                    benchmark_rate, volatility, _ = calculate_benchmark(tickers, admin_buffer/100)
                
                if benchmark_rate is None:
                    benchmark_rate = 12.0  # fallback
                    st.warning("Using fallback rate of 12%. Live data unavailable.")
                used_rate = benchmark_rate
            
            # Calculations
            monthly_rate = used_rate / 100 / 12
            tenure = calc_tenure
            principal = calc_amount
            
            # Monthly payment
            if monthly_rate > 0:
                monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
            else:
                monthly_payment = principal / tenure
            
            total_payment = monthly_payment * tenure
            total_profit = total_payment - principal
            
            # Conventional comparison (assume 22% KIBOR-based)
            conv_rate = 22.0 / 100 / 12
            conv_monthly = principal * (conv_rate * (1 + conv_rate)**tenure) / ((1 + conv_rate)**tenure - 1)
            conv_total = conv_monthly * tenure
            conv_interest = conv_total - principal
            
            savings = conv_total - total_payment
            
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:12px">
                <div class="label">Benchmark Rate Used</div>
                <div class="value">{used_rate:.2f}%</div>
                <div style="color:#7ab890;font-size:0.8rem">{calc_cluster} — Real Sector Return</div>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Monthly Payment</div>
                    <div class="value">${monthly_payment:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">Total Profit Paid</div>
                    <div class="value" style="color:#{'2ecc71' if total_profit < conv_interest else 'e74c3c'}">${total_profit:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d3b2e,#143d2b);border:1px solid #2a6b47;
                        border-radius:10px;padding:16px;margin:12px 0">
                <div style="color:#c9a84c;font-weight:700;margin-bottom:8px">💚 Savings vs Conventional Bank</div>
                <div style="color:#2ecc71;font-size:1.8rem;font-weight:700">${savings:,.0f}</div>
                <div style="color:#7ab890;font-size:0.8rem">
                    Conventional total: ${conv_total:,.0f} | Islamic total: ${total_payment:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Amortization chart
            schedule = []
            balance = principal
            for month in range(1, tenure + 1):
                profit_payment = balance * monthly_rate
                principal_payment = monthly_payment - profit_payment
                balance -= principal_payment
                schedule.append({
                    "Month": month,
                    "Principal": principal_payment,
                    "Profit": profit_payment,
                    "Balance": max(0, balance)
                })
            
            df_sched = pd.DataFrame(schedule)
            
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=["Payment Breakdown", "Outstanding Balance"])
            
            fig.add_trace(go.Bar(x=df_sched['Month'], y=df_sched['Principal'],
                                name='Principal', marker_color='#2ecc71'), row=1, col=1)
            fig.add_trace(go.Bar(x=df_sched['Month'], y=df_sched['Profit'],
                                name='Profit', marker_color='#c9a84c'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_sched['Month'], y=df_sched['Balance'],
                                    name='Balance', line=dict(color='#3498db', width=2),
                                    fill='tozeroy', fillcolor='rgba(52,152,219,0.1)'), row=1, col=2)
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8d5a3', family='Cairo'),
                barmode='stack', height=300,
                legend=dict(bgcolor='rgba(13,33,55,0.8)', bordercolor='#2a6b47'),
                margin=dict(t=30, b=10)
            )
            for i in [1, 2]:
                fig.update_xaxes(gridcolor='#1a3a2a', row=1, col=i)
                fig.update_yaxes(gridcolor='#1a3a2a', row=1, col=i)
            
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
#  TAB 4: MARKET TRENDS
# ═══════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📈 Market & Economic Trends</div>', unsafe_allow_html=True)
    
    # Major indices overview
    st.markdown("#### 🌍 Major Market Indices")
    
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI", 
        "NASDAQ": "^IXIC",
        "KSE-100 (Pakistan)": "^KSE",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225"
    }
    
    if st.button("📡 Load Market Data", use_container_width=True):
        with st.spinner("Fetching market data..."):
            market_data = {}
            for name, ticker in indices.items():
                try:
                    idx = yf.Ticker(ticker)
                    hist = idx.history(period="1mo")
                    if len(hist) > 2:
                        chg = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                        market_data[name] = {
                            'change': chg,
                            'current': hist['Close'].iloc[-1],
                            'hist': hist
                        }
                except:
                    pass
        
        if market_data:
            cols = st.columns(len(market_data))
            for i, (name, data) in enumerate(market_data.items()):
                with cols[i]:
                    color = "#2ecc71" if data['change'] > 0 else "#e74c3c"
                    arrow = "▲" if data['change'] > 0 else "▼"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="label" style="font-size:0.7rem">{name}</div>
                        <div class="value" style="font-size:1.2rem">{data['current']:,.0f}</div>
                        <div style="color:{color};font-size:0.9rem;font-weight:700">
                            {arrow} {abs(data['change']):.1f}%
                        </div>
                        <div style="color:#7ab890;font-size:0.7rem">1 Month</div>
                    </div>""", unsafe_allow_html=True)
            
            # Chart
            fig = go.Figure()
            chart_colors = ['#c9a84c', '#2ecc71', '#3498db', '#e67e22', '#9b59b6', '#1abc9c']
            for i, (name, data) in enumerate(market_data.items()):
                hist = data['hist']
                normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                fig.add_trace(go.Scatter(
                    x=hist.index, y=normalized, name=name,
                    line=dict(color=chart_colors[i % len(chart_colors)], width=2)
                ))
            
            fig.update_layout(
                title="1-Month Normalized Performance",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8d5a3', family='Cairo'),
                xaxis=dict(gridcolor='#1a3a2a'),
                yaxis=dict(gridcolor='#1a3a2a', title="Normalized (Base=100)"),
                legend=dict(bgcolor='rgba(13,33,55,0.8)', bordercolor='#2a6b47'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # World Bank economic indicators
    st.markdown('<div class="section-title">🏦 Economic Indicators (World Bank)</div>', unsafe_allow_html=True)
    
    wb_indicators = {
        "GDP Growth (%)": "NY.GDP.MKTP.KD.ZG",
        "Inflation (%)": "FP.CPI.TOTL.ZG",
        "Agricultural Value Added (% GDP)": "NV.AGR.TOTL.ZS",
        "Industry Value Added (% GDP)": "NV.IND.TOTL.ZS"
    }
    
    country_codes = {
        "Pakistan": "PK", "Malaysia": "MY", "Saudi Arabia": "SA",
        "UAE": "AE", "Bangladesh": "BD", "Global": "WLD"
    }
    
    selected_country_code = country_codes.get(country, "PK")
    
    if st.button("📊 Load Economic Indicators", use_container_width=True):
        with st.spinner("Fetching World Bank data..."):
            wb_results = {}
            for label, indicator in wb_indicators.items():
                values = fetch_world_bank_data(indicator, selected_country_code)
                if values:
                    wb_results[label] = values
        
        if wb_results:
            cols = st.columns(2)
            for i, (label, values) in enumerate(wb_results.items()):
                with cols[i % 2]:
                    years = list(range(2020, 2020 + len(values)))[::-1][:len(values)]
                    fig = go.Figure(go.Bar(
                        x=years, y=values[:len(years)],
                        marker_color=['#c9a84c' if v > 0 else '#e74c3c' for v in values[:len(years)]],
                        text=[f"{v:.1f}%" for v in values[:len(years)]],
                        textposition='outside', textfont=dict(color='#e8d5a3')
                    ))
                    fig.update_layout(
                        title=label,
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e8d5a3', family='Cairo', size=11),
                        xaxis=dict(gridcolor='#1a3a2a'),
                        yaxis=dict(gridcolor='#1a3a2a'),
                        height=280, margin=dict(t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No World Bank data available for {country}. Try a different country.")

# ═══════════════════════════════════════════
#  TAB 5: ISLAMIC FINANCE GUIDE
# ═══════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">📖 Islamic Finance Principles</div>', unsafe_allow_html=True)
    
    # Quranic verses
    verses = [
        {
            "ref": "Al-Baqarah 2:275",
            "arabic": "وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا",
            "translation": "Allah has permitted trade and forbidden interest (Riba)",
            "implication": "Foundation: All financing must be trade/asset-based, not interest-based"
        },
        {
            "ref": "Al-Baqarah 2:279",
            "arabic": "فَلَكُمْ رُءُوسُ أَمْوَالِكُمْ لَا تَظْلِمُونَ وَلَا تُظْلَمُونَ",
            "translation": "You shall have your principal — neither wronging others nor being wronged",
            "implication": "Capital preservation: You get your principal back, no exploitation"
        },
        {
            "ref": "Al-Baqarah 2:282",
            "arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنتُم بِدَيْنٍ إِلَىٰ أَجَلٍ مُّسَمًّى فَاكْتُبُوهُ",
            "translation": "O believers! When you contract a debt for a fixed term, write it down",
            "implication": "Transparency: All transactions must be documented — no hidden terms"
        },
        {
            "ref": "Al-Baqarah 2:245",
            "arabic": "مَّن ذَا الَّذِي يُقْرِضُ اللَّهَ قَرْضًا حَسَنًا",
            "translation": "Who will lend Allah a good loan (Qard-e-Hasana)?",
            "implication": "Social lending: Interest-free loans for the poor as religious obligation"
        }
    ]
    
    for verse in verses:
        st.markdown(f"""
        <div class="ayah-box" style="text-align:left;margin-bottom:16px">
            <div style="color:#c9a84c;font-size:0.8rem;margin-bottom:8px;letter-spacing:1px">
                📖 {verse['ref']}
            </div>
            <div class="ayah-arabic">{verse['arabic']}</div>
            <div class="ayah-translation">"{verse['translation']}"</div>
            <div style="color:#c9a84c;font-size:0.85rem;margin-top:10px;border-top:1px solid #2a6b47;padding-top:8px">
                💡 <b>Economic Implication:</b> {verse['implication']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Comparison table
    st.markdown('<div class="section-title">⚖️ Islamic vs Conventional Banking</div>', unsafe_allow_html=True)
    
    comparison = {
        "Basis of Return": ["Real sector profit (this system)", "Arbitrary interest rate (KIBOR/LIBOR)"],
        "Benchmark Source": ["Actual economic activity", "Central bank policy rate"],
        "Risk Distribution": ["Shared between bank & client", "Client bears all risk"],
        "Asset Requirement": ["Must be real, tangible asset", "Paper transaction only"],
        "Poor Protection": ["Rate based on actual sector", "Same rate regardless of your sector"],
        "Accountability": ["To Allah + Legal system", "Legal system only"],
        "Wealth Distribution": ["Zakat redistributes wealth", "Concentration of wealth"],
        "Crisis Behavior": ["Share losses in bad times", "Client owes even if bankrupt"],
    }
    
    df_comp = pd.DataFrame(comparison, index=["✅ Islamic (This System)", "❌ Conventional"]).T
    df_comp.index.name = "Feature"
    st.dataframe(df_comp, use_container_width=True)
    
    # How This System Differs from Fake Islamic Banking
    st.markdown('<div class="section-title">🚨 Why Existing Islamic Banks Are Failing</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>The Problem with Current "Islamic" Banks:</b><br><br>
    Current Islamic banks use <b>KIBOR/LIBOR + spread</b> as their benchmark, then rename the product 
    "Murabaha" or "Ijara". If KIBOR is 22%, their "profit rate" is mysteriously also ~22-24%.<br><br>
    <b>This system solves that by:</b><br>
    ✅ Using <b>actual sector returns</b> from real companies as the benchmark<br>
    ✅ If wheat farming returns 8% — wheat farmers pay 8-9%, not 22%<br>
    ✅ If tech sector returns 25% — tech financing costs 26%, justified by real returns<br>
    ✅ Bank shares in the <b>real risk</b> of the sector — no guaranteed return<br>
    ✅ Fully <b>transparent and auditable</b> — all data is public
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;padding:30px;color:#2a6b47;font-size:0.8rem;border-top:1px solid #1a3a2a;margin-top:40px">
    <div style="font-family:'Amiri',serif;color:#c9a84c;font-size:1.1rem">
        بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ
    </div>
    <div style="margin-top:8px">
        Islamic Profit Benchmark System — Building a Just Financial Economy Based on Quran & Real Data<br>
        Data sources: Yahoo Finance • World Bank API • Stock Exchanges
    </div>
</div>
""", unsafe_allow_html=True)
