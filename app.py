import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- 1. मोबाइल ऑप्टिमाइज्ड ऐप सेटअप ---
st.set_page_config(
    page_title="Institutional Engine",
    layout="wide",
    initial_sidebar_state="collapsed" # मोबाइल पर साइडबार पहले से बंद रहेगा ताकि पूरी स्क्रीन मिले
)

# मोबाइल स्क्रीन के लिए कस्टम CSS स्टाइलिंग (स्मूथ स्क्रॉलिंग और फॉन्ट)
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 100%; padding-top: 1rem; padding-right: 1rem; padding-left: 1rem; padding-bottom: 1rem; }
    .stRadio > div { flex-direction: row; justify-content: space-around; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Smart-Money Terminal")
st.markdown("---")

# --- 2. मोबाइल फ्रेंडली रिस्क कंट्रोल्स (साइडबार) ---
st.sidebar.header("🛡️ System & Risk Controls")

if 'is_paused' not in st.session_state: st.session_state.is_paused = False
if 'trade_count' not in st.session_state: st.session_state.trade_count = 0
if 'trade_history' not in st.session_state: st.session_state.trade_history = []

pause_lbl = "▶️ RESUME SCANNER" if st.session_state.is_paused else "⏸️ PAUSE SCANNER"
if st.sidebar.button(pause_lbl, use_container_width=True):
    st.session_state.is_paused = not st.session_state.is_paused

if st.sidebar.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
    st.session_state.is_paused = True
    st.session_state.trade_count = 5
    st.toast("Emergency Kill Switch Activated!", icon="🚨")

max_trades = st.sidebar.number_input("Daily Trade Limit", min_value=1, max_value=5, value=5)
max_loss = st.sidebar.number_input("Max Loss Cap (INR)", min_value=100, max_value=500, value=500)

# --- 3. ट्रेडिंग मोड सिलेक्शन ---
trade_mode = st.radio("Strategy Mode:", ["Intraday (5-Min)", "Holding / Delivery (Daily)"])
st.markdown("---")

# --- 4. हाई-स्पीड मल्टी-एसेट डेटा इंजन ---
@st.cache_data(ttl=10) # 10 सेकंड का कैश ताकि मोबाइल पर लोड कम पड़े और ऐप स्मूथ चले
def get_market_data_cached(mode_key, seed_time):
    categories = {
        "Equity Shares": ["Mankind Pharma", "Adani Green", "Reliance"],
        "Futures & Options": ["Bank Nifty Index", "Nifty 50 Index"],
        "Commodities (MCX)": ["Crude Oil", "Natural Gas"]
    }
    discovered = {}
    np.random.seed(seed_time)
    freq = '5min' if "Intraday" in mode_key else 'D'
    
    for cat, items in categories.items():
        for item in items:
            base = 6200 if "Crude" in item else (220 if "Natural" in item else np.random.uniform(300, 3000))
            prices = base + np.cumsum(np.random.normal(0, base*0.008, 30))
            opens = prices - np.random.normal(0, base*0.002, 30)
            highs = np.maximum(opens, prices) + np.random.uniform(1, base*0.005, 30)
            lows = np.minimum(opens, prices) - np.random.uniform(1, base*0.005, 30)
            volumes = np.random.randint(2000, 8000, 30)
            
            if item in ["Mankind Pharma", "Natural Gas", "Bank Nifty Index"] and np.random.rand() > 0.4:
                volumes[-1] *= 3.5 
                
            call_oi = np.random.randint(50000, 120000, 30)
            put_oi = np.random.randint(50000, 120000, 30)
            if "Index" in item or "Pharma" in item: put_oi[-1] *= 2.5
                
            discovered[item] = {
                "category": cat,
                "df": pd.DataFrame({
                    'timestamp': pd.date_range(end=datetime.now(), periods=30, freq=freq),
                    'open': opens, 'high': highs, 'low': lows, 'close': prices,
                    'volume': volumes, 'call_oi': call_oi, 'put_oi': put_oi
                })
            }
    return discovered

# --- 5. FII/DII संस्थागत चाल का एनालिसिस ---
def analyze_signals(df):
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=10) # ATR 10
    df['avg_vol'] = df['volume'].rolling(window=20).mean()
    df['inst_vol'] = df['volume'] > (df['avg_vol'] * 3.0)
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    df['pcr'] = df['put_oi'] / df['call_oi']
    df['signal'] = "HOLD"
    
    buy_cond = (df['close'] > df['vwap']) & (df['inst_vol'] == True) & (df['pcr'] > 1.20)
    sell_cond = (df['close'] < df['vwap']) & (df['inst_vol'] == True) & (df['pcr'] < 0.80)
    
    df.loc[buy_cond, 'signal'] = 'BUY (FII/DII Breakout)'
    df.loc[sell_cond, 'signal'] = 'SELL (FII/DII Breakout)'
    return df

# --- 6. सिग्नल और अलर्ट प्रोसेसिंग ---
all_assets = get_market_data_cached(trade_mode, int(time.time() // 10))
triggered_alerts = []

for name, info in all_assets.items():
    df_scan = analyze_signals(info["df"])
    last_row = df_scan.iloc[-1]
    
    if last_row['signal'] != "HOLD" and not st.session_state.is_paused:
        if "Intraday" in trade_mode and st.session_state.trade_count < max_trades:
            st.session_state.trade_count += 1
            
        sl = round(2.5 * last_row['atr'], 2)
        tp = round(7.5 * last_row['atr'], 2)
        
        triggered_alerts.append(f"🚀 **[{info['category']}] {name}**: {last_row['signal']} | Price: ₹{round(last_row['close'],2)} (SL: {round(last_row['close']-sl,1)} / TP: {round(last_row['close']+tp,1)})")

# सिग्नल्स को टॉप पर दिखाना
if triggered_alerts:
    for alert in triggered_alerts: st.success(alert)
else:
    st.info("🔄 स्कैनिंग जारी है... सभी एसेट्स 'HOLD' मोड में बड़े वॉल्यूम ब्लास्ट का इंतज़ार कर रहे हैं।")

# --- 7. मोबाइल फ्रेंडली डैशबोर्ड और कॉम्पैक्ट चार्ट ---
m1, m2 = st.columns(2)
m1.metric("Scanned", f"{len(all_assets)} Assets")
m2.metric("Signals Executed", f"{st.session_state.trade_count} / {max_trades}")

st.markdown("---")
selected_asset = st.selectbox("🎯 Click to view Asset Chart:", list(all_assets.keys()))

disp_df = analyze_signals(all_assets[selected_asset]["df"])
fig = go.Figure(data=[go.Candlestick(
    x=disp_df['timestamp'], open=disp_df['open'], high=disp_df['high'],
    low=disp_df['low'], close=disp_df['close'], name=selected_asset
)])
fig.add_trace(go.Scatter(x=disp_df['timestamp'], y=disp_df['vwap'], name="VWAP", line=dict(color='orange', width=2)))
fig.update_layout(xaxis_rangeslider_visible=False, height=350, margin=dict(l=5, r=5, t=10, b=5))
st.plotly_chart(fig, use_container_width=True)
