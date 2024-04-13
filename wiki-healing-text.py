import requests
from bs4 import BeautifulSoup
import random

def fetch_h3_and_below_content(base_url, category_path):
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
    
    # Remove any <section class="footnotes">
    footnotes_section = article_soup.find('section', class_='footnotes')
    if footnotes_section:
        footnotes_section.decompose()

    # Locate the <h2 id="Healing-Properties"> element and fetch the next h3 content
    h2_tag = article_soup.find('h2', id='Healing-Properties')
    if h2_tag:
        next_h3 = h2_tag.find_next('h3')
        if next_h3:
            # Include the text of the h3 element itself
            content_list = [next_h3.text.strip()]
            for sibling in next_h3.next_siblings:
                if sibling.name == 'h3':  # Stop at the next h3 tag
                    break
                if sibling.name and sibling.text.strip():  # Ignore empty tags and navigate through meaningful content only
                    content_list.append(sibling.text.strip())
            content = '\n'.join(content_list)
            return content, article_url, title
        else:
            return "No subsequent h3 element found.", article_url, title
    else:
        return "No h2 element with ID 'Healing-Properties' found.", article_url, title

# Example usage
base_url = 'https://wikip.co'
category_path = '/categories/natural-healing/'
h3_content, url, title = fetch_h3_and_below_content(base_url, category_path)
print(title, ":", url)
print(h3_content)
