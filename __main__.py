import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gspread
from google.oauth2.service_account import Credentials
import configparser
from src import parser

# Function to ensure token is refreshed if expired
def get_spotify_token(username, oauth_instances):
    token_info = oauth_instances[username].get_cached_token()

    if not token_info:
        auth_url = oauth_instances[username].get_authorize_url()
        print(f"Please visit this URL to authorize access for {username}: {auth_url}")
        response_code = input(f"Enter the URL you were redirected to for {username}: ").split('?code=')[1]
        token_info = oauth_instances[username].get_access_token(response_code)
    else:
        if oauth_instances[username].is_token_expired(token_info):
            token_info = oauth_instances[username].refresh_access_token(token_info['refresh_token'])

    return token_info['access_token']


def main():
    # Initializes and reads config
    config = configparser.ConfigParser()
    config.read('config.ini')

    CLIENT_ID = config.get('General', 'CLIENT_ID') # Spotify Client ID
    CLIENT_SECRET = config.get('General', 'CLIENT_SECRET') # Spotify Client Secret
    REDIRECT_URI = config.get('General', 'REDIRECT_URI') # Spotify Redirect URL
    daylist_id = config.get('General', 'DAYLIST_ID') # daylist id
    json_path = config.get('General', 'JSON_PATH') # last daylist" json path
    service_key_json = config.get('GOOGLE', 'SERIVCE_KEY_JSON') # google api service key json

    oauth_instances = {}
    usernames = [] # spotify usernames go here, was hardcoded for personal usage


    for username in usernames:
        oauth_instances[username] = SpotifyOAuth(client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET,
                                                redirect_uri=REDIRECT_URI,
                                                scope='user-library-read',
                                                cache_path=f".cache-{username}")

    # Get access tokens for all users using a list or dictionary
    access_tokens = {}

    for username in usernames:
        access_tokens[username] = get_spotify_token(username, oauth_instances)

    # Use the access tokens to make API requests for each user
    spotify_instances = {}

    for username in usernames:
        spotify_instances[username] = spotipy.Spotify(auth=access_tokens[username])

    # API requests
    for username in usernames:
        sp = spotify_instances[username]
        user_info = sp.current_user()
        #print(f"------------------------------------------------------\n")
        print(f"Logged in as {user_info['id']} - {user_info['display_name']}")
        daylist_parser = parser.Parser(username, sp, daylist_id, json_path, service_key_json)
        daylist_parser.parseDaylist()
        #print(f"------------------------------------------------------\n")

    # You can now access each user's Spotify instance using spotify_instances['username'] dictionary
    # and make API requests as needed.


if __name__ == '__main__':
    main()