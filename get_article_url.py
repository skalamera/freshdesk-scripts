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

