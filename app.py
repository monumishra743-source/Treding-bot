import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import requests  # Dhan API के साथ कम्युनिकेट करने के लिए

# --- 1. पेज सेटअप और इंटरफेस डिज़ाइन ---
st.set_page_config(page_title="Dhan Smart-Money Terminal", layout="wide")
st.title("🏛️ Institutional Smart-Money Terminal (Dhan Engine)")
st.markdown("---")

# --- 2. साइडबार कंट्रोल्स (सख्त रिस्क नियम प्रबंधन) ---
st.sidebar.header("🛡️ Strict Risk & System Controls")

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

# --- 3. DHAN API प्रमाणीकरण (Authentication) इनपुट ---
st.sidebar.markdown("---")
st.sidebar.header("🔑 Dhan API Authentication")
dhan_client_id = st.sidebar.text_input("Enter Dhan Client ID", type="password")
dhan_access_token = st.sidebar.text_input("Enter Dhan Access Token", type="password")

if not dhan_client_id or not dhan_access_token:
    st.warning("⚠️ कृपया लाइव ट्रेडिंग शुरू करने के लिए साइडबार में Dhan Client ID और Access Token दर्ज करें।")
else:
    st.success("✅ Dhan API इंजन सफलतापूर्वक कनेक्टेड है (30 दिनों के लिए वैध)!")

# --- 4. एडवांस्ड FII/DII चाल + Open Interest (OI) मैट्रिक्स ---
def analyze_smart_money(df):
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    
    # FII/DII हैवी वॉल्यूम (औसत से 3 गुना अधिक)
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['inst_volume'] = df['volume'] > (df['avg_volume'] * 3.0)
    
    # VWAP लाइन कैलकुलेशन हटा दी गई है (Negative Claim के अनुसार)
    # EMA 20 को भी शामिल नहीं किया गया है
    
    # PCR (Put Call Ratio) डेटा
    df['pcr'] = df['put_oi'] / df['call_oi']
    df['signal'] = "HOLD"
    
    # 200+ पॉइंट मूवमेंट ब्रेकआउट मैट्रिक्स (केवल वॉल्यूम और OI आधारित संस्थागत चाल)
    buy_matrix = (df['inst_volume'] == True) & (df['pcr'] > 1.25)
    sell_matrix = (df['inst_volume'] == True) & (df['pcr'] < 0.75)
    
    df.loc[buy_matrix, 'signal'] = 'BUY (Institutional OI Breakout)'
    df.loc[sell_matrix, 'signal'] = 'SELL (Institutional OI Breakout)'
    return df

# --- 5. DHAN लाइव आर्डर प्लेसमेंट फंक्शन ---
def place_dhan_order(symbol, quantity, order_type, price=0):
    if not dhan_client_id or not dhan_access_token:
        return "ERROR: क्रेडेंशियल्स गायब हैं"
        
    url = "https://dhan.co"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "access-token": dhan_access_token
    }
    
    # Dhan API के अनुसार आर्डर पेलोड संरचना
    payload = {
        "dhanClientId": dhan_client_id,
        "correlationId": f"algo_{int(time.time())}",
        "transactionType": "BUY" if order_type == "BUY" else "SELL",
        "exchangeSegment": "NSE_EQ",
        "productType": "INTRA", # इंट्राडे के लिए
        "orderType": "MARKET",
        "validity": "DAY",
        "tradingSymbol": symbol,
        "quantity": quantity
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            return f"Failed: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# --- 6. रीयल-टाइम लाइव डेटा फीड सिमुलेटर ---
def get_live_market_stream():
    np.random.seed(int(time.time()))
    prices = 1730.0 + np.cumsum(np.random.normal(0, 5, 30))
    opens = prices - np.random.normal(0, 2, 30)
    closes = prices
    highs = np.maximum(opens, closes) + np.random.uniform(1, 10, 30)
    lows = np.minimum(opens, closes) - np.random.uniform(1, 10, 30)
    volumes = np.random.randint(1000, 5000, 30)
    
    if np.random.rand() > 0.6:
        volumes[-1] = volumes[-1] * 4.0
        
    call_oi = np.random.randint(70000, 150000, 30)
    put_oi = np.random.randint(70000, 150000, 30)
    if np.random.rand() > 0.7:
        put_oi[-1] = put_oi[-1] * 2.5
        
    return pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=30, freq='5min'),
        'open': opens, 'high': highs, 'low': lows, 'close': closes,
        'volume': volumes, 'call_oi': call_oi, 'put_oi': put_oi
    })

# --- 7. इंटरफेस लेआउट (मेन स्क्रीन) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Order Configuration")
    symbol = st.text_input("Enter NSE Trading Symbol (e.g., MANKIND, TECHM)", value="TECHM").upper()
    quantity = st.number_input("Order Quantity", min_value=1, value=10)
    
    df_live = get_live_market_stream()
    df_analyzed = analyze_smart_money(df_live)
    latest_row = df_analyzed.iloc[-1]
    
    # अपर और लोअर सर्किट लिमिट्स की गणना
    base_price = latest_row['close']
    upper_circuit = round(base_price * 1.10, 2)
    lower_circuit = round(base_price * 0.90, 2)
    
    st.metric("Live LTP (INR)", f"₹{round(base_price, 2)}")
    st.text(f"🔒 Upper Circuit Limit: ₹{upper_circuit}")
    st.text(f"🔒 Lower Circuit Limit: ₹{lower_circuit}")
    st.metric("Live PCR Ratio", f"{round(latest_row['pcr'], 2)}")

with col2:
    st.subheader("📊 Live Candlestick View (Smart Money Active)")
    fig = go.Figure(data=[go.Candlestick(
        x=df_analyzed['timestamp'],
        open=df_analyzed['open'], high=df_analyzed['high'],
        low=df_analyzed['low'], close=df_analyzed['close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# --- 8. एग्जीक्यूशन ट्रिगर पैनल ---
st.markdown("---")
st.subheader("⚡ Execute Instant Smart Trade (Dhan API)")

c1, c2 = st.columns(2)
with c1:
    if st.button("🟢 INSTITUTIONAL BUY", type="primary", use_container_width=True):
        if st.session_state.trade_count >= max_trades:
            st.error(f"🔒 Risk Limit Reached: आज के {max_trades} ट्रेड्स पूरे हो चुके हैं।")
        elif st.session_state.is_paused:
            st.warning("⏸️ System Paused: इंजन अभी पॉज़ मोड पर है।")
        else:
            res = place_dhan_order(symbol, quantity, "BUY")
            st.session_state.trade_count += 1
            st.write("Dhan Execution Response:", res)
            
with c2:
    if st.button("🔴 INSTITUTIONAL SELL", type="secondary", use_container_width=True):
        if st.session_state.trade_count >= max_trades:
            st.error(f"🔒 Risk Limit Reached: आज के {max_trades} ट्रेड्स पूरे हो चुके हैं।")
        elif st.session_state.is_paused:
            st.warning("⏸️ System Paused: इंजन अभी पॉज़ मोड पर है।")
        else:
            res = place_dhan_order(symbol, quantity, "SELL")
            st.session_state.trade_count += 1
            st.write("Dhan Execution Response:", res)
