from requests_oauthlib import OAuth1Session
import os
import json
import vars
import random
import markdown_it

consumer_key = vars.OAUTH_CONSUMER_KEY
consumer_secret = vars.OAUTH_CONSUMER_SECRET

oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

access_token = vars.OAUTH_ACCESS_TOKEN
access_token_secret = vars.OAUTH_ACCESS_TOKEN_SECRET

oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)


def extract_sentences_from_markdown(filename):
    with open(filename, "r", encoding="utf-8") as file:
        markdown_text = file.read()

    # Initialize the Markdown parser
    md = markdown_it.MarkdownIt()

    # Parse the Markdown file and extract text
    parsed_text = md.render(markdown_text)

    # Split the text into sentences
    sentences = parsed_text.split(".")

    # Remove empty sentences and HTML-encoded entities
    sentences = [
        sentence.strip().replace("&lt;", "<").replace("&gt;", ">")
        for sentence in sentences
        if sentence.strip()
    ]

    return sentences


# Specify the path to your Markdown file
markdown_file = "output.md"

# Extract sentences from the Markdown file
sentences = extract_sentences_from_markdown(markdown_file)

# Choose a random sentence to tweet
selected_sentence = random.choice(sentences)

max_tweet_length = 280  # Twitter's previous character limit
if len(selected_sentence) > max_tweet_length:
    selected_sentence = selected_sentence[:max_tweet_length]

payload = {"text": selected_sentence}


response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
)

if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

json_response = response.json()
print(json.dumps(json_response, indent=4, sort_keys=True))
