import re  # Import the regular expression module
import json
from bs4 import BeautifulSoup  # Import BeautifulSoup
from requests_oauthlib import OAuth1Session
import vars
import random
import markdown_it
from textblob import TextBlob  # For natural language processing tasks

# Setup for OAuth using credentials from a separate file (vars.py)
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


# Function to extract sentences from a markdown file
def extract_sentences_from_markdown(filename):
    with open(filename, "r", encoding="utf-8") as file:
        markdown_text = file.read()

    md = markdown_it.MarkdownIt()
    parsed_text = md.render(markdown_text)

    # Use BeautifulSoup to remove HTML tags
    soup = BeautifulSoup(parsed_text, "lxml")
    text = soup.get_text(
        separator=" "
    )  # Use a space as a separator to avoid words concatenating

    sentences = text.split(".")
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences


# Function to generate up to 3 hashtags from a sentence, excluding those with non-alphanumeric characters
def generate_hashtags(sentence):
    blob = TextBlob(sentence)
    hashtags = set()
    for noun_phrase in blob.noun_phrases:
        # Convert noun phrase to hashtag format, remove spaces, and lowercase it
        hashtag = "#" + noun_phrase.replace(" ", "").lower()
        # Add hashtag only if it is 4 to 23 characters long and contains only alphanumeric characters
        if 4 <= len(hashtag) <= 23 and re.match(r"^#[a-zA-Z0-9]+$", hashtag):
            hashtags.add(hashtag)
    # Return only up to 3 hashtags
    return list(hashtags)[:3]


# Function to truncate the sentence to fit the tweet length
def truncate_sentence(sentence, max_length):
    return (
        sentence
        if len(sentence) <= max_length
        else sentence[:max_length].rsplit(" ", 1)[0]
    )


# Function to format the tweet with hashtags
def format_tweet(sentence, max_length=280):
    hashtags = generate_hashtags(sentence)
    max_length -= sum(len(tag) + 1 for tag in hashtags)  # account for spaces
    truncated_sentence = truncate_sentence(sentence, max_length)
    tweet = "{} {}".format(truncated_sentence, " ".join(hashtags)).strip()
    return tweet if len(tweet) <= 280 else truncate_sentence(tweet, 280)


# Extract sentences from the markdown file
sentences = extract_sentences_from_markdown("output.md")
selected_sentence = random.choice(sentences)
formatted_tweet = format_tweet(selected_sentence)

# Posting the tweet
payload = {"text": formatted_tweet}
response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
)

# Exception handling for the response
if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

# Printing the response details
print("Response code: {}".format(response.status_code))
json_response = response.json()
print(json.dumps(json_response, indent=4, sort_keys=True))
