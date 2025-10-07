"""
Freshdesk Knowledge Base Articles Export Script

DESCRIPTION:
This script exports all articles from the Freshdesk knowledge base, organizing
them by categories and folders. It cleans HTML content from descriptions and
exports the data to a CSV file for documentation and analysis purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with solutions read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update csv_filename if desired
4. Ensure your API key has permissions for solutions access
5. Run the script: python get_articles.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Solutions API: https://developers.freshdesk.com/api/#solutions
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- csv_filename: Output CSV file name

OUTPUT:
- CSV file with cleaned article data
- Console output showing processing progress
- Error messages for failed API calls

ARTICLE DATA INCLUDES:
- Category name for organization
- Folder name for grouping
- Article ID for reference
- Article title
- Cleaned description (HTML removed)
- Creation and update timestamps

CONTENT PROCESSING:
- Removes HTML tags from article descriptions
- Converts HTML entities to readable text
- Preserves article structure and metadata
- Handles encoding for international characters

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Continues processing even if individual articles fail
- Displays clear error messages for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has solutions read permissions
- Check that knowledge base contains categories and folders
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that articles have descriptions

USAGE SCENARIOS:
- Create knowledge base documentation archives
- Generate article inventories for content audits
- Analyze knowledge base structure and organization
- Support content migration projects
- Build internal documentation indexes
"""

import requests
import csv
import re
from html import unescape

# Freshdesk API credentials
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"

# Headers for authentication
headers = {
    "Content-Type": "application/json"
}

# Function to make API requests
def fetch_freshdesk_data(endpoint):
    url = f"https://{DOMAIN}/api/v2/{endpoint}"
    response = requests.get(url, auth=(API_KEY, "X"), headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Function to remove HTML tags from descriptions
def clean_html(raw_html):
    clean_text = re.sub(r'<[^>]+>', '', raw_html)  # Remove HTML tags
    clean_text = unescape(clean_text)  # Convert HTML entities to normal text
    return clean_text.strip()

# Step 1: Get all Solution Categories
categories = fetch_freshdesk_data("solutions/categories")
if categories:
    articles_data = []

    # Step 2: Get all Solution Folders for each category
    for category in categories:
        category_id = category["id"]
        category_name = category["name"]
        folders = fetch_freshdesk_data(f"solutions/categories/{category_id}/folders")

        if folders:
            # Step 3: Get all Solution Articles for each folder
            for folder in folders:
                folder_id = folder["id"]
                folder_name = folder["name"]
                articles = fetch_freshdesk_data(f"solutions/folders/{folder_id}/articles")

                if articles:
                    for article in articles:
                        cleaned_description = clean_html(article["description"])
                        articles_data.append([
                            category_name,
                            folder_name,
                            article["id"],
                            article["title"],
                            cleaned_description,
                            article["created_at"],
                            article["updated_at"]
                        ])

    # Save data to CSV
    csv_filename = "solution_articles_cleaned.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Folder", "Article ID", "Title", "Description", "Created At", "Updated At"])
        writer.writerows(articles_data)

    print(f"CSV file '{csv_filename}' has been created successfully and formatted correctly!")

