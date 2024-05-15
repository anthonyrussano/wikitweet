# wikitweet

### Documentation for `tweet-natural-healing-thread.py`

#### Overview
This script scrapes random articles from a specified category on a website, extracts content and an image, and posts the extracted content as a Twitter thread using OAuth for authentication. The script is designed to be run periodically, such as from a GitHub Actions workflow.

#### Functionality
1. **OAuth Authentication**: Sets up Twitter OAuth credentials from environment variables.
2. **Scraping Content**: Fetches random articles from a specific category on a website, extracts the title, main content, and an image.
3. **Image Upload**: Uploads the extracted image to Twitter.
4. **Tweet Posting**: Posts the content as a Twitter thread, with appropriate handling for content length and Twitter API rate limits.

#### Script Breakdown
1. **OAuth Setup**: 
   ```python
   consumer_key = os.getenv('OAUTH_CONSUMER_KEY')
   consumer_secret = os.getenv('OAUTH_CONSUMER_SECRET')
   access_token = os.getenv('OAUTH_ACCESS_TOKEN')
   access_token_secret = os.getenv('OAUTH_ACCESS_TOKEN_SECRET')

   if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
       raise ValueError("Twitter OAuth credentials are not set in environment variables.")
   ```

2. **Fetching Content**:
   ```python
   def fetch_random_h3_and_below_content_with_image(base_url, category_path, attempted_urls=None):
       ...
   ```

3. **Uploading Image**:
   ```python
   def upload_image_to_twitter(image_url, oauth_session):
       ...
   ```

4. **Posting Tweets with Exponential Backoff**:
   ```python
   def exponential_backoff_retry(request_func, max_retries=5):
       ...
   def post_tweet(title, content, url, media_id, oauth_session):
       ...
   ```

5. **Script Execution**:
   ```python
   oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)

   base_url = 'https://wikip.co'
   category_path = '/categories/natural-healing/'
   title, content, image_url, url = fetch_random_h3_and_below_content_with_image(base_url, category_path)

   if image_url:
       media_id = upload_image_to_twitter(image_url, oauth)
       if media_id:
           post_tweet(title, content, url, media_id, oauth)
       else:
           print("Failed to upload image.")
   else:
       print("No image found to upload.")
   ```

### GitHub Actions Workflow

This GitHub Actions workflow runs the `tweet-natural-healing-thread.py` script periodically or manually. It checks out the repository, sets up Python, installs dependencies, and runs the script with the required OAuth credentials.

```yaml
name: Run Tweet Script

on:
  schedule:
    - cron: '0 * * * *'  # Runs every hour, adjust as needed
  workflow_dispatch:  # Allows manual triggering from GitHub web interface

jobs:
  run-script:
    runs-on: ubuntu-latest  # Specifies the runner environment

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2  # Checks out your repository under $GITHUB_WORKSPACE

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'  # Set the Python version

    - name: Install dependencies
      run: pip install -r requirements.txt  # Installs required Python packages

    - name: Run script
      env:
        OAUTH_CONSUMER_KEY: ${{ secrets.OAUTH_CONSUMER_KEY }}
        OAUTH_CONSUMER_SECRET: ${{ secrets.OAUTH_CONSUMER_SECRET }}
        OAUTH_ACCESS_TOKEN: ${{ secrets.OAUTH_ACCESS_TOKEN }}
        OAUTH_ACCESS_TOKEN_SECRET: ${{ secrets.OAUTH_ACCESS_TOKEN_SECRET }}
      run: python tweet-natural-healing-thread.py
```

### Setting Up
1. **Repository Setup**:
   - Ensure the script `tweet-natural-healing-thread.py` is in the repository.
   - Create a `requirements.txt` with all the necessary dependencies, e.g., `requests`, `beautifulsoup4`, `requests_oauthlib`.

2. **GitHub Secrets**:
   - Go to the repository settings on GitHub.
   - Add the following secrets:
     - `OAUTH_CONSUMER_KEY`
     - `OAUTH_CONSUMER_SECRET`
     - `OAUTH_ACCESS_TOKEN`
     - `OAUTH_ACCESS_TOKEN_SECRET`

3. **Manual Triggering**:
   - The workflow can be manually triggered from the GitHub Actions tab in the repository.

4. **Periodic Scheduling**:
   - The workflow is configured to run every hour by default. Adjust the cron expression as needed.

This setup ensures that the script runs periodically or on-demand, fetching content and posting it to Twitter automatically.