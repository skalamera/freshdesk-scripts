"""
Freshdesk Knowledge Base Article URL Generator

DESCRIPTION:
This script retrieves all articles from specified folders in the Freshdesk
knowledge base and generates direct URLs for each article. The results are
exported to an Excel file for easy access and reference purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- Valid Freshdesk API key with solutions read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update folder_ids list with your folder IDs
4. Update OUTPUT_URL_PREFIX if your URL structure is different
5. Ensure your API key has permissions for solutions access
6. Run the script: python get_article_url.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Solutions API: https://developers.freshdesk.com/api/#solutions
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- folder_ids: List of folder IDs to process
- OUTPUT_URL_PREFIX: Base URL for article links

OUTPUT:
- Excel file with article names and direct URLs
- Console output showing processing progress
- Error messages for failed folder processing

ARTICLE DATA INCLUDES:
- Article ID from Freshdesk
- Article title/name
- Direct URL for easy access
- Processing status for each folder

ERROR HANDLING:
- Handles HTTP 404 (folder not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual folders fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining folders after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has solutions read permissions
- Check that folder IDs are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that folders contain articles

USAGE SCENARIOS:
- Generate quick reference lists for knowledge base articles
- Create documentation indexes with direct links
- Share article collections with team members
- Build internal knowledge base navigation aids
- Support content management and organization
"""

import requests
import time
import pandas as pd
import base64

# Freshdesk API credentials and endpoint
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/solutions/folders"
OUTPUT_URL_PREFIX = "https://techsupport.benchmarkeducation.com/support/solutions/articles/"

# Encode API Key for Authentication
encoded_api_key = base64.b64encode(f"{API_KEY}:X".encode("utf-8")).decode("utf-8")

# Folder IDs to process
folder_ids = [
    67000581069, 67000578178, 67000568834, 67000577978, 67000577979,
    67000577980, 67000577981, 67000577982, 67000578171, 67000578031,
    67000581156, 67000578068, 67000578069, 67000578101, 67000578273,
    67000580319, 67000580615, 67000581752, 67000581070, 67000581490,
    67000576038
]

def get_articles_from_folder(folder_id):
    """Retrieve all articles from a given folder ID with rate limit handling."""
    headers = {
        "Authorization": f"Basic {encoded_api_key}",
        "Content-Type": "application/json"
    }
    articles = []
    page = 1

    while True:
        try:
            response = requests.get(f"{BASE_URL}/{folder_id}/articles", headers=headers, params={"page": page}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break  # No more articles
                articles.extend(data)
                page += 1
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            elif response.status_code == 401:
                print(f"Unauthorized access. Check API key or permissions for folder {folder_id}.")
                break
            else:
                print(f"Error fetching articles for folder {folder_id}: {response.status_code}")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return articles

def main():
    article_data = []
    for folder_id in folder_ids:
        print(f"Fetching articles for folder ID: {folder_id}")
        articles = get_articles_from_folder(folder_id)
        for article in articles:
            article_id = article.get("id")
            article_name = article.get("title")
            if article_id and article_name:
                article_url = f"{OUTPUT_URL_PREFIX}{article_id}"
                article_data.append({"Article Name": article_name, "URL": article_url})
    
    # Save results to Excel
    df = pd.DataFrame(article_data)
    output_path = "Article_Details.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()

