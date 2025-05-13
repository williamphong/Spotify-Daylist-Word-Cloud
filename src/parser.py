import re
import json
import gspread
from google.oauth2.service_account import Credentials

class Parser:
        
    # Parser object initialization
    def __init__(self, username, sp, daylist_id, json_path, service_key_json):
        self.username = username
        self.sp = sp
        self.daylist_id = daylist_id
        self.json_path = json_path
        self.service_key_json = service_key_json

    # Function to get the playlist title
    def get_playlist_title(self):
        try:
            playlist = self.sp.playlist(self.daylist_id)
            title = playlist.get('name', 'No title available.')
            return title
        except Exception as e:
            return f"An error occurred obtaining the title: {e}"

    # Function to get the playlist description
    def get_playlist_description(self):
        try:
            playlist = self.sp.playlist(self.daylist_id)
            description = playlist.get('description', 'No description available.')
            return description
        except Exception as e:
            return f"An error occurred obtaining the description: {e}"

    def update_spreadsheet(self, name, data):
        # Define the scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        # Add your service account JSON file
        creds = Credentials.from_service_account_file(self.service_key_json, scopes=scope)

        # Authorize the client
        client = gspread.authorize(creds)

        # Open the Google Sheet by its name
        spreadsheet = client.open("")

        # Select the sheet based on name
        sheet = spreadsheet.worksheet(name)

        # Insert the data
        for row in data:
            sheet.append_row(row)
        
        print(f"Spreadsheet has been updated")

    # Function that updates json file
    def parseText(self, title, description):
        # days of week and times of day phrases that the spotify daylist uses
        days_of_week = set(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        time_of_day = (['early morning', 'late night', 'morning', 'afternoon', 'evening', 'night']) # sets have no order which makes phrase finding harder

        desc_arr = set([phrase.strip() for phrase in description.split("Here's some: ")[-1].replace(" and ", ", ").split(",")])
        #print(f"desc: '{mod_desc}'")

        # Initialize variables for removed day and time
        removed_day = '(none)'
        removed_tod = '(none)'
        title_cpy = title

        # Process title to remove days and times, and extract them
        for tod in time_of_day:
            if tod in title_cpy:
                removed_tod = tod
                title_cpy = title_cpy.replace(tod, '')
                break  # Exit the loop after the first match
            
        for word in title.split():
            if word in days_of_week:
                removed_day = word
                title_cpy = title_cpy.replace(word, '')
                break

        # Reconstruct cleaned title and find title_cpy part
        data = []
        #print(f"title cpy: '{title_cpy}'")
        #print(f"day: {removed_day}")
        #print(f"tod: {removed_tod}")


        # Remove phrases from title_cpy and update data
        for phrase in desc_arr:
            if phrase in title_cpy:
                data.append(phrase.replace(' ', '-')) # for formatting ie "city pop" -> "city-pop"
                #print(f"phrase {phrase}")
                title_cpy = title_cpy.replace(phrase, '').strip()

        # Process title_cpy and update data accordingly
        title_words = title.split()
        for i, word in enumerate(title_words):
            if i < len(title_words) - 1 and word in title_cpy.split():
                following_word = title_words[i + 1]
                for j, phrase in enumerate(data):
                    if following_word in phrase:
                        data[j] = f"{word}-{phrase}"  # for formatting ie "city pop" -> "city-pop"
                        title_cpy = title_cpy.replace(word, '').strip()

        # Add title_cpy, removed day, and removed time to data
        if title_cpy:
            data.append(title_cpy.strip())

        data.append(removed_day) # adds day
        data.append(removed_tod.replace(' ', '-')) # adds time of day, for formatting ie "early morning" -> "early-morning"
        data.append(f"{title}") # adds title to sheet in case of debug
        data.append(f"{', '.join(desc_arr)}") # adds description to sheet in case of debug

        return data

    def parseDaylist(self):
        user_id = self.sp.current_user()['id']
        display_name = self.sp.current_user()['display_name']
        
        # Get daylist title and description and extract relevant phrases
        title = self.get_playlist_title().replace("daylist • ", "")
        description = self.get_playlist_description()
        description = re.sub(r'^.*?\.\s|<a href="[^"]*">([^<]*)</a>', lambda m: m.group(1) if m.lastindex else '', description)

        # Initialize flag to track if the sheet needs to be updated
        update_sheet = False

         # Read existing JSON data from file, if it exists
        json_file_path = self.json_path
        try:
            with open(json_file_path, 'r') as json_file:
                last_daylist = json.load(json_file)
        except FileNotFoundError:
            last_daylist = {"users": []}

        # Using next() to find the user
        user = next((u for u in last_daylist["users"] if "id" in u and u["id"] == user_id), None)
        
        if user:
            if user["title"] == title and user.get("description") == description:
                print("Pre-existing daylist data found")
                update_sheet = False
            else:
                print(f"Updating {user_id}: {display_name}'s data ")
                user["title"] = title
                user["description"] = description
                user["data"] = self.parseText(title, description)
                #print(f"changed data: {user["data"]}\n")
                update_sheet = True
        else:
            # Handle the case where the user is not found if needed
            print(f"{user_id}: {display_name} not found, adding json entry")
            json_data = {
                "id": user_id,  # user id 
                "name": display_name,
                "title": title,
                "description": description,
                "data": self.parseText(title, description)
            }
            last_daylist["users"].append(json_data)
            #print(f"json entry: {json_data}\n")
            update_sheet = True

        if(update_sheet):
            # Write updated JSON data back to the file
            with open(json_file_path, 'w') as json_file:
                json.dump(last_daylist, json_file, indent=4)
            
            print(f"JSON data written to {json_file_path}")
            #self.update_spreadsheet(self.username, last_daylist["data"])

        user = next((u for u in last_daylist["users"] if "id" in u and u["id"] == user_id), None)
        if user:
            print(f"{user}\n")

