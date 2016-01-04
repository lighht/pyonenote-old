import json
import time
from urllib.parse import urlencode, parse_qs

import requests

from pyonenote import SESSION_FILE


class Client:
    DEFAULT_CLIENT_SCOPE = ['wl.signin', 'office.onenote_create', 'wl.offline_access', 'Office.onenote']
    DEFAULT_REDIRECT_URI = 'https://login.live.com/oauth20_desktop.srf'
    OAUTH_AUTHORIZE_URI = 'https://login.live.com/oauth20_authorize.srf'
    OAUTH_TOKEN_URI = 'https://login.live.com/oauth20_token.srf'
    OAUTH_SIGNOUT_URI = 'https://login.live.com/oauth20_logout.srf'
    API_URI = 'https://www.onenote.com/api/v1.0/'
    DEFAULT_CLIENT_ID = '000000004416FFEC'
    DEFAULT_CLIENT_SECRET = 'xdFxXg8SccDLuhrJ8RX8oOfXcjo6fl9-'

    def __init__(self, client_id=DEFAULT_CLIENT_ID, client_secret=DEFAULT_CLIENT_SECRET,
                 client_scope=DEFAULT_CLIENT_SCOPE,
                 redirect_uri=DEFAULT_REDIRECT_URI):
        """
        :param str client_id: Client ID for the app.
        :param str client_secret: Client secret for the app.
        :param list[str] client_scope: (Optional) Permissions for the app.
        :param str redirect_uri: Landing URL during authentication process.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_scope = client_scope
        self.redirect_uri = redirect_uri

        # Should be moved to account class
        self.session_info = None
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
        self.scope = None

    def get_auth_uri(self, display='touch', locale='en'):
        params = {
            'client_id': self.client_id,
            'scope': ' '.join(self.client_scope),
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'display': display,
            'locale': locale
        }
        return self.OAUTH_AUTHORIZE_URI + '?' + urlencode(params)

    def get_refresh_token(self):
        pass

    def get_session_info(self, uri=None, code=None):
        """
        :param str uri: Client ID for the app.
        :param str code: Client secret for the app.
        :returns json formatted response
        """
        if uri is None:
            if self.session_info is None:
                try:
                    with open(SESSION_FILE, 'r') as f:
                        self.session_info = json.loads(f.read())
                    self.renew_if_expired()
                except:
                    print('reading failed')
            else:
                self.renew_if_expired()


        if uri is not None and '?' in uri:
            qs_dict = parse_qs(uri.split('?')[1])
            if 'code' in qs_dict:
                code = qs_dict['code']
            if code is None:
                raise ValueError("Authorization code is not found.")
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'code': code,
            }
            response = requests.post(self.OAUTH_TOKEN_URI, data=params)
            if response.status_code != requests.codes.ok:
                raise ValueError('The authentication code is not valid.')
            session_info = response.json()
            expires_at = time.time() + session_info['expires_in']
            session_info['expires_at'] = expires_at
            self.session_info = session_info
        return self.session_info

    def renew_tokens(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'refresh_token',
            'refresh_token': self.session_info['refresh_token']
        }
        request = requests.post(self.OAUTH_TOKEN_URI, data=params)
        self.session_info = request.json()
        self.session_info['expires_at'] = time.time() + self.session_info['expires_in']
        print("new tokens:" + self.session_info['access_token'])
        self.dump()

    def dump(self):
        self.access_token = self.session_info['access_token']
        self.refresh_token = self.session_info['refresh_token']
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump(self.session_info, f)
                print('session file written')
        except:
            print('writing failed')

    def renew_if_expired(self):
        if time.time() > self.session_info['expires_at']:
            print('token expired.getting new')
            self.renew_tokens()
