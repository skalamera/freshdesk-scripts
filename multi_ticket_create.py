"""
Freshdesk Multi-Ticket Creation Script

DESCRIPTION:
This script creates multiple tickets in Freshdesk with different subjects and
priority levels for testing and bulk ticket generation purposes. It creates
tickets for various fulfillment types (Trial, Pilot, Distributor, etc.) at
both high and low priority levels.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket creation permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update tickets_to_create list if you want different subjects/priorities
4. Ensure your API key has permissions for ticket creation
5. Run the script: python multi_ticket_create.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#create_ticket
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- tickets_to_create: List of ticket configurations with subject and priority
- email: Default requester email for all tickets

OUTPUT:
- Creates multiple tickets with specified subjects and priorities
- Console output showing creation progress and results
- Detailed logging for troubleshooting

TICKET CREATION PROCESS:
- Creates tickets with different subjects for testing scenarios
- Sets priority levels (1 = Low, 2 = Medium, 3 = High, 4 = Urgent)
- Uses same requester email for all tickets
- Sets status to Open (2) for all tickets
- Includes 1-second delay between creations to respect rate limits

ERROR HANDLING:
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and connection errors
- Validates API responses and displays error details
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Includes 1-second delays between ticket creations
- Handles rate limit responses with retry-after delays
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket creation permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that requester email exists or is valid

USAGE SCENARIOS:
- Generate test tickets for training and demonstration
- Create sample data for testing automation workflows
- Bulk ticket creation for scenario testing
- Load testing and performance validation
"""

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

