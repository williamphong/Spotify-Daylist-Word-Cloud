from wordcloud import WordCloud, STOPWORDS
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import configparser

# URL for colormaps 
# https://matplotlib.org/stable/tutorials/colors/colormaps.html

# Initializes and reads config
config = configparser.ConfigParser()
config.read('config.ini')
service_key_json = config.get('GOOGLE', 'SERIVCE_KEY_JSON')

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Add your service account JSON file
creds = Credentials.from_service_account_file(service_key_json, scopes=scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet by its name
spreadsheet = client.open()

total = ""
sheetDict = {}

# Iterate through each sheet
for i, sheet in enumerate(spreadsheet.worksheets()):
    if i == 0:
        # Skip the first sheet
        continue
    
    print(f"Sheet Name: {sheet.title}")
    
    descriptor_1 = sheet.col_values(1)[1:]
    descriptor_2 = sheet.col_values(2)[1:]

    # change from ['a', 'b'] to a, b
    text0 = ', '.join(descriptor_1)
    text1 = ', '.join(descriptor_2)
    " ".join(text0.split())
    " ".join(text1.split())
    
    sheetDict[sheet.title] = text0 + text1
    
    total = total + text0 + text1
    
    #print(f"DESC 1: {text0}")
    #print(f"DESC 2: {text1}")


#print(f"total: {total}\n")

sheetDict['latest'] = total

print("spreadsheet data read")

#with open("wordcloud.txt", 'w') as f:
#    f.write(total)


# Custom function to tokenize the text
def custom_tokenizer(text):
    # Tokenize by alphanumeric words and preserve phrases with numbers
    tokens = re.findall(r'\b[a-zA-Z0-9-]+\b', text)
    return tokens


stopwords= set(STOPWORDS) # filters out predefined stopwords like the, is, etc..

plt.rcParams["figure.figsize"] = (30,30) # x by x inch plot

# excludes default stopwords 
#wordcloud = WordCloud(width = 1600, height = 800, max_font_size=40, max_words=150, background_color="white",stopwords= [], colormap='plasma').generate(total)
custom_regex = r'\b[a-zA-Z0-9-]+\b'

for name in sheetDict:
    wordcloud = WordCloud(width = 1600, height = 800, max_words=300, background_color="white", stopwords=set(), colormap='plasma',regexp=custom_regex).generate(sheetDict[name])

    plt.plot()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #plt.show()

    # Format the date and time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Example path string with date and time
    path = f"wordclouds/{name}_wordcloud_{timestamp}.png"
    plt.savefig(path, bbox_inches='tight') # save wordcloud by timestamp
    plt.savefig(f"wordclouds/{name}_wordcloud.png", bbox_inches='tight') # latest wordcloud
    print("wordcloud.png saved")



