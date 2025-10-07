import requests
import json
import time
import logging
from datetime import datetime, timedelta

# Constants
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
TICKETS_ENDPOINT = f"https://{DOMAIN}/api/v2/tickets"
CONTACTS_ENDPOINT = f"https://{DOMAIN}/api/v2/contacts"

# Calculate the date 30 days ago
thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_tickets():
    all_tickets = []
    page = 1

    while True:
        logging.info(f"Fetching page {page} of tickets")
        response = requests.get(
            TICKETS_ENDPOINT,
            headers={"Content-Type": "application/json"},
            params={"page": page, "per_page": 100, "updated_since": thirty_days_ago},
            auth=(API_KEY, "X")
        )

        if response.status_code != 200:
            logging.error(f"Failed to fetch tickets: {response.status_code} - {response.text}")
            break

        tickets = response.json()
        if not tickets:
            logging.info("No more tickets found")
            break

        all_tickets.extend(tickets)

        # Check rate limit and handle 429 errors
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if rate_limit_remaining == 0:
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            sleep_time = reset_time - time.time() + 1  # Adding 1 second to ensure rate limit reset
            logging.warning(f"Rate limit reached. Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
        else:
            page += 1

    return all_tickets

def get_contact_details(contact_id):
    response = requests.get(
        f"{CONTACTS_ENDPOINT}/{contact_id}",
        headers={"Content-Type": "application/json"},
        auth=(API_KEY, "X")
    )

    if response.status_code == 200:
        return response.json(), response
    else:
        logging.error(f"Failed to fetch contact details for {contact_id}: {response.status_code} - {response.text}")
        return {}, response

def extract_ticket_info(tickets):
    extracted_info = []
    unique_contacts = {}
    for ticket in tickets:
        contact_details, response = get_contact_details(ticket['requester_id'])
        extracted_info.append({
            "ticket_id": ticket["id"],
            "created_at": ticket["created_at"],
            "contact_details": {
                "name": contact_details.get("name"),
                "email": contact_details.get("email"),
                "phone": contact_details.get("phone"),
            }
        })
        
        # Add to unique contacts list
        contact_id = ticket['requester_id']
        if contact_id not in unique_contacts:
            unique_contacts[contact_id] = contact_details
        
        # Rate limit handling for contacts endpoint
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if rate_limit_remaining == 0:
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            sleep_time = reset_time - time.time() + 1
            logging.warning(f"Rate limit reached while fetching contacts. Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
    return extracted_info, list(unique_contacts.values())

def save_tickets_to_file(tickets, filename="tickets.json"):
    with open(filename, 'w') as file:
        json.dump(tickets, file, indent=4)
    logging.info(f"Tickets saved to {filename}")

def save_contacts_to_file(contacts, filename="contacts.json"):
    with open(filename, 'w') as file:
        json.dump(contacts, file, indent=4)
    logging.info(f"Contacts saved to {filename}")

def main():
    tickets = get_tickets()
    logging.info(f"Retrieved {len(tickets)} tickets")
    ticket_info, unique_contacts = extract_ticket_info(tickets)
    save_tickets_to_file(ticket_info)
    save_contacts_to_file(unique_contacts)

if __name__ == "__main__":
    main()
