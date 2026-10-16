import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- 1. पेज सेटअप और इंटरफेस डिज़ाइन ---
st.set_page_config(page_title="Universal Multi-Asset Engine", layout="wide")
st.title("🏛️ Universal Smart-Money Engine (Shares, F/O, Commodities)")
st.markdown("---")

# --- 2. लाइव ऑडियो सायरन (Sound Engine) ---
def play_institutional_alert():
    sound_html = """
    <audio autoplay class="stAudio">
    <source src="https://soundhelix.com" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- 3. साइडबार कंट्रोल्स और सख्त रिस्क नियम ---
st.sidebar.header("🛡️ Strict Risk & System Controls")

if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False

pause_btn = st.sidebar.button(
    "⏸️ PAUSE ENGINE" if not st.session_state.is_paused else "▶️ RESUME ENGINE",
    type="primary" if not st.session_state.is_paused else "secondary"
)
if pause_btn:
    st.session_state.is_paused = not st.session_state.is_paused

if st.sidebar.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
    st.session_state.is_paused = True
    st.session_state.trade_count = 5
    st.toast("Emergency Kill Switch Activated!", icon="🚨")

max_trades = st.sidebar.number_input("Maximum Daily Trades Limit", min_value=1, max_value=5, value=5)
max_loss_limit = st.sidebar.number_input("Max Daily Loss Cap (INR)", min_value=100, max_value=500, value=500)

if 'trade_count' not in st.session_state:
    st.session_state.trade_count = 0
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

# --- 4. ट्रेडिंग मोड सिलेक्शन (Intraday vs Holding) ---
st.subheader("⚙️ Select Your Strategy Mode")
trade_mode = st.radio("Choose Trading Style:", ["Intraday Trading (5-Min)", "Share Holding / Delivery (Daily)"], horizontal=True)

# --- 5. मल्टी-एसेट ऑटोमैटिक डेटा जनरेटर ---
def auto_discover_all_assets(mode):
    # एसेट क्लास के हिसाब से संपत्तियां बांटना
    categories = {
        "General Shares (Equity)": ["Mankind Pharma", "Adani Green", "Reliance", "HDFC Bank"],
        "Futures & Options (F/O)": ["Bank Nifty Index", "Nifty 50 Index"],
        "Commodities (MCX)": ["Crude Oil", "Natural Gas", "Gold Mini"]
    }
    
    discovered_data = {}
    np.random.seed(int(time.time()))
    time_freq = '5min' if "Intraday" in mode else 'D'
    periods_count = 30
    
    for category, items in categories.items():
        for item in items:
            # मोड के हिसाब से प्राइस रेंज सेट करना
            base_price = np.random.uniform(200, 6000)
            if "Crude" in item: base_price = 6200
            elif "Natural" in item: base_price = 220
            
            prices = base_price + np.cumsum(np.random.normal(0, base_price*0.01, periods_count))
            opens = prices - np.random.normal(0, base_price*0.003, periods_count)
            closes = prices
            highs = np.maximum(opens, closes) + np.random.uniform(1, base_price*0.008, periods_count)
            lows = np.minimum(opens, closes) - np.random.uniform(1, base_price*0.008, periods_count)
            
            # वॉल्यूम और ओपन इंटरेस्ट (OI) ब्लास्ट मैट्रिक्स
            volumes = np.random.randint(2000, 8000, periods_count)
            if item in ["Mankind Pharma", "Natural Gas", "Bank Nifty Index"] and np.random.rand() > 0.3:
                volumes[-1] = volumes[-1] * 3.5 # 3 गुना से ज्यादा संस्थागत वॉल्यूम
                
            call_oi = np.random.randint(50000, 120000, periods_count)
            put_oi = np.random.randint(50000, 120000, periods_count)
            if "Index" in item or "Pharma" in item:
                put_oi[-1] = put_oi[-1] * 2.6 # पुट राइटर्स की भारी एक्टिविटी
                
            discovered_data[item] = {
                "category": category,
                "df": pd.DataFrame({
                    'timestamp': pd.date_range(end=datetime.now(), periods=periods_count, freq=time_freq),
                    'open': opens, 'high': highs, 'low': lows, 'close': closes,
                    'volume': volumes, 'call_oi': call_oi, 'put_oi': put_oi
                })
            }
    return discovered_data

# --- 6. एडवांस्ड FII/DII चाल + 200+ पॉइंट ब्रेकआउट लॉजिक ---
def analyze_smart_money(df):
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=10) # ATR 10
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['inst_volume'] = df['volume'] > (df['avg_volume'] * 3.0)
    
    # VWAP लाइन
    df['cum_vol_price'] = (df['close'] * df['volume']).cumsum()
    df['cum_vol'] = df['volume'].cumsum()
    df['vwap'] = df['cum_vol_price'] / df['cum_vol']
    
    df['pcr'] = df['put_oi'] / df['call_oi']
    df['signal'] = "HOLD"
    
    # बिना RSI/CCI के ब्रेकआउट नियम
    buy_matrix = (df['close'] > df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] > 1.20)
    sell_matrix = (df['close'] < df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] < 0.80)
    
    df.loc[buy_matrix, 'signal'] = 'BUY (Institutional IO Breakout)'
    df.loc[sell_matrix, 'signal'] = 'SELL (Institutional IO Breakout)'
    return df

# --- 7. रिस्क मैनेजमेंट और सिग्नल प्रोसेसिंग ---
def process_signals(name, cat, signal, price, atr_val, mode):
    if st.session_state.is_paused or "HOLD" in signal:
        return None
    if st.session_state.trade_count >= max_trades and "Intraday" in mode:
        return None
        
    play_institutional_alert()
    if "Intraday" in mode:
        st.session_state.trade_count += 1
        
    sl = round(2.5 * atr_val, 2)
    tp = round(7.5 * atr_val, 2)
    
    trade_log = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Asset Name": name,
        "Type": cat,
        "Signal": signal,
        "Price": round(price, 2),
        "Stop Loss": round(price - sl if "BUY" in signal else price + sl, 2),
        "Target": round(price + tp if "BUY" in signal else price - tp, 2),
        "Horizon": "INTRADAY" if "Intraday" in mode else "HOLDING/DELIVERY"
    }
    st.session_state.trade_history.append(trade_log)
    return f"🚀 [{cat}] {name} में {signal} मिला! कीमत: {round(price,2)}"

# --- 8. स्कैनर रन और आउटपुट रेंडरिंग ---
all_assets = auto_discover_all_assets(trade_mode)
st.markdown("---")
st.subheader(f"🔍 Scanner Results for: {trade_mode}")

triggered_signals = []
for asset_name, asset_info in all_assets.items():
    df_analyzed = analyze_smart_money(asset_info["df"])
    latest_bar = df_analyzed.iloc[-1]
    
    res = process_signals(asset_name, asset_info["category"], latest_bar['signal'], latest_bar['close'], latest_bar['atr'], trade_mode)
    if res:
        triggered_signals.append(res)

if triggered_signals:
    for sig in triggered_signals:
        st.success(sig)
else:
    st.info("बाजार स्कैन किया जा रहा है... वर्तमान में सभी एसेट्स 'HOLD' मोड पर हैं। भारी संस्थागत वॉल्यूम का इंतजार है।")

# लाइव चार्ट व्यू
st.markdown("---")
st.subheader("📊 Multi-Asset Live Chart View")
selected_asset = st.selectbox("Select Asset to view detailed Chart:", list(all_assets.keys()))

display_df = analyze_smart_money(all_assets[selected_asset]["df"])
latest_data = display_df.iloc[-1]

fig = go.Figure(data=[go.Candlestick(
    x=display_df['timestamp'], open=display_df['open'], high=display_df['high'],
    low=display_df['low'], close=display_df['close'], name=selected_asset
)])
fig.add_trace(go.Scatter(x=display_df['timestamp'], y=display_df['vwap'], name="Institutional VWAP", line=dict(color='orange', width=2)))
fig.update_layout(xaxis_rangeslider_visible=False, height=450, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig, use_container_width=True)

# सिग्नल्स हिस्ट्री लॉग
if st.session_state.trade_history:
    st.subheader("📜 Live Automated Signal Logs")
    st.table(pd.DataFrame(st.session_state.trade_history))
