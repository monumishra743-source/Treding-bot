import streamlit as st
import streamlit.components.v1 as components
import json

# 🔴 अपनी बनाई हुई लाइब्रेरी फ़ाइल से आर्डर फ़ंक्शन को इम्पोर्ट करना
from dhan_helper import place_dhan_order

# Streamlit पेज सेटिंग्स
st.set_page_config(page_title="Dhan Live Algo Terminal", layout="wide")
st.title("⚡ Dhan Live Algo Engine Control")

MY_DHAN_ID = "11118"

# फ्रंटएंड से जावास्क्रिप्ट डेटा रिसीव करना
ctx = components.declare_component("dhan_order_bridge", value=None)
order_data_raw = ctx()

if order_data_raw:
    try:
        order_info = json.loads(order_data_raw)
        action = order_info.get("action")
        symbol = order_info.get("symbol")
        quantity = order_info.get("quantity", 10)
        user_token = order_info.get("token")
        
        # 🚀 लाइब्रेरी फ़ंक्शन को कॉल करना (Real Trade Execution)
        response = place_dhan_order(
            client_id=MY_DHAN_ID,
            access_token=user_token,
            action=action,
            symbol=symbol,
            quantity=quantity
        )
        
        # स्क्रीन पर रिस्पांस दिखाना
        if response["status"] == "success":
            st.success(f"Dhan Server Success: {response['data']}")
        else:
            st.error(f"Dhan Server Error: {response['message']}")
            
    except Exception as e:
        st.error(f"Bridge Error: {str(e)}")

# फ्रंटएंड इंटरफ़ेस कोड (HTML/CSS)
html_code = f"""
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{
            --bg-color: #0b0e14;
            --card-bg: #151a22;
            --text-color: #adbac7;
            --text-bright: #f0f6fc;
            --primary-green: #238636;
            --primary-red: #da3637;
            --border-color: #30363d;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 10px;
        }}
        .container {{
            max-width: 100%;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }}
        @media (min-width: 768px) {{
            .container {{ grid-template-columns: 360px 1fr; }}
        }}
        .status-bar {{
            background-color: rgba(35, 134, 54, 0.12);
            border: 1px solid var(--primary-green);
            color: #56d364;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
        }}
        label {{ display: block; margin-bottom: 5px; font-size: 12px; color: #768390; }}
        input, select {{
            width: 100%; padding: 10px; background-color: #0b0e14;
            border: 1px solid var(--border-color); border-radius: 6px;
            color: var(--text-bright); font-size: 14px; box-sizing: border-box;
        }}
        .row-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .btn-panel {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
        .btn {{ width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; color: var(--text-bright); }}
        .btn-buy {{ background-color: var(--primary-green); }}
        .btn-sell {{ background-color: var(--primary-red); }}
        .response-box {{ margin-top: 15px; background-color: #1c2128; border: 1px solid var(--border-color); border-radius: 6px; padding: 10px; font-size: 12px; height: 80px; overflow-y: auto; color: #f0f6fc; }}
        .chart-container {{ min-height: 500px; background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }}
    </style>
</head>
<body>
<div class="container">
    <div class="status-bar" style="grid-column: 1 / -1;">
        🟢 MULTI-FILE ARCHITECTURE: लाइब्रेरी लोड हो चुकी है
    </div>
    <div class="card">
        <h3>🔑 लाइव ऑथेंटिकेशन</h3>
        <div>
            <label>Dhan Client ID</label>
            <input type="text" value="{MY_DHAN_ID}" readonly style="background-color: #21262d; color: #8b949e;">
        </div>
        <div style="margin-top: 10px;">
            <label>Dhan Access Token</label>
            <input type="password" id="dhanTokenInput" placeholder="यहाँ लाइव टोकन पेस्ट करें">
        </div>
        <h3>⚡ आर्डर कॉन्फ़िगरेशन</h3>
        <div>
            <label>ट्रेडिंग सिंबल</label>
            <input type="text" id="assetSymbol" value="NATURALGAS" onchange="handleSymbolChange()">
        </div>
        <div class="row-2" style="margin-top: 10px;">
            <div>
                <label>क्वांटिटी (Qty)</label>
                <input type="number" id="orderQty" value="10">
            </div>
            <div>
                <label>टाइप</label>
                <select><option>MARKET</option></select>
            </div>
        </div>
        <div class="btn-panel">
            <button class="btn btn-buy" onclick="executeRealOrder('BUY')">Institutional Buy</button>
            <button class="btn btn-sell" onclick="executeRealOrder('SELL')">Institutional Sell</button>
        </div>
        <h3>📋 सिस्टम लॉग्स</h3>
        <div class="response-box" id="logConsole">लाइब्रेरी फ़ाइल कनेक्टेड। आर्डर के लिए तैयार।</div>
    </div>
    <div class="chart-container"><div id="tv_widget_live" style="height: 100%; width: 100%;"></div></div>
</div>
<script type="text/javascript" src="https://tradingview.com"></script>
<script type="text/javascript">
    window.onload = function() {{
        let savedToken = localStorage.getItem('dhan_live_token');
        if(savedToken) {{ document.getElementById('dhanTokenInput').value = savedToken; }}
        loadChart("NATURALGAS");
    }}
    function loadChart(symbolName) {{
        let marketPrefix = "MCX:";
        if(symbolName === "TECHM" || symbolName === "RELIANCE") {{ marketPrefix = "NSE:"; }}
        new TradingView.widget({{"autosize": true, "symbol": marketPrefix + symbolName, "interval": "5", "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "in", "container_id": "tv_widget_live"}});
    }}
    function handleSymbolChange() {{
        let sym = document.getElementById("assetSymbol").value.toUpperCase().trim();
        document.getElementById("assetSymbol").value = sym;
        loadChart(sym);
    }}
    function executeRealOrder(action) {{
        let sym = document.getElementById("assetSymbol").value;
        let qty = document.getElementById("orderQty").value;
        let token = document.getElementById("dhanTokenInput").value;
        if(!token) {{ alert("टोकन दर्ज करें!"); return; }}
        localStorage.setItem('dhan_live_token', token);
        let orderDetails = {{ "action": action, "symbol": sym, "quantity": qty, "token": token }};
        document.getElementById("logConsole").innerHTML = "आर्डर जा रहा है...";
        if (window.parent && window.parent.postMessage) {{
            window.parent.postMessage({ type: 'streamlit:setComponentValue', value: JSON.stringify(orderDetails) }, '*');
        }}
    }}
</script>
</body>
</html>
"""
components.html(html_code, height=750, scrolling=True)
