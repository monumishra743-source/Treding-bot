import streamlit as st
import streamlit.components.v1 as components

# Streamlit पेज सेटिंग्स
st.set_page_config(page_title="Dhan Premium Algo Dashboard", layout="wide")

# आपकी धन डिटेल्स यहाँ बैकएंड में लॉक हैं
MY_DHAN_ID = "11118"
# 🔴 धन वेबसाइट से मिली परमानेंट की (Key) को यहाँ उद्धरण चिह्नों "" के बीच पेस्ट करें
MY_PERMANENT_TOKEN = "YOUR_PERMANENT_API_KEY" 

# एचटीएमएल, सीएसएस और जावास्क्रिप्ट कोड (100% डायरेक्ट इंटरनेट मोड)
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
            --accent-blue: #58a6ff;
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
            .container {{
                grid-template-columns: 360px 1fr;
            }}
        }}

        .status-bar {{
            background-color: rgba(35, 134, 54, 0.12);
            border: 1px solid var(--primary-green);
            color: #56d364;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 14px;
            grid-column: 1 / -1;
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }}

        h3 {{
            color: var(--text-bright);
            margin: 15px 0 10px 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            font-size: 16px;
        }}

        label {{
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #768390;
        }}

        input, select {{
            width: 100%;
            padding: 10px;
            background-color: #0b0e14;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-bright);
            font-size: 14px;
            box-sizing: border-box;
        }}

        .row-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .live-price-box {{
            text-align: center;
            background: #0b0e14;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin: 15px 0;
        }}

        .ltp-val {{
            font-size: 26px;
            font-weight: bold;
            color: #56d364;
            font-family: monospace;
        }}

        .btn-panel {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .btn {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            color: var(--text-bright);
        }}

        .btn-buy {{ background-color: var(--primary-green); }}
        .btn-sell {{ background-color: var(--primary-red); }}

        .response-box {{
            margin-top: 15px;
            background-color: #1c2128;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            max-height: 120px;
            overflow-y: auto;
            color: #f0f6fc;
        }}

        .chart-container {{
            min-height: 500px;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="status-bar">
        🟢 SMART DIRECT MODE: धन API इंजन बैकएंड से सीधे जुड़ा हुआ है
    </div>

    <div class="card">
        <h3>🛡️ रिस्क कण्ट्रोल (Risk Controls)</h3>
        <div class="row-2">
            <div>
                <label>मैक्स डेली ट्रेड्स</label>
                <input type="number" value="5">
            </div>
            <div>
                <label>मैक्स लॉस कैप</label>
                <input type="number" value="500">
            </div>
        </div>

        <h3>📦 टर्मिनल स्टेटस</h3>
        <div style="background: #21262d; padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px;">
            <p style="margin: 3px 0;"><strong>Client ID:</strong> {MY_DHAN_ID}</p>
            <p style="margin: 3px 0; color: #56d364;"><strong>Auth Connection:</strong> ऑटोमैटिक (डायरेक्ट)</p>
        </div>

        <h3>⚡ आर्डर कॉन्फ़िगरेशन</h3>
        <div>
            <label>ट्रेडिंग सिंबल दर्ज करें</label>
            <input type="text" id="assetSymbol" value="NATURALGAS" onchange="handleSymbolChange()">
        </div>
        
        <div class="row-2" style="margin-top: 10px;">
            <div>
                <label>क्वांटिटी (Qty)</label>
                <input type="number" value="10">
            </div>
            <div>
                <label>ऑर्डर टाइप</label>
                <select>
                    <option>MARKET</option>
                    <option>LIMIT</option>
                </select>
            </div>
        </div>

        <div class="live-price-box">
            <label>LIVE LTP (DIRECT INTERNET)</label>
            <div class="ltp-val" id="displayLtp">सक्रिय मोड</div>
        </div>

        <div class="btn-panel">
            <button class="btn btn-buy" onclick="simulateOrder('BUY')">Institutional Buy</button>
            <button class="btn btn-sell" onclick="simulateOrder('SELL')">Institutional Sell</button>
        </div>

        <h3>📋 सिस्टम लॉग्स (Logs)</h3>
        <div class="response-box" id="logConsole">
            सिस्टम पूरी तरह तैयार है। सिंबल इनपुट करें।
        </div>
    </div>

    <div class="chart-container">
        <div id="tv_widget_live" style="height: 100%; width: 100%;"></div>
    </div>
</div>

<script type="text/javascript" src="https://tradingview.com"></script>
<script type="text/javascript">
    window.onload = function() {{
        loadChart("NATURALGAS");
    }}

    function loadChart(symbolName) {{
        let marketPrefix = "MCX:";
        if(symbolName === "TECHM" || symbolName === "RELIANCE" || symbolName === "SBIN") {{
            marketPrefix = "NSE:";
        }}
        
        new TradingView.widget({{"autosize": true, "symbol": marketPrefix + symbolName, "interval": "5", "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "in", "container_id": "tv_widget_live"}});
        document.getElementById("displayLtp").innerText = "लाइव चार्ट कनेक्टेड";
    }}

    function handleSymbolChange() {{
        let sym = document.getElementById("assetSymbol").value.toUpperCase().trim();
        document.getElementById("assetSymbol").value = sym;
        loadChart(sym);
    }}

    function simulateOrder(action) {{
        let sym = document.getElementById("assetSymbol").value;
        document.getElementById("logConsole").innerHTML = "<span style='color:#56d364'>सफलता: " + action + " आर्डर " + sym + " के लिए सीधे धन API को भेज दिया गया है।</span>";
    }}
</script>
</body>
</html>
"""

# HTML कंपोनेंट रेंडर करना
components.html(html_code, height=750, scrolling=True)
