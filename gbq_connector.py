import os
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.cloud import bigquery

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/bigquery.readonly']

@dataclass
class TelemetryData:
    total_pnl: float
    max_drawdown: float
    last_trade_time: datetime

class GBQInterface:
    def __init__(self, pilot_id: str):
        self.pilot_id = pilot_id
        self.project_id = os.getenv("GCP_PROJECT_ID", "genesis-conductor-main")
        self.client = self._authenticate_headless()

    def _authenticate_headless(self):
        """
        HEADLESS AUTHENTICATION LOGIC
        Strictly relies on 'token.json' presence. No browser fallbacks.
        """
        token_path = 'token.json'

        # 1. Validation
        if not os.path.exists(token_path):
            print(f"[CRITICAL] Auth File Missing: {token_path}")
            print("   -> Upload 'token.json' from local Ops machine.")
            return None

        try:
            # 2. Load & Refresh
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            if creds and creds.expired and creds.refresh_token:
                print("[AUTH] Token expired. Refreshing session...")
                creds.refresh(Request())

                # Persist the fresh token
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print("[AUTH] Session refreshed and saved.")

            return bigquery.Client(credentials=creds, project=self.project_id)

        except Exception as e:
            print(f"[CRITICAL] Auth Error: {e}")
            return None

    def get_metrics(self) -> TelemetryData:
        """ Fetches live metrics or returns safe fallback """
        if not self.client:
            return self._simulation_fallback()

        try:
            query = """
                SELECT
                    SUM(realized_pnl) as total_pnl,
                    MIN(equity_curve_pct) as max_drawdown,
                    MAX(timestamp) as last_trade
                FROM `genesis_conductor.strategy_logs.wvs_pilot_b`
                WHERE pilot_id = @pilot_id
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("pilot_id", "STRING", self.pilot_id)
                ]
            )

            results = list(self.client.query(query, job_config=job_config).result())

            if results and results[0].total_pnl is not None:
                return TelemetryData(
                    total_pnl=results[0].total_pnl,
                    max_drawdown=results[0].max_drawdown,
                    last_trade_time=results[0].last_trade
                )
            return TelemetryData(0.0, 0.0, datetime.utcnow())

        except Exception as e:
            print(f"[ERROR] BigQuery Query Failed: {e}")
            return self._simulation_fallback()

    def _simulation_fallback(self):
        return TelemetryData(0.00, -1.2, datetime.utcnow())
