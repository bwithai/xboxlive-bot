import re
import json
import requests

try:
    from urlparse import urlparse, parse_qs
    from urllib import urlencode, unquote
except ImportError:  # py 3.x
    from urllib.parse import urlparse, parse_qs, urlencode, unquote

headers = {
    'x-xbl-contract-version': '4',
    # 'Accept-Encoding': 'gzip, deflate',
    'content-type': 'application/json',
    # 'MS-CV': 'blwAACI4AADBRQAA',
    # 'Accept-Language': 'en-US',
}


# Approach 1 -----------------------------------------------------------------------------------------------------------

def authenticate(login=None, password=None):
    session = requests.session()
    authenticated = False

    # firstly we have to GET the login page and extract
    # certain data we need to include in our POST request.
    # sadly the data is locked away in some javascript code
    base_url = 'https://login.live.com/oauth20_authorize.srf?'

    # if the query string is percent-encoded the server
    # complains that client_id is missing
    qs = unquote(urlencode({
        'client_id': '0000000048093EE3',
        'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
        'response_type': 'token',
        'display': 'touch',
        'scope': 'service::user.auth.xboxlive.com::MBI_SSL',
        'locale': 'en',
    }))
    resp = session.get(base_url + qs)

    # python 3.x will error if this string is not a
    # bytes-like object
    url_re = b'urlPost:\\\'([A-Za-z0-9:\?_\-\.&/=]+)'
    ppft_re = b'sFTTag:\\\'.*value="(.*)"/>'

    login_post_url = re.search(url_re, resp.content).group(1)
    post_data = {
        'login': login,
        'passwd': password,
        'PPFT': re.search(ppft_re, resp.content).groups(1)[0],
        'PPSX': 'Passpor',
        'SI': 'Sign in',
        'type': '11',
        'NewUser': '1',
        'LoginOptions': '1',
        'i3': '36728',
        'm1': '768',
        'm2': '1184',
        'm3': '0',
        'i12': '1',
        'i17': '0',
        'i18': '__Login_Host|1',
    }

    resp = session.post(
        login_post_url, data=post_data, allow_redirects=False,
    )

    if 'Location' not in resp.headers:
        # we can only assume the login failed
        msg = 'Could not log in with supplied credentials'
        print(msg)
        exit()

    # the access token is included in fragment of the location header
    location = resp.headers['Location']
    parsed = urlparse(location)
    fragment = parse_qs(parsed.fragment)
    access_token = fragment['access_token'][0]

    url = 'https://user.auth.xboxlive.com/user/authenticate'
    resp = session.post(url, data=json.dumps({
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token,
        }
    }), headers=headers)

    json_data = resp.json()
    user_token = json_data['Token']
    uhs = json_data['DisplayClaims']['xui'][0]['uhs']

    url = 'https://xsts.auth.xboxlive.com/xsts/authorize'
    resp = session.post(url, data=json.dumps({
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL",
        }
    }), headers=headers)

    response = resp.json()
    print(response, "\n_____________________________________________________________________________________")
    AUTHORIZATION_HEADER = 'XBL3.0 x=%s;%s' % (uhs, response['Token'])
    # user_xid = response['DisplayClaims']['xui'][0]['xid']
    authenticated = True

    if authenticated:
        print('<xbox.Client: %s>' % login)
    else:
        print('<xbox.Client: Unauthenticated>')
    return response['Token'], AUTHORIZATION_HEADER


# Approach 2 -----------------------------------------------------------------------------------------------------------

CLIENT_ID = "0000000048093EE3"
REDIRECT_URI = "https://login.live.com/oauth20_desktop.srf"


def get_x_token():
    """
    Authorize account for app and receive authorization code
    """

    url = "https://login.live.com/oauth20_authorize.srf"
    query_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "Xboxlive.signin Xboxlive.offline_access",
        "redirect_uri": REDIRECT_URI,
    }

    destination_url = requests.Request("GET", url, params=query_params).prepare().url

    print("Authorize using following URL: " + destination_url)

    authorization_code = input("Enter Code:")

    """
    Authenticate account via authorization code and receive access/refresh token
    """
    base_url = "https://login.live.com/oauth20_token.srf"
    params = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "scope": "Xboxlive.signin Xboxlive.offline_access",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
    }

    resp = requests.post(base_url, data=params)
    print(resp.content)
    if resp.status_code != 200:
        print("Failed to get access token")
        return

    access_token = resp.json()["access_token"]

    """
    Authenticate via access token and receive user token
    """
    url = "https://user.auth.xboxlive.com/user/authenticate"
    headers = {"x-xbl-contract-version": "1"}
    data = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d=" + access_token,
        },
    }

    resp = requests.post(url, json=data, headers=headers)

    if resp.status_code != 200:
        print("Invalid response")
        return

    user_token = resp.json()["Token"]

    """
    Authorize via user token and receive final X token
    """
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    headers = {"x-xbl-contract-version": "1"}
    data = {
        "RelyingParty": "http://xboxlive.com",
        # "RelyingParty": "https://prod.xsts.halowaypoint.com/",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL",
        },
    }

    resp = requests.post(url, json=data, headers=headers)

    if resp.status_code != 200:
        print("Invalid response")
        return

    print(":::XTOKEN:::")
    json_data = resp.json()
    uhs = json_data['DisplayClaims']['xui'][0]['uhs']
    AUTHORIZATION_HEADER = 'XBL3.0 x=%s;%s' % (uhs, json_data['Token'])
    print(AUTHORIZATION_HEADER)
    print("_____________________________________________________\n", json_data)
