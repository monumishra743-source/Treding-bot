import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- 1. पेज सेटअप और इंटरफेस डिज़ाइन ---
st.set_page_config(page_title="Institutional Candlestick Engine", layout="wide")
st.title("🏛️ Institutional Smart-Money Terminal with Candlestick View")
st.markdown("---")

# --- 2. एडवांस्ड लाइव ऑडियो सायरन (Sound Engine) ---
def play_institutional_alert():
    sound_html = """
    <audio autoplay class="stAudio">
    <source src="https://soundhelix.com" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- 3. साइडबार कंट्रोल्स (सख्त रिस्क नियम प्रबंधन और टोकन इनपुट) ---
st.sidebar.header("🛡️ Strict Risk & System Controls")

# API टोकन इनपुट बॉक्स
api_token = st.sidebar.text_input("Enter Dhan API Token", type="password", placeholder="Paste your Dhan token here")

if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False

pause_btn = st.sidebar.button(
    "⏸️ PAUSE ENGINE" if not st.session_state.is_paused else "▶️ RESUME ENGINE",
    type="primary" if not st.session_state.is_paused else "secondary"
)
if pause_btn:
    st.session_state.is_paused = not st.session_state.is_paused

# पैनिक किल-स्विच (Emergency Hard Stop)
st.sidebar.markdown("---")
if st.sidebar.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
    st.session_state.is_paused = True
    st.session_state.trade_count = 5
    st.toast("Emergency Kill Switch Activated! All systems halted.", icon="🚨")

max_trades = st.sidebar.number_input("Maximum Daily Trades Limit", min_value=1, max_value=5, value=5)
max_loss_limit = st.sidebar.number_input("Max Daily Loss Cap (INR)", min_value=100, max_value=500, value=500)

if 'trade_count' not in st.session_state:
    st.session_state.trade_count = 0
if 'daily_pnl' not in st.session_state:
    st.session_state.daily_pnl = 0.0
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

# --- 4. एडवांस्ड FII/DII चाल + Open Interest (OI) मैट्रिक्स ---
def analyze_smart_money(df):
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    # FII/DII हैवी वॉल्यूम (औसत से 3 गुना अधिक)
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['inst_volume'] = df['volume'] > (df['avg_volume'] * 3.0)
    
    # VWAP लाइन कैलकुलेशन
    df['cum_vol_price'] = (df['close'] * df['volume']).cumsum()
    df['cum_vol'] = df['volume'].cumsum()
    df['vwap'] = df['cum_vol_price'] / df['cum_vol']
    
    # PCR (Put Call Ratio) डेटा
    df['pcr'] = df['put_oi'] / df['call_oi']
    df['signal'] = "HOLD"
    
    # 200+ पॉइंट मूवमेंट ब्रेकआउट मैट्रिक्स
    buy_matrix = (df['close'] > df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] > 1.25)
    sell_matrix = (df['close'] < df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] < 0.75)
    
    df.loc[buy_matrix, 'signal'] = 'BUY (Institutional OI Breakout)'
    df.loc[sell_matrix, 'signal'] = 'SELL (Institutional OI Breakout)'
    return df

# --- 5. रियल-टाइम लाइव डेटा फीड सिम्युलेटर ---
def get_live_market_stream():
    np.random.seed(int(time.time()))
    prices = 9300.0 + np.cumsum(np.random.normal(0, 12, 30))
    opens = prices - np.random.normal(0, 4, 30)
    closes = prices
    highs = np.maximum(opens, closes) + np.random.uniform(2, 15, 30)
    lows = np.minimum(opens, closes) - np.random.uniform(2, 15, 30)
    volumes = np.random.randint(1000, 5000, 30)
    if np.random.rand() > 0.6:
        volumes[-1] = volumes[-1] * 4.0
    call_oi = np.random.randint(70000, 150000, 30)
    put_oi = np.random.randint(70000, 150000, 30)
    if np.random.rand() > 0.7:
        put_oi[-1] = put_oi[-1] * 2.5
        
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=30, freq='5min'),
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes,
        'call_oi': call_oi,
        'put_oi': put_oi
    })

# --- 6. रिस्क मैनेजमेंट और नियम अनुपालन चेकर ---
def process_risk_and_execution(signal, price, atr_val, pcr_val):
    if st.session_state.is_paused:
        return "SYSTEM STATUS: इंजन अभी पॉज़ मोड पर है।"
    if st.session_state.daily_pnl <= -max_loss_limit:
        return f"🔒 RISK BLOCK: ₹{max_loss_limit} दैनिक नुकसान सीमा पार! ट्रेडिंग लॉक्ड।"
    if st.session_state.trade_count >= max_trades:
        return f"💡 BROKERAGE SAVED: आज के {max_trades} ट्रेड्स पूरे हो चुके हैं।"
    if "HOLD" in signal:
        return None
        
    play_institutional_alert()
    st.session_state.trade_count += 1
    sl = round(2.5 * atr_val, 2)
    tp = round(7.5 * atr_val, 2)
    
    trade_log = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Type": signal,
        "Entry Price": round(price, 2),
        "Stop Loss": round(price - sl if "BUY" in signal else price + sl, 2),
        "Target (200+ Move)": round(price + tp if "BUY" in signal else price - tp, 2),
        "PCR Value": round(pcr_val, 2),
        "Status": "🔔 ALARM TRIGGERED"
    }
    st.session_state.trade_history.append(trade_log)
    return f"🚀 {signal} एग्जीक्यूट हुआ! एंट्री: {round(price,2)}"

# --- 7. इंजन रन और लाइव डैशबोर्ड रेंडरिंग ---
df = get_live_market_stream()
df = analyze_smart_money(df)

latest_row = df.iloc[-1]
status_msg = process_risk_and_execution(latest_row['signal'], latest_row['close'], latest_row['atr'], latest_row['pcr'])

# डैशबोर्ड मेट्रिक्स डिस्प्ले
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Price", f"₹{round(latest_row['close'], 2)}")
m2.metric("Daily Trades", f"{st.session_state.trade_count} / {max_trades}")
m3.metric("Daily P&L", f"₹{st.session_state.daily_pnl}")
m4.metric("Market Status", "🟢 OPEN" if not st.session_state.is_paused else "⏸️ PAUSED")

if status_msg:
    st.info(status_msg)

# कैंडलस्टिक चार्ट क्रिएशन
fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    name="Market Feed"
)])
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['vwap'], name="Institutional VWAP", line=dict(color='orange', width=2)))
fig.update_layout(title="Live Institutional Candlestick Feed", xaxis_rangeslider_visible=False, height=500)
st.plotly_chart(fig, use_container_width=True)

# ट्रेड हिस्ट्री लॉग टेबल
if st.session_state.trade_history:
    st.subheader("📜 Today's Smart-Money Trade Logs")
    st.table(pd.DataFrame(st.session_state.trade_history))

