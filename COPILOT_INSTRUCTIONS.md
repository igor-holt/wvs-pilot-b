# Copilot / AI Assistant Instructions

**Context:**
You are working on a high-stakes financial trading pilot (WVS-Pilot-B). The code controls real capital. Safety, reliability, and security are the highest priorities.

## 🚨 Critical Rules (DO NOT BREAK)

1.  **Fail-Closed Architecture**:
    *   Never remove or bypass the `check_sentiment_health()` calls.
    *   If a service is unreachable, the system MUST default to a `HALTED` or `SAFE` state.
    *   Do not suggest "retry loops" that ignore repeated failures; fail fast.

2.  **Headless Environment**:
    *   This code runs on a headless VPS (Docker/Cloud Run).
    *   **NEVER** suggest code that requires `webbrowser.open()` or interactive login flows in `gbq_connector.py` or `pilot_dashboard.py`.
    *   All authentication must rely on `token.json` or environment variables.

3.  **Data Integrity**:
    *   The `TelemetryData` dataclass is the source of truth. Do not modify its structure without updating the BigQuery schema.
    *   Always handle `None` values from BigQuery (e.g., when a new pilot ID has no trades yet).

4.  **Security**:
    *   **NEVER** hardcode credentials (API keys, private keys, passwords) in the code.
    *   Always use `os.getenv()` or the `dotenv` library.
    *   Do not log raw sensitive data (e.g., `print(credentials)`).

## 🏗️ Codebase Structure

*   **`sentiment_service.py`**: The "Safety Valve". It simulates an external risk signal. It has a `SIMULATE_OUTAGE` flag for testing.
*   **`gbq_connector.py`**: Handles BigQuery connections. It has a `_simulation_fallback()` method that MUST be used if the connection fails, to prevent crashing.
*   **`pilot_dashboard.py`**: The main loop. It generates static HTML. It does NOT use a complex frontend framework (React/Vue) to keep dependencies minimal.

## 🧪 Testing Guidelines
*   When writing tests, mock the `GBQInterface` to avoid making real billing calls to BigQuery.
*   Test the "Fail-Closed" logic by simulating a 503 error from the Sentiment Service.
