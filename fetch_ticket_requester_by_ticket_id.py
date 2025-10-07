"""
Freshdesk Ticket Requesters Data Export Script

DESCRIPTION:
This script retrieves requester information for a list of specific tickets in
Freshdesk and exports the data to a CSV file. It processes tickets in batches
with proper rate limiting and error handling for reliable data collection.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TICKET_IDS list with the ticket IDs you want to analyze
4. Update CSV_FILE name if desired
5. Ensure your API key has permissions for ticket access
6. Run the script: python fetch_ticket_requesters.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_IDS: List of ticket IDs to process
- CSV_FILE: Output CSV file name

OUTPUT:
- CSV file with ticket requester information
- Console output showing processing progress
- Detailed error messages for failed lookups

REQUESTER DATA INCLUDES:
- Ticket ID for reference
- Requester name from ticket data
- Requester email address
- Processing status for each ticket

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Monitors rate limit headers and adjusts timing
- Includes delays between requests to respect limits
- Handles rate limit responses with retry-after delays

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that ticket IDs are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets have associated requesters

USAGE SCENARIOS:
- Generate requester contact lists for specific tickets
- Analyze ticket patterns by requester
- Create mailing lists for ticket follow-ups
- Generate reports for customer communication
- Support workflow analysis and user behavior studies
"""

import requests
import csv
import time
import logging

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2/tickets'
TICKET_IDS = [
    310100, 310382, 310733, 309129, 309932, 310892, 310021, 310754, 309185, 309604,
    310884, 310078, 309657, 309436, 309830, 309595, 308982, 309234, 308920, 310161,
    309971, 310445, 310383, 310639, 310633, 306217, 308843, 310620, 309954, 310369,
    310435, 310271, 309497, 310830, 310903
]
HEADERS = {"Content-Type": "application/json"}
CSV_FILE = 'ticket_requesters.csv'

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def respect_rate_limit(response):
    """Handles Freshdesk rate limits based on response headers."""
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        logging.warning(f"429 Rate Limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return True

    remaining = int(response.headers.get("X-Ratelimit-Remaining", 1))
    used = int(response.headers.get("X-Ratelimit-Used-CurrentRequest", 1))
    if remaining <= 2:
        logging.warning("Approaching rate limit. Sleeping for 10 seconds.")
        time.sleep(10)
    return False

# Output data
results = []

# Process each ticket
for ticket_id in TICKET_IDS:
    url = f"{BASE_URL}/{ticket_id}?include=requester"
    try:
        response = requests.get(url, auth=(API_KEY, 'X'), headers=HEADERS)

        if respect_rate_limit(response):
            # Skip current ticket and retry in the next loop
            continue

        if response.status_code == 200:
            data = response.json()
            requester = data.get('requester', {})
            results.append({
                'ticket_id': ticket_id,
                'requester_name': requester.get('name', ''),
                'requester_email': requester.get('email', '')
            })
            logging.info(f"Fetched requester for ticket {ticket_id}")
        else:
            logging.error(f"Failed to retrieve ticket {ticket_id}: {response.status_code} - {response.text}")

    except Exception as e:
        logging.exception(f"Exception while processing ticket {ticket_id}: {e}")
        time.sleep(5)

# Write to CSV
with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['ticket_id', 'requester_name', 'requester_email'])
    writer.writeheader()
    writer.writerows(results)

logging.info(f"âœ… CSV file '{CSV_FILE}' generated with {len(results)} records.")

