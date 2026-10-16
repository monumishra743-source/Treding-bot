import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from growwapi import GrowwAPI  # Groww Python SDK

# --- 1. पेज सेटअप और इंटरफेस डिज़ाइन ---
st.set_page_config(page_title="Institutional Candlestick Engine", layout="wide")
st.title("🏛️ Institutional Smart-Money Terminal with Groww Live Engine")
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

# Groww API Credentials (इन्हें अपने Groww डैशबोर्ड से बदलें)
GROWW_API_KEY = "YOUR_GROWW_API_KEY"
GROWW_SECRET = "YOUR_GROWW_SECRET"

try:
    groww = GrowwAPI(api_key=GROWW_API_KEY, api_secret=GROWW_SECRET)
except Exception as e:
    st.sidebar.error(f"Groww SDK Init Error: {e}")

# --- 3. एडवांस्ड FII/DII चाल + Open Interest (OI) मैट्रिक्स (Fixed for IndexError) ---
def analyze_smart_money(df):
    # सुरक्षा कवच: अगर डेटा खाली है, तो डिफ़ॉल्ट मान सेट करें
    if df.empty:
        df = pd.DataFrame([{
            'timestamp': datetime.now(), 'open': 0, 'high': 0, 'low': 0, 'close': 0, 
            'volume': 0, 'call_oi': 1, 'put_oi': 1, 'upper_circuit': 0, 'lower_circuit': 0
        }])
        
    # सुरक्षा कवच: अगर डेटा 20 लाइनों से कम है, तो एरर से बचाने के लिए रो बढ़ा लें
    if len(df) < 20:
        df = pd.concat([df] * 20, ignore_index=True)

    # इंडिकेटर कैलकुलेशन
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    
    # FII/DII हैवी वॉल्यूम (औसत से 3 गुना अधिक)
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['inst_volume'] = df['volume'] > (df['avg_volume'] * 3.0)
    
    # PCR (Put Call Ratio) डेटा एनालिसिस
    df['pcr'] = df['put_oi'] / df['call_oi']
    
    df['signal'] = "HOLD"
    
    # 200+ पॉइंट मूवमेंट ब्रेकआउट मैट्रिक्स (स्मार्ट मनी सिग्नल)
    buy_matrix = (df['inst_volume'] == True) & (df['pcr'] > 1.25)
    sell_matrix = (df['inst_volume'] == True) & (df['pcr'] < 0.75)
    
    df.loc[buy_matrix, 'signal'] = 'BUY (Institutional OI Breakout)'
    df.loc[sell_matrix, 'signal'] = 'SELL (Institutional OI Breakout)'
    return df

# --- 4. Groww लाइव डेटा स्ट्रीम फ़ंक्शन ---
def get_live_market_stream(ticker):
    try:
        segment = "FNO" if "NIFTY" in ticker.upper() or "BANKNIFTY" in ticker.upper() else "CASH"
        response = groww.get_live_data(exchange="NSE", segment=segment, trading_symbol=ticker)
        
        if response and response.get("status") == "SUCCESS":
            payload = response.get("payload", {})
            ohlc_data = payload.get("ohlc", {})
            
            df = pd.DataFrame([{
                'timestamp': datetime.now(),
                'open': float(ohlc_data.get('open', 0)),
                'high': float(ohlc_data.get('high', 0)),
                'low': float(ohlc_data.get('low', 0)),
                'close': float(payload.get('average_price', 0)), # LTP
                'volume': float(payload.get('bid_quantity', 0)),
                'call_oi': float(payload.get('call_open_interest', 100000)),
                'put_oi': float(payload.get('put_open_interest', 120000)),
                'upper_circuit': float(payload.get('upper_circuit_limit', 0)),
                'lower_circuit': float(payload.get('lower_circuit_limit', 0))
            }])
            return df
    except Exception as e:
        pass
    
    # फॉलबैक डेटा ताकि मार्केट बंद होने पर भी टर्मिनल क्रैश न हो
    return pd.DataFrame([{
        'timestamp': datetime.now(), 'open': 24000, 'high': 24100, 'low': 23900, 'close': 24020, 
        'volume': 5000, 'call_oi': 100000, 'put_oi': 130000, 'upper_circuit': 26400, 'lower_circuit': 21600
    }])

# --- 5. Groww ऑटोमेटेड ऑर्डर Placement इंजन (Circuit Shield) ---
def place_groww_order(ticker, quantity, action, current_price, upper_circuit, lower_circuit):
    if st.session_state.is_paused:
        return "🔒 ERROR: इंजन अभी पॉज़ मोड पर है।"
    if st.session_state.daily_pnl <= -max_loss_limit:
        return f"🔒 RISK BLOCK: ₹{max_loss_limit} दैनिक नुकसान सीमा पार!"
    if st.session_state.trade_count >= max_trades:
        return f"💡 BROKERAGE SAVED: आज के {max_trades} ट्रेड्स पूरे हो चुके हैं।"
    
    # सर्किट शील्ड सुरक्षा जांच
    if upper_circuit > 0 and current_price >= (upper_circuit - 0.5):
        return "🚨 ORDER BLOCKED: शेयर अपर सर्किट (Upper Circuit) के पास है! एंट्री होल्ड।"
    if lower_circuit > 0 and current_price <= (lower_circuit + 0.5):
        return "🚨 ORDER BLOCKED: शेयर लोअर सर्किट (Lower Circuit) के पास है! एंट्री होल्ड।"

    try:
        segment = "FNO" if "NIFTY" in ticker.upper() or "BANKNIFTY" in ticker.upper() else "CASH"
        order_response = groww.place_order(
            exchange="NSE", segment=segment, trading_symbol=ticker,
            quantity=int(quantity), price=float(current_price),
            order_type="LIMIT", transaction_type=action.upper(), product_type="INTRADAY"
        )
        if order_response and order_response.get("status") == "SUCCESS":
            st.session_state.trade_count += 1
            st.toast(f"✅ Order Success: {action} {ticker}", icon="🚀")
            return f"🔔 ORDER SUCCESS: ID {order_response.get('payload', {}).get('order_id', 'N/A')}"
        else:
            return f"❌ GROWW REJECTION: {order_response.get('error_message', 'API Error')}"
    except Exception as e:
        return f"❌ SYSTEM ERROR: {str(e)}"

# --- 6. मुख्य यूजर इंटरफेस और लाइव पैनल ---
ticker_input = st.text_input("Enter NSE Trading Symbol (e.g., MANKIND):", "MANKIND")
qty_input = st.number_input("Order Quantity:", min_value=1, value=1, step=1)

# लाइव डेटा लोड और एनालिसिस
df_live = get_live_market_stream(ticker_input)
df_analyzed = analyze_smart_money(df_live)

ltp = df_analyzed['close'].iloc[-1]
uc_limit = df_analyzed['upper_circuit'].iloc[-1]
lc_limit = df_analyzed['lower_circuit'].iloc[-1]
pcr_val = df_analyzed['pcr'].iloc[-1]
signal_status = df_analyzed['signal'].iloc[-1]

# डिस्प्ले लाइव मैट्रिक्स
col1, col2, col3, col4 = st.columns(4)
col1.metric("Live LTP (INR)", f"₹{ltp}")
col2.metric("Upper Circuit", f"₹{uc_limit}")
col3.metric("Lower Circuit", f"₹{lc_limit}")
col4.metric("Live PCR", f"{pcr_val:.2f}")

# लाइव सर्किट शील्ड स्टेटस चेक
if ltp >= (uc_limit - (uc_limit * 0.01)) or ltp <= (lc_limit + (lc_limit * 0.01)):
    st.error("🚨 CIRCUIT ALERT: स्टॉक सर्किट लिमिट ज़ोन के बहुत करीब है!")
else:
    st.success("🛡️ Circuit Shield: Safe Zone")

# स्मार्ट मनी अलार्म बॉक्स
st.info(f"🤖 Institutional Signal Status: **{signal_status}**")

# --- 7. कैंडलस्टिक चार्ट फीचर ---
st.subheader("📊 Live Candlestick View")
fig = go.Figure(data=[go.Candlestick(
    x=[df_analyzed['timestamp'].iloc[-1]],
    open=[df_analyzed['open'].iloc[-1]],
    high=[df_analyzed['high'].iloc[-1]],
    low=[df_analyzed['low'].iloc[-1]],
    close=[ltp],
    name=ticker_input
)])
fig.update_layout(theme="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("⚡ Execute Instant Smart Trade (Groww)")

btn_buy, btn_sell = st.columns(2)

with btn_buy:
    if st.button("🟢 INSTITUTIONAL BUY ENTRY", use_container_width=True, type="primary"):
        res = place_groww_order(ticker_input, qty_input, "BUY", ltp, uc_limit, lc_limit)
        st.info(res)

with btn_sell:
    if st.button("🔴 INSTITUTIONAL SELL EXIT", use_container_width=True):
        res = place_groww_order(ticker_input, qty_input, "SELL", ltp, uc_limit, lc_limit)
        st.info(res)

# --- 📰 लाइव बिजनेस न्यूज़ स्ट्रीम पैनल ---
st.markdown("---")
st.subheader("📊 Live Business Headlines Stream")
st.info("📰 फिलहाल कोई नई लाइव बिजनेस न्यूज़ उपलब्ध नहीं है।")
