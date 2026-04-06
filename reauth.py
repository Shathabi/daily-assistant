"""Re-authenticate Google APIs"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate(token_path, scopes, label, force_new=False):
    """Authenticate a Google account"""
    creds = None
    credentials_path = 'config/credentials.json'

    if not force_new and os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(f"\n>>> Browser will open. Log into {label} and click 'Allow' <<<")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            # Force account selection so user can pick the right account
            creds = flow.run_local_server(
                port=0,
                prompt='select_account'
            )

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Gmail - shathabi@gmail.com
print("1. Authenticating Gmail (shathabi@gmail.com)...")
authenticate('config/token.pickle', SCOPES_GMAIL, 'shathabi@gmail.com')
print("✓ shathabi@gmail.com authenticated!")

# Gmail - abi.mullusoge@gmail.com
print("\n2. Authenticating Gmail (abi.mullusoge@gmail.com)...")
authenticate('config/token2.pickle', SCOPES_GMAIL, 'abi.mullusoge@gmail.com', force_new=True)
print("✓ abi.mullusoge@gmail.com authenticated!")

# Calendar
print("\n3. Authenticating Calendar...")
authenticate('config/calendar_token.pickle', SCOPES_CALENDAR, 'your Google Calendar account')
print("✓ Calendar authenticated!")

print("\n✅ All done! Your daily assistant is ready.")
