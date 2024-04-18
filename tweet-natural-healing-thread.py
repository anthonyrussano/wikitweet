import os
import requests
from bs4 import BeautifulSoup
import random
import time
from requests_oauthlib import OAuth1Session

# OAuth credentials
consumer_key = os.getenv('OAUTH_CONSUMER_KEY')
consumer_secret = os.getenv('OAUTH_CONSUMER_SECRET')
access_token = os.getenv('OAUTH_ACCESS_TOKEN')
access_token_secret = os.getenv('OAUTH_ACCESS_TOKEN_SECRET')

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    raise ValueError("Twitter OAuth credentials are not set in environment variables.")

def fetch_random_h3_and_below_content_with_image(base_url, category_path, attempted_urls=None):
    if attempted_urls is None:
        attempted_urls = []

    url = f"{base_url}{category_path}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', class_='timeline-article-title')
    
    # Filter out already attempted URLs
    links = [link for link in links if base_url + link.get('href') not in attempted_urls]
    if not links:
        return None, None, None, "No suitable links found."

    random_link = random.choice(links)
    article_url = base_url + random_link.get('href')
    if article_url in attempted_urls:
        return None, None, None, "No new articles left to try."
    attempted_urls.append(article_url)

    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    
    title_tag = article_soup.find('h1', class_='article-title')
    title = title_tag.find('span').text if title_tag and title_tag.find('span') else "No title found"
    
    image_tag = article_soup.find('img')
    image_url = image_tag['src'] if image_tag else None
    
    footnotes_section = article_soup.find('section', class_='footnotes')
    if footnotes_section:
        footnotes_section.decompose()

    content_list = []
    h2_tag = article_soup.find('h2', id=lambda x: x in ['Healing-Properties', 'Biological-Properties', 'Disease-Symptom-Treatment'])
    if h2_tag:
        h3_elements = h2_tag.find_all_next('h3', limit=10)
        for h3 in h3_elements:
            content_list.append(h3.text.strip())
            for sibling in h3.next_siblings:
                if sibling.name in ['h3', 'h2']:
                    break
                if sibling.name:
                    content_list.append(sibling.text.strip())
                    
    if not content_list:
        # Recursively try next article
        return fetch_random_h3_and_below_content_with_image(base_url, category_path, attempted_urls)

    content = '\n'.join(content_list)
    return title, content, image_url, article_url

def upload_image_to_twitter(image_url, oauth_session):
    response = requests.get(image_url, stream=True)
    if response.status_code != 200:
        return None
    files = {'media': ('filename.jpg', response.raw, 'image/jpeg')}
    response = oauth_session.post("https://upload.twitter.com/1.1/media/upload.json", files=files)
    if response.status_code != 200:
        return None
    return response.json()['media_id_string']

def exponential_backoff_retry(request_func, max_retries=5):
    retry_delay = 10  # start with 10 seconds delay
    for attempt in range(max_retries):
        response = request_func()
        if response.status_code == 201:
            return response
        elif response.status_code == 429:
            print(f"Rate limit exceeded, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # double the delay for the next attempt
        else:
            print(f"Failed to post tweet with status {response.status_code}: {response.text}")
            break
    return None

def post_tweet(title, content, url, media_id, oauth_session):
    base_tweet_text = f"{title} \nRead more: {url}"
    max_tweet_length = 280
    tweets = []
    while len(content) > 0:
        available_length = max_tweet_length - len(base_tweet_text) - 4
        if len(content) <= available_length:
            tweet_text = f"{content} \nRead more: {url}"
            content = ""
        else:
            split_point = content.rfind('.', 0, available_length)
            if split_point == -1:
                split_point = available_length
            tweet_text = content[:split_point + 1]
            content = content[split_point + 1:]
        tweets.append(tweet_text)

    previous_tweet_id = None
    for tweet_text in tweets:
        payload = {"text": tweet_text}
        if media_id:
            payload["media"] = {"media_ids": [media_id]}
        if previous_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}

        # Wrap the API call in a retry logic function
        response = exponential_backoff_retry(lambda: oauth_session.post("https://api.twitter.com/2/tweets", json=payload))
        if response and response.status_code == 201:
            response_data = response.json()
            previous_tweet_id = response_data["data"]["id"]

# Setup OAuth session
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)

# Scrape content and image
base_url = 'https://wikip.co'
category_path = '/categories/natural-healing/'
title, content, image_url, url = fetch_random_h3_and_below_content_with_image(base_url, category_path)

# Upload image and post tweet
if image_url:
    media_id = upload_image_to_twitter(image_url, oauth)
    if media_id:
        response = post_tweet(title, content, url, media_id, oauth)
        print(response)
    else:
        print("Failed to upload image.")
else:
    print("No image found to upload.")
