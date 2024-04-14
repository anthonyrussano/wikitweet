import requests
from bs4 import BeautifulSoup
import random

def fetch_random_h3_and_below_content_with_image(base_url, category_path):
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
        return "No links found.", None, None, None

    # Select one random link
    random_link = random.choice(links)
    article_url = base_url + random_link.get('href')
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    
    # Fetch the title from the <span> element nested within <h1 class="article-title">
    title_tag = article_soup.find('h1', class_='article-title')
    title = title_tag.find('span').text if title_tag and title_tag.find('span') else "No title found"

    # Find the image URL
    image_tag = article_soup.find('img')
    image_url = image_tag['src'] if image_tag else "No image found"

    # Remove any <section class="footnotes">
    footnotes_section = article_soup.find('section', class_='footnotes')
    if footnotes_section:
        footnotes_section.decompose()

    # Locate the <h2> element with one of the specific IDs
    h2_tag = article_soup.find('h2', id=lambda x: x in ['Healing-Properties', 'Biological-Properties', 'Disease-Symptom-Treatment'])
    if h2_tag:
        h3_elements = h2_tag.find_all_next('h3', limit=10)  # Find only the first h3 after each h2
        if h3_elements:
            random_h3 = random.choice(h3_elements)
            content_list = [random_h3.text.strip()]
            for sibling in random_h3.next_siblings:
                if sibling.name in ['h3', 'h2']:  # Stop at the next h3 or h2 tag
                    break
                if sibling.name and sibling.text.strip():  # Ignore empty tags and navigate through meaningful content only
                    content_list.append(sibling.text.strip())
            content = '\n'.join(content_list)
            return content, article_url, title, image_url
        else:
            return "No h3 elements found under specified h2.", article_url, title, image_url
    else:
        return "No h2 element with the specified IDs found.", article_url, title, image_url

# Example usage
base_url = 'https://wikip.co'
category_path = '/categories/natural-healing/'
h3_content, url, title, image_url = fetch_random_h3_and_below_content_with_image(base_url, category_path)
print(title, ":", url)
print("Image URL:", image_url)
print(h3_content)
