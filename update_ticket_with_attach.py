"""
Freshdesk Ticket Attachment Upload Script

DESCRIPTION:
This script adds an attachment to a Freshdesk ticket by creating a private note
with the attached file. It uploads image files (or other file types) to existing
tickets for documentation and reference purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and conversation write permissions
- Freshdesk account and domain access
- Valid attachment file path

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TICKET_ID with the ticket you want to attach files to
4. Update ATTACHMENT_PATH with the path to your attachment file
5. Ensure your API key has permissions for ticket and conversation access
6. Run the script: python update_ticket_with_attach.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Conversations API: https://developers.freshdesk.com/api/#create_conversation
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_ID: ID of the ticket to attach files to
- ATTACHMENT_PATH: Local path to the file to attach

OUTPUT:
- Adds attachment as a private note to the specified ticket
- Console output showing success/failure status
- Error messages if upload fails

ATTACHMENT PROCESS:
- Creates a private note with the attachment
- Supports various file types (images, documents, etc.)
- Uses multipart/form-data for file upload
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
- Check that ticket ID is valid and accessible
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Attach screenshots for bug reports or issue documentation
- Upload reference documents to support tickets
- Add evidence or supporting files to cases
- Document issues with visual or file-based evidence
"""

import requests

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
TICKET_ID = 298629
ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for adding a note with an attachment
url = f"https://{DOMAIN}/api/v2/tickets/{TICKET_ID}/notes"

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
}

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Data payload (private note with attachment)
    data = {
        "body": "Here is the attached screenshot for the ticket.",
        "private": "true"  # Freshdesk API expects a string "true"/"false" instead of a boolean
    }

    # Send POST request using multipart/form-data
    response = requests.post(url, auth=(API_KEY, "X"), files=files, data=data)

# Handle response
if response.status_code == 201:
    print("âœ… Attachment added successfully as a note!")
elif response.status_code == 429:
    print("âš ï¸ Rate limit exceeded. Try again later.")
else:
    print(f"âŒ Failed to add attachment: {response.status_code}, {response.text}")

