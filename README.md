# Spotify Daylist Word Cloud

## UPDATE
Spotify has killed this project with the changes to their api limiting the amount of data provided to developers

our last group wordcloud collected from 8 friends over 8 months
![wordcloud](/wordcloud.png)

## Installation
This program requires Python3, spotipy, and gpsread. 
A virtual environment is recommended to prevent risk of breaking your Python installation or OS

```
sudo apt install python3-venv
python3 -m venv env
source env/bin/activate

pip install spotipy
pip install gspread google-auth oauth2client
pip install configparser

```

## Setup

The OAuth's scope includes ```user-library-read```, which provides the API with the ability to:
- Check User's Saved Albums
- Check User's Saved Tracks
- Get Current User's Saved Albums
- Get a User's Saved Tracks
- Check User's Saved Episodes
- Get User's Saved Episodes

If you would like to remove the API's access to the previous information, you can visit https://www.spotify.com/us/account/apps/ to manage apps and remove access from ```daylist spreadsheet```
