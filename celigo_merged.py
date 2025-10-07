import requests
import base64
import time

# API key and Freshdesk domain
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2'

# Encode the API key in base64
encoded_api_key = base64.b64encode(f"{API_KEY}:X".encode('utf-8')).decode('utf-8')

# Headers for authentication
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_api_key}'
}

# Ticket IDs extracted from the image
ticket_ids = [
    264878, 264879, 264880, 264887, 264888,
    264889, 264890, 264891, 264892, 264893
]

def get_merged_tickets(parent_ticket_id):
    """Fetch tickets merged into the parent ticket."""
    url = f'{BASE_URL}/tickets/{parent_ticket_id}/merged_tickets'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 10))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return get_merged_tickets(parent_ticket_id)
    else:
        print(f"Failed to fetch merged tickets for ticket ID {parent_ticket_id}: {response.status_code}, {response.text}")
        return []

def main():
    merged_tickets = []
    
    # Step 1: For each ticket ID, get the merged tickets
    for ticket_id in ticket_ids:
        merged = get_merged_tickets(ticket_id)
        if merged:
            merged_tickets.extend(merged)

    # Step 2: Identify closed merged tickets
    closed_merged_tickets = [t for t in merged_tickets if t['status'] == 5]  # Status 5 indicates Closed

    # Output the results
    if closed_merged_tickets:
        print("Closed merged tickets:")
        for ticket in closed_merged_tickets:
            print(f"Ticket ID: {ticket['id']}, Subject: {ticket['subject']}")
    else:
        print("No closed merged tickets found.")

if __name__ == '__main__':
    main()

