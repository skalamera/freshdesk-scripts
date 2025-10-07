"""
Freshdesk Ticket with Attachment Creation Script

DESCRIPTION:
This script creates a new tracker ticket in Freshdesk and immediately adds an
attachment to it as a private note. This workflow is useful for creating tickets
with supporting documentation or evidence files from the initial creation.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and conversation write permissions
- Freshdesk account and domain access
- Valid attachment file path

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update RELATED_TICKET_ID with the ticket to link as a related ticket
4. Update ATTACHMENT_PATH with the path to your attachment file
5. Ensure your API key has permissions for ticket and conversation access
6. Run the script: python create_ticket_with_attach.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#create_ticket
- Conversations API: https://developers.freshdesk.com/api/#create_conversation
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- RELATED_TICKET_ID: ID of the ticket to associate with the new tracker
- ATTACHMENT_PATH: Local file path to the attachment file

OUTPUT:
- Creates a new tracker ticket linked to the related ticket
- Adds attachment as a private note to the tracker ticket
- Console output showing success/failure for each step

TICKET CREATION PROCESS:
1. Creates tracker ticket with related_ticket_ids array
2. Retrieves the new ticket ID from the creation response
3. Creates a private note with the attachment file
4. Associates the attachment with the newly created ticket

ATTACHMENT PROCESS:
- Supports various file types (images, documents, etc.)
- Uses multipart/form-data for file upload
- Creates private notes (visible only to agents)
- Validates file exists before attempting upload

ERROR HANDLING:
- Validates attachment file exists before upload
- Handles HTTP 429 (rate limit) errors
- Handles network and file access errors
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and conversation write permissions
- Check that attachment file exists and is readable
- Ensure network connectivity to Freshdesk API
- Check that related ticket ID is valid and accessible
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Create tracker tickets with supporting documentation
- Attach screenshots for bug reports or issue documentation
- Upload reference documents to support tickets
- Document issues with visual or file-based evidence
- Automated evidence collection for incident management
"""

import requests
import json
import logging
import sys

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
RELATED_TICKET_ID = 115423  # The ticket to which the tracker will be linked
ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for creating a new tracker ticket
create_ticket_url = f"https://{DOMAIN}/api/v2/tickets"

# Configure logging to both file and console
LOG_FILENAME = 'ticket_attachment_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
    "Content-Type": "application/json"
}

# Step 1: Create the tracker ticket (without attachment)
logging.info("Step 1: Creating tracker ticket...")
print("Step 1: Creating tracker ticket...")
ticket_payload = {
    "description": "This is a tracker ticket linked to another issue.",
    "subject": "Tracker Ticket for Issue #115423",
    "email": "sskalamera@benchmarkeducation.com",  # Required to create the ticket
    "related_ticket_ids": [RELATED_TICKET_ID],  # Must be an array of integers
    "priority": 1,  # 1 = Low, 2 = Medium, 3 = High, 4 = Urgent
    "status": 2,  # 2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed
    "cc_emails": ["skalamera@gmail.com"]  # Must be an array
}

# Send request to create tracker ticket
create_response = requests.post(create_ticket_url, auth=(API_KEY, "X"), headers=headers, json=ticket_payload)

# Check if ticket creation was successful
if create_response.status_code == 201:
    tracker_ticket = create_response.json()  # Get response as JSON
    tracker_ticket_id = tracker_ticket["id"]  # Extract new ticket ID
    print(f"âœ… Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
    logging.info(f"Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
else:
    error_msg = f"Failed to create tracker ticket: {create_response.status_code}, {create_response.text}"
    print(f"âŒ {error_msg}")
    logging.error(error_msg)
    exit()  # Stop script if creation fails

# Step 2: Update the newly created tracker ticket with the attachment
logging.info("Step 2: Adding attachment to tracker ticket...")
print("Step 2: Adding attachment to tracker ticket...")
update_ticket_url = f"https://{DOMAIN}/api/v2/tickets/{tracker_ticket_id}/notes"

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Payload for adding a private note with the attachment
    update_payload = {
        "body": "Attaching relevant screenshot to the tracker ticket.",
        "private": "true"  # Must be string "true" or "false" when using multipart
    }

    # Send request to update the ticket with the attachment
    update_response = requests.post(update_ticket_url, auth=(API_KEY, "X"), files=files, data=update_payload)

# Check if update was successful
if update_response.status_code == 201:
    print("âœ… Attachment added successfully to the tracker ticket!")
    logging.info("Attachment added successfully to the tracker ticket!")
else:
<<<<<<< Current (Your changes)
    print(f"âŒ Failed to add attachment: {update_response.status_code}, {update_response.text}")
=======
    error_msg = f"Failed to add attachment: {update_response.status_code}, {update_response.text}"
    print(f"âŒ {error_msg}")
    logging.error(error_msg)
>>>>>>> Incoming (Background Agent changes)

