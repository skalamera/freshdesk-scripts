"""
Freshdesk Ticket to Tracker Association Script

DESCRIPTION:
This script creates an association between a regular ticket and a tracker ticket
in Freshdesk using the ticket association API. It links tickets for better
organization and tracking of related issues.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket update permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TRACKER_ID and TICKET_ID with the appropriate ticket numbers
4. Ensure your API key has permissions for ticket updates
5. Run the script: python link_to_tracker.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Ticket Associations API: https://developers.freshdesk.com/api/#ticket_associations
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TRACKER_ID: ID of the tracker ticket
- TICKET_ID: ID of the ticket to associate with the tracker
- ASSOCIATION_TYPE: Type of association (3 = tracker relationship)

OUTPUT:
- Associates the specified ticket with the tracker ticket
- Console output showing success/failure status
- Detailed response information if successful

ASSOCIATION PROCESS:
- Uses PUT request to update the tracker ticket
- Sets association_type to 3 (tracker relationship)
- Includes both ticket IDs in related_ticket_ids array
- Creates bidirectional association between tickets

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that both ticket IDs are valid
- Ensure network connectivity to Freshdesk API
- Verify that tickets exist and are accessible

USAGE SCENARIOS:
- Link support tickets to their corresponding tracker tickets
- Organize related tickets for better issue tracking
- Create associations for reporting and analysis
- Maintain ticket relationships for workflow management
"""

import requests
import json
import logging
import sys

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"

# Ticket and tracker IDs
TRACKER_ID = 299766
TICKET_ID = 299585

# API endpoint to update the tracker ticket
url = f"https://{DOMAIN}/api/v2/tickets/{TRACKER_ID}"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Configure logging to both file and console
LOG_FILENAME = 'ticket_tracker_linking.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Data payload to associate both tickets
data = {
    "association_type": 3,  # Ensure the tracker is explicitly defined
    "related_ticket_ids": [TRACKER_ID, TICKET_ID]  # Include both tracker and ticket
}

# Make the request
logging.info("Making API request to link ticket to tracker...")
print("Making API request to link ticket to tracker...")
response = requests.put(
    url,
    auth=(API_KEY, "X"),
    headers=headers,
    data=json.dumps(data)
)

# Output the response
if response.status_code == 200:
    message = "Ticket successfully linked to tracker!"
    print(message)
    print(response.json())
    logging.info(message)
else:
    error_msg = f"Failed to link ticket. Status Code: {response.status_code}"
    print(error_msg)
    print(response.text)
    logging.error(error_msg)

