import json
import sys
from requests_oauthlib import OAuth1Session
import vars

def load_credentials():
    try:
        import vars

        print("Loading credentials from vars.py")
        return (
            vars.OAUTH_CONSUMER_KEY,
            vars.OAUTH_CONSUMER_SECRET,
            vars.OAUTH_ACCESS_TOKEN,
            vars.OAUTH_ACCESS_TOKEN_SECRET,
        )
    except ImportError:
        print(
            "vars.py not found, attempting to load credentials from environment variables"
        )
        return (
            os.getenv("OAUTH_CONSUMER_KEY"),
            os.getenv("OAUTH_CONSUMER_SECRET"),
            os.getenv("OAUTH_ACCESS_TOKEN"),
            os.getenv("OAUTH_ACCESS_TOKEN_SECRET"),
        )

# Check if tweet content was provided as argument
if len(sys.argv) != 2:
    print("Usage: python tweet.py \"your tweet content\"")
    sys.exit(1)

tweet_content = sys.argv[1]

# Load credentials
consumer_key, consumer_secret, access_token, access_token_secret = load_credentials()

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    raise ValueError(
        "Twitter OAuth credentials are not set in vars.py or environment variables."
    )

oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

payload = {"text": tweet_content}
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
