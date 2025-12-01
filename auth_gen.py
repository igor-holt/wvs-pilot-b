import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# --- CONFIGURATION ---
# Ensure 'client_secret.json' from GCP Console is in this directory.
SCOPES = ['https://www.googleapis.com/auth/bigquery.readonly']

def generate_token():
    if not os.path.exists('client_secret.json'):
        print("❌ CRITICAL: 'client_secret.json' missing.")
        print("   Action: Download OAuth Client ID JSON from GCP Console.")
        sys.exit(1)

    print("==========================================")
    print("🔐 WVS Pilot: Credential Generator")
    print("==========================================")
    print("1. A browser window will open.")
    print("2. Login with the authorized Google Account.")
    print("3. Grant access to BigQuery.")
    print("------------------------------------------")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)

        # Launches local server for callback
        creds = flow.run_local_server(port=0)

        # Serializes the refresh token to disk
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        print("\n✅ SUCCESS: 'token.json' generated.")
        print("🚀 NEXT STEP: Upload 'token.json' to the production server root.")

    except Exception as e:
        print(f"\n❌ FAILURE: {e}")

if __name__ == "__main__":
    generate_token()
