from getpass import getpass

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/adwords"]

client_id = input("Paste GOOGLE_ADS_CLIENT_ID: ").strip()
client_secret = getpass("Paste GOOGLE_ADS_CLIENT_SECRET (hidden): ").strip()

if not client_id or not client_secret:
    raise SystemExit("Client ID and client secret are required.")

client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

credentials = flow.run_local_server(
    port=0,
    prompt="consent",
    access_type="offline",
)

if not credentials.refresh_token:
    raise SystemExit("Google did not return a refresh token.")

print("\nNew Google Ads refresh token created.")
print("Copy the value below into .env as GOOGLE_ADS_REFRESH_TOKEN:")
print(credentials.refresh_token)