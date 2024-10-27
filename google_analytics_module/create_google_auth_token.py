'''
    Creates google authentication token
'''
from google_auth_oauthlib.flow import InstalledAppFlow

# Define OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics',
    'openid'
    ]
CLIENT_SECRETS_FILE = './credentials/oauth_credentials.json'

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
creds = flow.run_local_server()
with open('./credentials/token.json', 'w', encoding='UTF-8') as token:
    token.write(creds.to_json())
