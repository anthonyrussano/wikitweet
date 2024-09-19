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
        return "No links found.", None, None

    # Select one random link
    random_link = random.choice(links)
    article_url = base_url + random_link.get('href')
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    
    # Fetch the title from the <span> element nested within <h1 class="article-title">
    title_tag = article_soup.find('h1', class_='article-title')
    title = title_tag.find('span').text if title_tag and title_tag.find('span') else "No title found"
    
    # Target the specific div for text extraction
    article_body = article_soup.find('div', {'class': 'article-entry', 'style': 'text-align:justify;'})
    if article_body:
        # Extract text up to the first footnote reference
        text_parts = []
        for elem in article_body.descendants:
            if elem.name == 'sup' and 'footnote-ref' in elem.get('class', []):
                break
            if isinstance(elem, str) and not elem.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                text_parts.append(elem.strip())
        text = ''.join(text_parts).strip()

        # Split the collected text into sentences
        article_sentences = [sentence.strip() for sentence in text.split('.') if sentence.strip()]
        
        # Return a random sentence if available along with URL and title
        if article_sentences:
            return random.choice(article_sentences), article_url, title
        else:
            return "No sentences found.", article_url, title
    else:
        return "Article body not found.", article_url, title

# Example usage
base_url = 'https://wikip.co'
category_path = '/categories/natural-healing/'
random_sentence, url, title = fetch_random_sentence(base_url, category_path)
print(title, ":", url)
print(random_sentence)
