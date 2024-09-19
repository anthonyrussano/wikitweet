import re
import requests
import random
import json
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1Session
import vars  # Make sure this module contains your OAuth credentials


# Function to list directories in the repository
def get_directories(repo_url):
    response = requests.get(repo_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch repository data: " + response.text)

    directories = [item["path"] for item in response.json() if item["type"] == "dir"]
    return directories


# Function to list HTML files in a directory
def get_html_files_in_directory(repo_url, directory):
    dir_url = f"{repo_url}/{directory}"
    response = requests.get(dir_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch directory data: " + response.text)

    html_files = [
        item["path"] for item in response.json() if item["path"].endswith(".html")
    ]
    return html_files


# Function to get the content of a file from GitHub
def get_file_content_from_github(file_url):
    response = requests.get(file_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch file content: " + response.text)

    return response.text


# Function to extract a random sentence from HTML content
def extract_random_sentence(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()
    sentences = re.split(r"(?<=[.!?]) +", text)  # Split text into sentences

    suitable_sentences = [
        s for s in sentences if len(s) <= 280
    ]  # Filter sentences within Twitter's limit

    if not suitable_sentences:
        return None  # Return None if no suitable sentence is found

    return random.choice(suitable_sentences).strip()


# Twitter OAuth setup
consumer_key = vars.OAUTH_CONSUMER_KEY
consumer_secret = vars.OAUTH_CONSUMER_SECRET
access_token = vars.OAUTH_ACCESS_TOKEN
access_token_secret = vars.OAUTH_ACCESS_TOKEN_SECRET

oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# Main process
repo_url = "https://api.github.com/repos/wikip-co/public/contents"  # Root URL of the repo contents
directories = get_directories(repo_url)
if not directories:
    raise Exception("No directories found in the repository")

selected_dir = random.choice(directories)
html_files = get_html_files_in_directory(repo_url, selected_dir)

if not html_files:
    raise Exception("No HTML files found in the selected directory")

selected_file = random.choice(html_files)
selected_file_url = (
    "https://raw.githubusercontent.com/wikip-co/public/main/" + selected_file
)
file_content = get_file_content_from_github(selected_file_url)

sentence = extract_random_sentence(file_content)

if not sentence:
    raise Exception("Could not find a suitable sentence within the character limit")

# Prompt the user before posting
user_confirmation = input("Tweet this sentence? (yes/no): " + sentence + "\n")
if user_confirmation.lower() == "yes":
    # Post to Twitter
    payload = {"text": sentence}

    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    print("Response code: {}".format(response.status_code))
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
else:
    print("Tweeting aborted by the user.")
