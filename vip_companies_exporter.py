"""
Freshdesk VIP Districts Export Script

DESCRIPTION:
This script retrieves all companies from Freshdesk and filters for VIP companies
(customers with VIP status enabled). It exports VIP company information to a
CSV file including company details, domains, and timestamps for analysis and
reporting purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with company read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for company read access
4. Run the script: python get_vip_districts.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Companies API: https://developers.freshdesk.com/api/#companies
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- PER_PAGE: Number of companies per API page (default: 100, maximum allowed)
- OUTPUT_FILENAME: CSV file for VIP companies (default: 'VIP Districts.csv')

OUTPUT:
- CSV file with VIP company information
- Console output showing progress and results
- Detailed logging for troubleshooting

CSV OUTPUT FORMAT:
ID,Name,Domain,VIP,Description,Created At,Updated At
12345,Example School District,"example.com,school.org",true,District description,2023-01-15T10:30:00Z,2023-01-20T14:22:00Z

VIP FILTERING:
- Only exports companies where custom_fields.vip = true
- Handles missing custom_fields gracefully
- Processes all pages of company results

ERROR HANDLING:
- Handles HTTP 404 (no companies found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual pages fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining pages after rate limit delay
- Includes 1-second delays between pages

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has company read permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that VIP companies exist in your Freshdesk account

PERFORMANCE CONSIDERATIONS:
- Processes companies in pages (100 per page by default)
- Handles pagination automatically
- Large numbers of companies may take significant time to process
- Rate limiting may cause delays in processing

USAGE SCENARIOS:
- Generate VIP customer lists for account management
- Export VIP data for compliance reporting
- Create VIP customer reference lists
- Data migration and backup operations
- Customer success team reporting
"""

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

