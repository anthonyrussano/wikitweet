import requests
from bs4 import BeautifulSoup
import random
from requests_oauthlib import OAuth1Session
import vars

# OAuth credentials
consumer_key = os.getenv('OAUTH_CONSUMER_KEY')
consumer_secret = os.getenv('OAUTH_CONSUMER_SECRET')
access_token = os.getenv('OAUTH_ACCESS_TOKEN')
access_token_secret = os.getenv('OAUTH_ACCESS_TOKEN_SECRET')

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    raise ValueError("Twitter OAuth credentials are not set in environment variables.")


def fetch_random_h3_and_below_content_with_image(base_url, category_path):
    url = f"{base_url}{category_path}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', class_='timeline-article-title')
    if not links:
        return None, None, None, "No links found."
    
    random_link = random.choice(links)
    article_url = base_url + random_link.get('href')
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
    content = '\n'.join(content_list) if content_list else "..."
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

def post_tweet(title, content, url, media_id, oauth_session):
    tweet_text = f"{title} \n {content} \n Read more: {url}"
    if media_id:
        payload = {
            "text": tweet_text,
            "media": {
                "media_ids": [media_id]
            }
        }
    else:
        payload = {"text": tweet_text}
    response = oauth_session.post("https://api.twitter.com/2/tweets", json=payload)
    return response.json()

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
