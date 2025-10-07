"""
Freshdesk Subscription Fulfillment Test Ticket Script

DESCRIPTION:
This script creates a single test ticket for subscription fulfillment testing
purposes. It creates a ticket with a specific format for item quantities and
tracking codes commonly used in subscription management workflows.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket creation permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_data with your desired subject, description, and email
4. Ensure your API key has permissions for ticket creation
5. Run the script: python test_sub_ticket_creation.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#create_ticket
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- ticket_data: Ticket configuration with subject, description, priority, etc.

OUTPUT:
- Creates a single test ticket with subscription fulfillment details
- Console output showing creation results
- Detailed response information if successful

TICKET CREATION PROCESS:
- Creates ticket with priority 1 (Low) and status 2 (Open)
- Uses specific format for item quantities (I:X159685 Q:1, etc.)
- Assigns to specified email address as requester
- Includes rate limit handling with retry logic

ERROR HANDLING:
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and connection errors
- Validates API responses and displays error details

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Retries failed requests with exponential backoff

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket creation permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Check that requester email is valid
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Create test tickets for subscription workflow testing
- Generate sample data for training and demonstration
- Test automation workflows with specific ticket formats
- Validate ticket creation processes and permissions
"""

import requests
import json
import time

# Your Freshdesk credentials and domain
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# Freshdesk API URL for ticket creation
url = f"https://{DOMAIN}/api/v2/tickets"

# Ticket details
ticket_data = {
    "email": "skalamera@gmail.com",
    "subject": "Subscription Fulfillment",
    "priority": 1,
    "description": "I:X159685 Q:1, I:X104568 Q:2, I:X158687 Q:3, I:8563586 Q:4",
    "status": 2  # Open status
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Function to handle rate limits and retry
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False

# Function to create ticket
def create_ticket():
    while True:
        try:
            # Make the request to Freshdesk API
            response = requests.post(url, auth=(API_KEY, "X"), headers=headers, data=json.dumps(ticket_data))

            # Check for rate limit and retry if necessary
            if handle_rate_limit(response):
                continue

            # Check if the request was successful
            if response.status_code == 201:
                print("Ticket created successfully!")
                print("Ticket details:", response.json())
                break
            else:
                print(f"Failed to create ticket. Status Code: {response.status_code}, Response: {response.text}")
                break

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

# Run the function
create_ticket()

