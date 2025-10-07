import requests
import csv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Freshdesk API credentials
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/companies"

# Headers for authentication
auth = (API_KEY, "X")
headers = {"Content-Type": "application/json"}

# Pagination variables
per_page = 100  # Maximum allowed per page
page = 1
vip_companies = []

logging.info("Starting the process of fetching VIP companies from Freshdesk...")

# Fetch all companies and filter VIP ones
while True:
    logging.info(f"Fetching page {page} of company records...")
    response = requests.get(f"{BASE_URL}?per_page={per_page}&page={page}", auth=auth, headers=headers)

    if response.status_code == 200:
        companies = response.json()
        if not companies:
            logging.info("No more companies to fetch. Stopping pagination.")
            break

        # Log first 5 companies to verify structure
        if page == 1:
            logging.info(f"Sample company data: {companies[:5]}")

        # Filtering companies where custom_fields.vip = true
        for company in companies:
            if company.get("custom_fields", {}).get("vip"):
                vip_companies.append(company)

        logging.info(f"Page {page}: {len(companies)} companies retrieved, {len(vip_companies)} VIP companies found so far.")
        page += 1  # Move to the next page

        # Respect rate limits to avoid 429 errors
        time.sleep(1)

    elif response.status_code == 429:  # Rate limit exceeded
        retry_after = int(response.headers.get("Retry-After", 10))
        logging.warning(f"Rate limit exceeded! Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
    else:
        logging.error(f"Failed to fetch companies! Status Code: {response.status_code}, Response: {response.text}")
        break

# Export to CSV
csv_filename = "VIP Districts.csv"
if vip_companies:
    logging.info(f"Exporting {len(vip_companies)} VIP companies to {csv_filename}...")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Domain", "VIP", "Description", "Created At", "Updated At"])

        for company in vip_companies:
            writer.writerow([
                company.get("id"),
                company.get("name"),
                company.get("domains", []),
                company.get("custom_fields", {}).get("vip", False),  # VIP field from custom fields
                company.get("description", ""),
                company.get("created_at"),
                company.get("updated_at")
            ])

    logging.info(f"Export complete! {csv_filename} has been created.")
else:
    logging.warning("No VIP companies found. No file created.")

logging.info("Script execution finished.")

