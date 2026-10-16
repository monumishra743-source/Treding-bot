<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Advanced Dhan Algo Terminal</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --text-color: #c9d1d9;
            --text-bright: #ffffff;
            --primary-green: #238636;
            --primary-green-hover: #2ea043;
            --primary-red: #da3637;
            --primary-red-hover: #f85149;
            --border-color: #30363d;
            --accent-blue: #58a6ff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 10px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }

        @media (min-width: 768px) {
            .container {
                grid-template-columns: 350px 1fr;
            }
        }

        /* Status Bar */
        .status-bar {
            background-color: rgba(35, 134, 54, 0.15);
            border: 1px solid var(--primary-green);
            color: #56d364;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 14px;
            grid-column: 1 / -1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        h3 {
            color: var(--text-bright);
            margin-top: 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
            color: #8b949e;
        }

        input, select {
            width: 100%;
            padding: 10px;
            background-color: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-bright);
            font-size: 14px;
            box-sizing: border-box;
            transition: border-color 0.2s;
        }

        input:focus {
            border-color: var(--accent-blue);
            outline: none;
        }

        .row-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        /* Action Buttons */
        .btn-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 20px;
        }

        .btn {
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-bright);
            text-transform: uppercase;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .btn-buy { background-color: var(--primary-green); }
        .btn-buy:hover { background-color: var(--primary-green-hover); }
        .btn-sell { background-color: var(--primary-red); }
        .btn-sell:hover { background-color: var(--primary-red-hover); }

        .btn-kill {
            width: 100%;
            background-color: #21262d;
            border: 1px solid var(--primary-red);
            color: var(--primary-red);
            margin-top: 15px;
        }
        .btn-kill:hover {
            background-color: var(--primary-red);
            color: var(--text-bright);
        }

        /* Live Data View */
        .live-price-box {
            text-align: center;
            background: #0d1117;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin: 15px 0;
        }

        .ltp-val {
            font-size: 28px;
            font-weight: bold;
            color: #56d364;
            font-family: monospace;
            animation: pulse 2s infinite;
        }

        /* Chart Wrapper */
        .chart-container {
            min-height: 450px;
            height: 100%;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.8; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>

<div class="container">
    <!-- Live Connected Header -->
    <div class="status-bar">
        🟢 Dhan API इंजन सफलतापूर्वक कनेक्टेड है (लाइव ट्रेडिंग मोड एक्टिव)
    </div>

    <!-- Left Controls Panel -->
    <div class="card">
        <h3>🛡️ सिस्टम और रिस्क कण्ट्रोल</h3>
        
        <div class="row-2">
            <div class="form-group">
                <label>मैक्स डेली ट्रेड्स</label>
                <input type="number" value="5">
            </div>
            <div class="form-group">
                <label>मैक्स लॉस कैप (INR)</label>
                <input type="number" value="500">
            </div>
        </div>

        <h3>🔑 Dhan API ऑथेंटिकेशन</h3>
        <div class="form-group">
            <label>Dhan Client ID</label>
            <input type="text" placeholder="अपनी Client ID दर्ज करें">
        </div>
        <div class="form-group">
            <label>Dhan Access Token</label>
            <input type="password" placeholder="••••••••••••••••••••">
        </div>

        <h3>⚡ आर्डर कॉन्फ़िगरेशन</h3>
        <div class="form-group">
            <label>ट्रेडिंग सिंबल (जैसे: NATURALGASOCT2026, TECHM)</label>
            <input type="text" id="symInput" value="NATURALGASOCT2026" onchange="updateChart()">
        </div>
        
        <div class="row-2">
            <div class="form-group">
                <label>क्वांटिटी (Qty)</label>
                <input type="number" value="10">
            </div>
            <div class="form-group">
                <label>ऑर्डर टाइप</label>
                <select>
                    <option>MARKET</option>
                    <option>LIMIT</option>
                </select>
            </div>
        </div>

        <div class="live-price-box">
            <label>LIVE LTP (INR)</label>
            <div class="ltp-val" id="liveLtp">₹1,724.26</div>
        </div>

        <div class="btn-panel">
            <button class="btn btn-buy">Institutional Buy</button>
            <button class="btn btn-sell">Institutional Sell</button>
        </div>

        <button class="btn btn-kill">Emergency Kill Switch</button>
    </div>

    <!-- Right Live Chart Panel -->
    <div class="chart-container" id="chartWrapper">
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container" style="height:100%;width:100%">
          <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%"></div>
          <script type="text/javascript" src="https://tradingview.com"></script>
          <script type="text/javascript">
          function loadTradingView(symbol) {
              new TradingView.widget({
              "autosize": true,
              "symbol": "MCX:" + symbol.replace("OCT2026", ""),
              "interval": "5",
              "timezone": "Asia/Kolkata",
              "theme": "dark",
              "style": "1",
              "locale": "in",
              "enable_publishing": false,
              "hide_side_toolbar": false,
              "allow_symbol_change": true,
              "container_id": "tradingview_chart"
            });
          }
          // Initial Load
          window.onload = function() {
              loadTradingView("NATURALGAS");
          }
          function updateChart() {
              var sym = document.getElementById("symInput").value;
              loadTradingView(sym);
          }
          </script>
        </div>
        <!-- TradingView Widget END -->
    </div>
</div>

</body>
</html>
