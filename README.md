# WVS-Pilot-B (Weekend Volatility Seasonality - Variant B)

**Project Status:** `PILOT` | **Regime:** `FEAR` | **Auth:** `Headless/OAuth2`

## 📡 Overview
WVS-Pilot-B is an automated trading pilot designed to exploit volatility seasonality anomalies during weekend market closures. This repository contains the **Variant B** implementation, which features a decoupled microservice architecture and a "Fail-Closed" safety mechanism.

### System Architecture
1.  **Sentiment Oracle (`sentiment_service.py`)**: A FastAPI microservice that acts as the safety valve. If this service is unreachable or reports extreme fear, the system halts.
2.  **Telemetry Connector (`gbq_connector.py`)**: Interfaces with Google BigQuery to fetch real-time PnL and Drawdown metrics. Optimized for headless environments using `token.json`.
3.  **Dashboard Engine (`pilot_dashboard.py`)**: Orchestrates the system state, polls telemetry, and generates the static HTML dashboard.
4.  **Launch Script (`launch_pilot.sh`)**: One-click deployment script for Ops.

---

## 🛠️ Setup & Installation

### Prerequisites
*   Python 3.9+
*   Google Cloud Project with BigQuery API enabled.
*   `client_secret.json` (OAuth 2.0 Client ID for Desktop Apps).

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
# General
PILOT_ID=WVS-Pilot-B-v1.0
MARKET_REGIME=FEAR
SIMULATE_OUTAGE=False
REFRESH_RATE=60

# GCP Config (Project ID is required, others are optional if using token.json)
GCP_PROJECT_ID=your-project-id
```

### 2. Authentication (Headless)
This project uses a "Token Upload" pattern to avoid storing long-lived private keys on the server.

1.  **Local Machine**: Place `client_secret.json` in the root.
2.  **Local Machine**: Run the generator to create credentials:
    ```bash
    python3 auth_gen.py
    ```
3.  **Server**: Upload the generated `token.json` to the server root.

### 3. Installation
```bash
chmod +x launch_pilot.sh
./launch_pilot.sh
```
This script will:
*   Create/Activate a virtual environment (if configured).
*   Install dependencies (`fastapi`, `google-cloud-bigquery`, etc.).
*   Start all services in the background.
*   Serve the dashboard on Port 8080.

---

## 🖥️ Usage

**Access Dashboard:**
Open `http://localhost:8080/index.html` (or your server IP).

**Stop System:**
```bash
pkill -f python3
```

---

## 🛡️ Safety Mechanisms
*   **Fail-Closed**: If the Sentiment Oracle is unreachable (503/Timeout), the Dashboard state immediately switches to `HALTED`.
*   **Regime Gating**: Trading is only active if `MARKET_REGIME` allows (currently set to `FEAR` which restricts leverage).
*   **Headless Auth**: No browser is required on the production server; tokens are auto-refreshed.
