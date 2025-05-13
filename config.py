import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser

# Initialize and read config
config = configparser.ConfigParser()
config.read('daylist/config.ini')

# Spotify API credentials
CLIENT_ID = config.get('General', 'CLIENT_ID')
CLIENT_SECRET = config.get('General', 'CLIENT_SECRET')
REDIRECT_URI = config.get('General', 'REDIRECT_URI')


# Initialize SpotifyOAuth instance without cache path initially
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope='user-library-read user-read-email',
                        cache_path=f".cache-", #hard coded cache naming
                        show_dialog=True) # Forces the authorization dialog to be shown)

# Function to ensure token is refreshed if expired
def get_spotify_token():
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Please visit this URL to authorize access: {auth_url}")
        response_code = input("Enter the URL you were redirected to: ").split('?code=')[1]
        token_info = sp_oauth.get_access_token(response_code)
    else:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info['access_token']

# Get a valid access token
access_token = get_spotify_token()

# Use the access token to make API requests
sp = spotipy.Spotify(auth=access_token)
user_info = sp.current_user()
print(user_info['id'])
name = user_info['display_name']
print(f"Logged in as: {name}\n")
