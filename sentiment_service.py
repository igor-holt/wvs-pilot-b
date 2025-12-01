import uvicorn
from fastapi import FastAPI, HTTPException
from datetime import datetime
import random
import os

# --- CONFIGURATION ---
app = FastAPI(title="WVS Pilot Sentiment Oracle")

# Environment Variables for Dynamic Control
MARKET_REGIME = os.getenv("MARKET_REGIME", "FEAR") # Options: NEUTRAL, GREED, FEAR
SIMULATE_OUTAGE = os.getenv("SIMULATE_OUTAGE", "False").lower() == "true"

@app.get("/heartbeat")
async def heartbeat():
    """
    Critical Safety Check.
    Dashboard/Pilot polls this. Timeout/503 = IMMEDIATE HALT.
    """
    if SIMULATE_OUTAGE:
        # Simulate latency/timeout for Fail-Closed testing
        raise HTTPException(status_code=503, detail="Service Unavailable: Timeout")

    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "module": "Sentiment_Analyst_Core"
    }

@app.get("/scores")
async def get_scores():
    """
    Returns logic-gating metrics.
    """
    if SIMULATE_OUTAGE:
        raise HTTPException(status_code=503, detail="Data Feed Down")

    # Logic to simulate realistic score fluctuation
    base_score = -0.6 if MARKET_REGIME == "FEAR" else 0.2
    jitter = random.uniform(-0.1, 0.1)

    return {
        "global_score": round(base_score + jitter, 2),
        "regime": MARKET_REGIME,
        "confidence": 0.95,
        "source_timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
