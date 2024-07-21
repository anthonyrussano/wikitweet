import json
import random
from requests_oauthlib import OAuth1Session
import vars
import feedparser
import re


def parse_urls_file(file_content):
    urls = []
    for line in file_content.split("\n"):
        if line.startswith("http") and not line.startswith("#"):
            # Split the line by whitespace and take the first part (the URL)
            url = line.split()[0]
            urls.append(url)
    return urls


def get_random_feed(urls):
    return random.choice(urls)


def fetch_latest_content(feed_url):
    feed = feedparser.parse(feed_url)
    if feed.entries:
        latest_entry = feed.entries[0]
        title = latest_entry.title
        link = latest_entry.link
        return f"{title}\n{link}"
    return None


def clean_text(text):
    # Remove HTML tags
    clean = re.sub("<[^<]+?>", "", text)
    # Limit to 280 characters
    return clean[:280]


# Parse the URLs file
with open("urls_file.txt", "r") as file:
    urls_content = file.read()
urls = parse_urls_file(urls_content)

# Get a random feed
random_feed = get_random_feed(urls)

# Fetch the latest content
content = fetch_latest_content(random_feed)

if content:
    # Clean and prepare the tweet text
    tweet_text = clean_text(content)

    # Twitter API credentials
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

    payload = {"text": tweet_text}
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

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
    print("No content found to tweet.")
