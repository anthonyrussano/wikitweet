import requests
from bs4 import BeautifulSoup
import random

def fetch_random_sentence(base_url, category_path):
    # Complete URL
    url = f"{base_url}{category_path}"
    
    # Send HTTP request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links within article titles
    links = soup.find_all('a', class_='timeline-article-title')
    if not links:
        return "No links found."

    # Select one random link
    random_link = random.choice(links)
    article_url = base_url + random_link.get('href')
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    
    # Target the specific div for text extraction
    article_body = article_soup.find('div', {'class': 'article-entry', 'style': 'text-align:justify;'})
    if article_body:
        # Extract text and split into sentences
        text = article_body.get_text()
        article_sentences = [sentence.strip() for sentence in text.split('.') if sentence.strip()]
        
        # Return a random sentence if available
        if article_sentences:
            return random.choice(article_sentences)
        else:
            return "No sentences found."
    else:
        return "Article body not found."

# Example usage
base_url = 'https://wikip.co'
category_path = '/categories/natural-healing/'
random_sentence = fetch_random_sentence(base_url, category_path)
print("Random sentence:", random_sentence)
