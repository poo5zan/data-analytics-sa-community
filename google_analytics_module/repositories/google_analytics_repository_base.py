"""Google Analytics API methods"""

import os
import sys
import logging
sys.path.insert(1, os.getcwd())

# pylint: disable=wrong-import-position
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from helpers.string_helper import StringHelper
from google_analytics_module.enums import GoogleAuthenticationMethod
# pylint: enable=wrong-import-position


class GoogleAnalyticsRepositoryBase:
    """Retrieve data from google analytics"""

    def __init__(
        self,
        google_authentication_method: GoogleAuthenticationMethod,
        oauth_credentials_filepath: str,
        oauth_token_filepath: str,
    ) -> None:
        self.google_authentication_method = google_authentication_method
        self.oauth_credentials_filepath = oauth_credentials_filepath
        self.oauth_token_filepath = oauth_token_filepath
        self.str_helper = StringHelper()
        self.log = logging.getLogger(__name__)

        if google_authentication_method == GoogleAuthenticationMethod.OAUTH:
            if self.str_helper.is_null_or_whitespace(oauth_credentials_filepath):
                raise ValueError("oauth credentials filepath is required.")

            if self.str_helper.is_null_or_whitespace(oauth_token_filepath):
                raise ValueError("oauth token filepath is required.")

        self.creds = None

    def get_oauth_credentials(self):
        """get oauth credentials"""
        scopes = ["https://www.googleapis.com/auth/analytics.readonly"]
        if os.path.exists(self.oauth_token_filepath):
            self.creds = Credentials.from_authorized_user_file(
                self.oauth_token_filepath, scopes
            )
            if not self.creds or not self.creds.valid:
                self.refresh_oauth_token()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.oauth_credentials_filepath, scopes
            )
            self.creds = flow.run_local_server(port=0)
            with open(self.oauth_token_filepath, "w", encoding="UTF-8") as token:
                token.write(self.creds.to_json())

    # REFRESH token doesnot work, need to debug it later
    def refresh_oauth_token(self):
        """refresh oauth token if expired"""
        if self.creds is None:
            self.get_oauth_credentials()
        elif self.creds.expired:
            self.creds.refresh(Request())
            with open(self.oauth_token_filepath, "w", encoding="UTF-8") as token:
                token.write(self.creds.to_json())
