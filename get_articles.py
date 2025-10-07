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

