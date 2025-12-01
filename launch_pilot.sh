#!/bin/bash

echo "=================================================="
echo "   GENESIS CONDUCTOR: WVS-Pilot-B Launch          "
echo "   Mode: Headless / OAuth2 Token                  "
echo "=================================================="

# 0. Pre-Flight Check
if [ ! -f "token.json" ]; then
    echo "❌ ERROR: 'token.json' not found!"
    echo "   STOPPING DEPLOYMENT."
    echo "   Instruction: Run 'auth_gen.py' locally and upload the token file."
    exit 1
fi

# 1. Dependencies
echo "[1/3] Verifying Python Environment..."
pip install fastapi uvicorn requests google-cloud-bigquery google-auth-oauthlib python-dotenv > /dev/null

# 2. Services
echo "[2/3] Starting Services..."

# Sentiment Oracle
nohup python3 sentiment_service.py > sentiment.log 2>&1 &
PID_SENTIMENT=$!
echo "      -> Oracle Active (PID: $PID_SENTIMENT)"

# Dashboard Engine
nohup python3 pilot_dashboard.py > dashboard.log 2>&1 &
PID_DASHBOARD=$!
echo "      -> Dashboard Active (PID: $PID_DASHBOARD)"

# 3. UI Serving
echo "[3/3] Binding HTTP Port 8080..."
nohup python3 -m http.server 8080 > http.log 2>&1 &

echo "--------------------------------------------------"
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "👉 Dashboard: http://<SERVER_IP>:8080/index.html"
echo "--------------------------------------------------"
