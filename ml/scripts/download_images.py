#This file creates the dataset of card images
import json
import os 
import random 
import requests #Sending API requests (for scryfall)
import re #To clean the filenames
import time 
from tqdm import tqdm

#Creating the files for each card 
base_dir = os.path.dirname(__file__)  #This is ml/scripts
data_dir = os.path.join(base_dir, "../data")
card_dir = os.path.join(data_dir, "card_images")
json_path = os.path.join(data_dir, "AllCards.json")

#Creates the folder if it doesn't exist
os.makedirs(card_dir, exist_ok=True)

#Opening and loading through the json file
with open("ml/data/AllCards.json", "r", encoding="utf-8") as f:
    data = json.load(f) #Converting the json into a dictionary
    
card_names = list(data.keys()) #Getting a list of all the card names

#Ensures it is the same randomised card selection
random.seed(42)
random.shuffle(card_names) #Reorders the cards randomly

#Dataset size
card_names = card_names[:60]
print(card_names)

def clean_name(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name) #Santises the name by replacing any character which isn't a letter

#Downloading images via Scryfall API
def download_card(name):
    url = "https://api.scryfall.com/cards/named" #The link of the API
    params = {"fuzzy" : name} #Used to match the names
    req = requests.get(url, params=params) #Sending the request for the card
    #Checking if the API request failed
    if req.status_code != 200:
        print("Failed: %s" % (name))
        return
    
    data = req.json() #Turning the request into a dictionary
    
    if "image_uris" in data:  #'image_uris' are the normal cards
        img_url = data["image_uris"]["normal"]
    elif "card_faces" in data: #These are the double faced cards
        img_url = data["card_faces"][0]["image_uris"]["normal"]
    else: #If there is no image for that card
        print("No image for %s" % (name))
        return
    
    #Downloading the image bytes
    img_data = requests.get(img_url).content
    
    safe_name = clean_name(name)
    #Creating the card folder
    card_folder = os.path.join(card_dir, safe_name)
    os.makedirs(card_folder, exist_ok=True)
    
    #Writing the binary data (image) inside the folder
    with open(os.path.join(card_folder, "img_0.jpg"), "wb") as f:
        f.write(img_data)

#Looping through each card
for name in tqdm(card_names):
    download_card(name) #Downloads each card
    time.sleep(0.1) #A 0.1s delay between downloads (to avoid, overwhelming the server/rate-limiting)
    
