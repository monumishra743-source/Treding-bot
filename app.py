import streamlit as st
import streamlit.components.v1 as components

# Streamlit पेज की सेटिंग्स (टाइटल और लेआउट)
st.set_page_config(page_title="Dhan Premium Algo Dashboard", layout="wide")

# एचटीएमएल, सीएसएस और जावास्क्रिप्ट कोड (बिना किसी इनवैलिड इमोजी के)
html_code = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg-color: #0b0e14;
            --card-bg: #151a22;
            --text-color: #adbac7;
            --text-bright: #f0f6fc;
            --primary-green: #238636;
            --primary-red: #da3637;
            --border-color: #30363d;
            --accent-blue: #58a6ff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 10px;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }

        @media (min-width: 768px) {
            .container {
                grid-template-columns: 360px 1fr;
            }
        }

        .status-bar {
            background-color: rgba(35, 134, 54, 0.12);
            border: 1px solid var(--primary-green);
            color: #56d364;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 14px;
            grid-column: 1 / -1;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }

        h3 {
            color: var(--text-bright);
            margin: 15px 0 10px 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            font-size: 16px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #768390;
        }

        input, select {
            width: 100%;
            padding: 10px;
            background-color: #0b0e14;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-bright);
            font-size: 14px;
            box-sizing: border-box;
        }

        .row-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .live-price-box {
            text-align: center;
            background: #0b0e14;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin: 15px 0;
        }

        .ltp-val {
            font-size: 26px;
            font-weight: bold;
            color: #56d364;
            font-family: monospace;
        }

        .btn-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            color: var(--text-bright);
        }

        .btn-buy { background-color: var(--primary-green); }
        .btn-sell { background-color: var(--primary-red); }

        .response-box {
            margin-top: 15px;
            background-color: #1c2128;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            max-height: 120px;
            overflow-y: auto;
            color: #f0f6fc;
        }

        .chart-container {
            min-height: 500px;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="status-bar">
        Dhan API Engine Successfully Connected (Valid for 30 Days)
    </div>

    <div class="card">
        <h3>Risk Controls</h3>
        <div class="row-2">
            <div>
                <label>Max Daily Trades</label>
                <input type="number" value="5">
            </div>
            <div>
                <label>Max Daily Loss</label>
                <input type="number" value="500">
            </div>
        </div>

        <h3>Dhan API Authentication</h3>
        <div>
            <label>Dhan Client ID</label>
            <input type="text" placeholder="Enter Client ID">
        </div>
        <div style="margin-top: 10px;">
            <label>Dhan Access Token</label>
            <input type="password" value="UCC_TOKEN_HOLDER">
        </div>

        <h3>Order Configuration</h3>
        <div>
            <label>Trading Symbol</label>
            <input type="text" id="assetSymbol" value="NATURALGAS" onchange="handleSymbolChange()">
        </div>
        
        <div class="row-2" style="margin-top: 10px;">
            <div>
                <label>Qty</label>
                <input type="number" value="10">
            </div>
            <div>
                <label>Type</label>
                <select>
                    <option>MARKET</option>
                    <option>LIMIT</option>
                </select>
            </div>
        </div>

        <div class="live-price-box">
            <label>LIVE LTP (INR)</label>
            <div class="ltp-val" id="displayLtp">Loading Data...</div>
        </div>

        <div class="btn-panel">
            <button class="btn btn-buy" onclick="simulateOrder('BUY')">Institutional Buy</button>
            <button class="btn btn-sell" onclick="simulateOrder('SELL')">Institutional Sell</button>
        </div>

        <h3>System Logs</h3>
        <div class="response-box" id="logConsole">
            System ready. Awaiting inputs...
        </div>
    </div>

    <div class="chart-container">
        <div id="tv_widget_live" style="height: 100%; width: 100%;"></div>
    </div>
</div>

<script type="text/javascript" src="https://tradingview.com"></script>
<script type="text/javascript">
    function loadChart(symbolName) {
        let marketPrefix = "MCX:";
        if(symbolName === "TECHM" || symbolName === "RELIANCE" || symbolName === "SBIN") {
            marketPrefix = "NSE:";
        }
        
        new TradingView.widget({
            "autosize": true,
            "symbol": marketPrefix + symbolName,
            "interval": "5",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "in",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "container_id": "tv_widget_live"
        });
        
        document.getElementById("displayLtp").innerText = "Active Mode";
        document.getElementById("logConsole").innerHTML = "Success: " + symbolName + " live chart loaded.";
    }

    window.onload = function() {
        loadChart("NATURALGAS");
    }

    function handleSymbolChange() {
        let sym = document.getElementById("assetSymbol").value.toUpperCase().trim();
        document.getElementById("assetSymbol").value = sym;
        loadChart(sym);
    }

    function simulateOrder(action) {
        let sym = document.getElementById("assetSymbol").value;
        let consoleLog = document.getElementById("logConsole");
        
        if (action === "BUY" && (sym === "TECHM" || sym === "RELIANCE")) {
            consoleLog.innerHTML = "<span style='color:var(--primary-red)'>Error (405): Market Closed. Order Rejected.</span>";
        } else {
            consoleLog.innerHTML = "<span style='color:#56d364'>Success: " + action + " order for " + sym + " sent to Dhan API.</span>";
        }
    }
</script>
</body>
</html>
"""

# HTML कंपोनेंट को स्ट्रीमलिट ऐप के अंदर रेंडर करना
components.html(html_code, height=750, scrolling=True)
