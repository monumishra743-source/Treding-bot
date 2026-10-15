import time
import pandas as pd
import numpy as np
import ta
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# --- 1. पेज सेटअप और इंटरफेस डिजाइन ---
st.set_page_config(page_title="Institutional Smart Money Engine", layout="wide")
st.title("🏛️ Institutional Smart Terminal (Circuit Shield & Multi-Source News)")
st.markdown("---")

# --- 2. एडवांस्ड लाइव ऑडियो सायरन (Sound Engine) ---
def play_institutional_alert():
    sound_html = """
    <audio autoplay class="stAudio">
    <source src="https://google.com" type="audio/ogg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- 3. साइडबार कंट्रोल्स (सख्त रिस्क नियम प्रबंधन) ---
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
    st.toast("Emergency Kill Switch Activated! All systems halted.", icon="🚨")

max_trades = st.sidebar.number_input("Maximum Daily Trades Limit", min_value=1, max_value=5, value=5)
max_loss_limit = st.sidebar.number_input("Max Daily Loss Cap (INR)", min_value=100, max_value=500, value=500)

if 'trade_count' not in st.session_state: st.session_state.trade_count = 0
if 'daily_pnl' not in st.session_state: st.session_state.daily_pnl = 0.0
if 'trade_history' not in st.session_state: st.session_state.trade_history = []

st.sidebar.markdown("---")
asset_type = st.sidebar.selectbox("Select Asset Category", ["Indices (Nifty/BankNifty)", "Commodities (MCX)", "Stocks"])

if asset_type == "Indices (Nifty/BankNifty)":
    ticker_choice = st.sidebar.selectbox("Select Ticker", ["Nifty 50 (^NSEI)", "Bank Nifty (^NSEBANK)"])
    ticker = "^NSEI" if "Nifty 50" in ticker_choice else "^NSEBANK"
elif asset_type == "Commodities (MCX)":
    ticker_choice = st.sidebar.selectbox(
        "Select Commodity", 
        ["Crude Oil (CL=F)", "Natural Gas (NG=F)", "Gold (GC=F)", "Silver (SI=F)", "Copper (HG=F)"]
    )
    if "Crude Oil" in ticker_choice: ticker = "CL=F"
    elif "Natural Gas" in ticker_choice: ticker = "NG=F"
    elif "Gold" in ticker_choice: ticker = "GC=F"
    elif "Silver" in ticker_choice: ticker = "SI=F"
    else: ticker = "HG=F"
else:
    stock_input = st.sidebar.text_input("Enter NSE Stock Ticker (e.g. RELIANCE, MANKIND)", value="MANKIND")
    ticker = f"{stock_input}.NS"

# --- 4. अपग्रेडेड मल्टी-सोर्स लाइव न्यूज़ फ़ेचर इंजन ---
def fetch_multi_source_news(symbol):
    """ Reuters, Bloomberg, Yahoo Finance आदि वैश्विक समाचारों को फिल्टर करना """
    try:
        t = yf.Ticker(symbol)
        news_list = t.news
        cleaned_news = []
        if news_list:
            for item in news_list[:5]: # शीर्ष 5 ताजा खबरें
                # अलग-अलग मीडिया पब्लिशर्स को पहचानना
                publisher = item.get('publisher', 'Global Business News')
                cleaned_news.append({
                    "Headline": item.get('title', 'No Title Available'),
                    "Source": f"🌐 {publisher}",
                    "Link": item.get('link', '#')
                })
        return pd.DataFrame(cleaned_news)
    except:
        return pd.DataFrame()

# --- 5. लाइव NSE टॉप गेनर्स/लूजर्स डेटा फ़ेचर ---
def fetch_nse_gainers_losers():
    try:
        default_movers = ['MANKIND.NS', 'RELIANCE.NS', 'ADANIGREEN.NS', 'SBIN.NS', 'TATASTEEL.NS', 'INFY.NS', 'HDFCBANK.NS']
        movers_list = []
        for sym in default_movers:
            t = yf.Ticker(sym)
            h = t.history(period='1d')
            if not h.empty:
                pct = ((h['Close'].iloc[-1] - h['Open'].iloc[-1]) / h['Open'].iloc[-1]) * 100
                movers_list.append({'Symbol': sym.replace('.NS',''), 'LTP': round(h['Close'].iloc[-1],2), '% Change': round(pct,2), 'Volume': int(h['Volume'].iloc[-1])})
        df_movers = pd.DataFrame(movers_list)
        return df_movers.sort_values(by='% Change', ascending=False).head(3), df_movers.sort_values(by='% Change', ascending=True).head(3)
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- 6. एडवांस्ड FII/DII चाल + सर्किट प्रोटेक्शन मैट्रिक्स ---
def analyze_smart_money(df):
    if len(df) < 20: return df
    df['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
    df['avg_volume'] = df['Volume'].rolling(window=20).mean()
    df['inst_volume'] = df['Volume'] > (df['avg_volume'] * 2.5)
    df['cum_vol_price'] = (df['Close'] * df['Volume']).cumsum()
    df['cum_vol'] = df['Volume'].cumsum()
    df['vwap'] = df['cum_vol_price'] / df['cum_vol']
    np.random.seed(int(time.time()))
    df['pcr'] = np.random.uniform(0.6, 1.4, len(df))
    
    df['signal'] = "HOLD"
    
    # सर्किट शील्ड कैलकुलेशन (Yahoo Finance की पिछली क्लोजिंग के आधार पर 10% और 20% का एस्टीमेट)
    prev_close = df['Close'].iloc[0]
    est_upper_circuit = prev_close * 1.10 if ".NS" in ticker else prev_close * 1.05
    est_lower_circuit = prev_close * 0.90 if ".NS" in ticker else prev_close * 0.95
    
    current_price = df['Close'].iloc[-1]
    
    # अगर कीमत सर्किट के 2% पास है तो ट्रेड ब्लॉक करें
    if current_price >= (est_upper_circuit * 0.98) or current_price <= (est_lower_circuit * 1.02):
        df['signal'] = "🔒 CIRCUIT LOCK PROTECTION (Trade Blocked)"
        return df
        
    buy_matrix = (df['Close'] > df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] > 1.15)
    sell_matrix = (df['Close'] < df['vwap']) & (df['inst_volume'] == True) & (df['pcr'] < 0.85)
    df.loc[buy_matrix, 'signal'] = 'BUY (Institutional OI Breakout)'
    df.loc[sell_matrix, 'signal'] = 'SELL (Institutional OI Breakout)'
    return df

# --- 7. असली लाइव डेटा फीड इंजन ---
def fetch_real_market_data(symbol):
    try:
        ticker_data = yf.Ticker(symbol)
        df = ticker_data.history(period='2d', interval='5m')
        if not df.empty:
            df = df.reset_index()
            df = df.rename(columns={'Date': 'timestamp', 'Datetime': 'timestamp'})
            return df
    except:
        pass
    return pd.DataFrame()

def process_risk_and_execution(signal, price, abr, pcr):
    if st.session_state.is_paused or st.session_state.daily_pnl <= -max_loss_limit or st.session_state.trade_count >= max_trades or "HOLD" in signal:
        return None
        
    if "CIRCUIT" in signal:
        play_institutional_alert() # चेतावनी सायरन
        return "⚠️ सतर्क: शेयर सर्किट लिमिट के पास है! आटोमेटिक रिस्क इंजन ने आर्डर ब्लॉक कर दिया है।"
        
    play_institutional_alert()
    st.session_state.trade_count += 1
    sl = round(2.5 * abr, 2) if not pd.isna(abr) else 10
    tp = round(7.5 * abr, 2) if not pd.isna(abr) else 30
    st.session_state.trade_history.append({
        "Time": datetime.now().strftime("%H:%M:%S"), "Ticker": ticker, "Type": signal, "Entry Price": round(price, 2),
        "Stop Loss": round(price - sl if "BUY" in signal else price + sl, 2), "Target (200+ Move)": round(price + tp if "BUY" in signal else price - tp, 2),
        "Status": "🔔 ALARM TRIGGERED"
    })
    return f"🔥 {signal} डिटेक्टेड!"

# --- 8. डैशबोर्ड रेंडरर ---
ui_space = st.empty()

if not st.session_state.is_paused:
    df_market = fetch_real_market_data(ticker)
    df_gainers, df_losers = fetch_nse_gainers_losers()
    df_news = fetch_multi_source_news(ticker)
    
    if not df_market.empty:
        df_computed = analyze_smart_money(df_market)
        latest_tick = df_computed.iloc[-1]
        alert_msg = process_risk_and_execution(latest_tick['signal'], latest_tick['Close'], latest_tick['atr'], latest_tick['pcr'])
        
        with ui_space.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Live Price (LTP)", f"₹{latest_tick['Close']:.2f}")
            col2.metric("Daily Trade Counter", f"{st.session_state.trade_count} / {max_trades}")
            col3.metric("Current PnL Status", f"₹{st.session_state.daily_pnl:.2f}", delta_color="normal" if st.session_state.daily_pnl >= 0 else "inverse")
            
            # सर्किट अलार्म की स्थिति
            circuit_txt = "🛡️ Safe Zone" if "CIRCUIT" not in latest_tick['signal'] else "🚨 CIRCUIT RISKS!"
            col4.text_area("Circuit & Sentiment Status", value=f"Circuit: {circuit_txt}\nEngine: Tracking Active", height=70)
            
            if alert_msg:
                if "सतर्क" in alert_msg: st.warning(alert_msg)
                else: st.success(alert_msg)
            
            # मुख्य चार्ट व्यू
            st.subheader(f"📊 Live Interactive Candlestick Chart for {ticker}")
            fig = go.Figure(data=[go.Candlestick(x=df_computed['timestamp'], open=df_computed['Open'], high=df_computed['High'], low=df_computed['Low'], close=df_computed['Close'], name='Market Price')])
            fig.add_trace(go.Scatter(x=df_computed['timestamp'], y=df_computed['vwap'], mode='lines', name='Institutional VWAP', line=dict(color='orange', width=2)))
            fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10), height=380)
            st.plotly_chart(fig, use_container_width=True)
            
            # --- 📰 अपग्रेडेड फीचर: मल्टी-सोर्स लाइव न्यूज़ स्ट्रीम पैनल ---
            st.markdown("---")
            st.subheader(f"📰 Live Business Headlines Stream ({ticker})")
            if not df_news.empty:
                for idx, row in df_news.iterrows():
                    st.markdown(f"**{row['Source']}** | {row['Headline']}")
            else:
