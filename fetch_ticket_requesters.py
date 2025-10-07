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

