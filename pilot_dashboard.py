import time
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from gbq_connector import GBQInterface

# 1. Load Environment Configuration
load_dotenv()

# 2. Fetch Config from .env (with defaults for safety)
PILOT_ID = os.getenv("PILOT_ID", "WVS-Pilot-B-v1.0")
REFRESH_RATE = int(os.getenv("REFRESH_RATE", 60))
SENTIMENT_URL = os.getenv("SENTIMENT_URL", "http://127.0.0.1:8000/heartbeat")
BUDGET_USD = 150.00  # Fixed per authorized budget

class DashboardEngine:
    def __init__(self):
        # Initialize the BigQuery Connector
        # (It will self-authenticate using GCP_PRIVATE_KEY from .env)
        self.gbq = GBQInterface(PILOT_ID)

    def check_sentiment_health(self):
        """ Pings the microservice to verify the Fail-Closed sensor is active """
        try:
            r = requests.get(SENTIMENT_URL, timeout=0.5)
            return r.status_code == 200
        except:
            return False

    def determine_status(self, sentiment_ok):
        """
        Core State Machine Logic
        Determines the operational color code for the Dashboard.
        """
        now = datetime.utcnow()
        is_weekend = now.weekday() >= 5

        if not sentiment_ok:
            return "HALTED (SENSOR FAILURE)", "#c0392b" # Red
        elif not is_weekend:
            return "SLEEP (WAITING FOR WEEKEND)", "#f39c12" # Orange
        else:
            return "ACTIVE (TRADING)", "#27ae60" # Green

    def generate_html(self):
        # 1. Fetch Real-Time Data
        metrics = self.gbq.get_metrics()
        sentiment_ok = self.check_sentiment_health()
        status_text, status_color = self.determine_status(sentiment_ok)

        # 2. Build HTML Dashboard
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="{REFRESH_RATE}">
            <title>Pilot {PILOT_ID}</title>
            <style>
                body {{ background: #121212; color: #e0e0e0; font-family: 'Courier New', monospace; padding: 20px; }}
                .card {{ border: 1px solid #333; padding: 20px; margin-bottom: 20px; border-radius: 4px; background: #1e1e1e; }}
                .stat {{ font-size: 2em; font-weight: bold; }}
                .badge {{ padding: 5px 10px; background: {status_color}; color: #000; font-weight: bold; border-radius: 3px; }}
                .meta {{ color: #666; font-size: 0.8em; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>WVS Pilot Control Board</h1>
                <p>Status: <span class="badge">{status_text}</span></p>
                <p>Sentiment Link: {"🟢 ONLINE" if sentiment_ok else "🔴 OFFLINE"}</p>
            </div>
            <div class="card">
                <h3>Financial Telemetry</h3>
                <div style="display:flex; gap:40px;">
                    <div>
                        <small>PNL (USD)</small><br>
                        <span class="stat" style="color: {'#27ae60' if metrics.total_pnl >= 0 else '#c0392b'}">${metrics.total_pnl:.2f}</span>
                    </div>
                    <div>
                        <small>Drawdown</small><br>
                        <span class="stat" style="color: {'#e0e0e0' if metrics.max_drawdown > -15 else '#c0392b'}">{metrics.max_drawdown:.2f}%</span>
                    </div>
                    <div>
                        <small>Budget</small><br>
                        <span class="stat">${BUDGET_USD}</span>
                    </div>
                </div>
            </div>
            <div class="meta">
                Last Sync: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} <br>
                Pilot ID: {PILOT_ID} <br>
                Environment: .env Configured
            </div>
        </body>
        </html>
        """

        # Write the static file for the HTTP server to pick up
        with open("index.html", "w") as f:
            f.write(html)
        print(f"[{datetime.utcnow()}] Dashboard updated. Status: {status_text}")

if __name__ == "__main__":
    engine = DashboardEngine()
    print(f"🚀 Dashboard Engine Started for {PILOT_ID}...")
    print(f"   -> Refresh Rate: {REFRESH_RATE}s")
    print(f"   -> Sentiment Node: {SENTIMENT_URL}")

    while True:
        engine.generate_html()
        time.sleep(REFRESH_RATE)
