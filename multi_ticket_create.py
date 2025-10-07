import requests
import json
import logging
import time  # Import the time module

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Freshdesk API details
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'

# Endpoint to create a ticket
url = f'https://{domain}/api/v2/tickets'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Define ticket details for both priority levels
tickets_to_create = [
    {"subject": "Trial Fulfillment - Test", "priority": 1},
    {"subject": "Pilot Fulfillment - Test", "priority": 1},
    {"subject": "Distributor Fulfillment - Test", "priority": 1},
    {"subject": "RFP Trial Fulfillment - Test", "priority": 1},
    {"subject": "New Customer Fulfillment", "priority": 1},
    {"subject": "Trial Fulfillment", "priority": 2},
    {"subject": "Pilot Fulfillment", "priority": 2},
    {"subject": "Distributor Fulfillment", "priority": 2},
    {"subject": "RFP Trial Fulfillment", "priority": 2},
    {"subject": "Renewal Fulfillment", "priority": 2}
]

def create_ticket(subject, priority):
    data = {
        "subject": subject,
        "priority": priority,
        "status": 2,  # Adjust the status as necessary
        "description": f"This ticket is for {subject}.",
        "email": "skalamera@gmail.com"  # Requester's email
    }
    
    try:
        response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:
            logger.info(f"Ticket '{subject}' created successfully with ID: {response.json()['id']}")
        else:
            logger.error(f"Failed to create ticket '{subject}': {response.status_code}, {response.text}")
            
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as errh:
        logger.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Oops: Something Else {err}")

if __name__ == "__main__":
    for ticket in tickets_to_create:
        create_ticket(ticket['subject'], ticket['priority'])
        time.sleep(1)  # Optional: Add delay between ticket creations if needed

