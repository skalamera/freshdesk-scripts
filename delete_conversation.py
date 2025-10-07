"""
Freshdesk Conversation Deletion Script

DESCRIPTION:
This script deletes all conversations (notes and replies) associated with a
specific ticket in Freshdesk. It handles rate limiting, retries failed requests,
and provides comprehensive logging for audit trails and troubleshooting.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with conversation deletion permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_id with the ticket ID whose conversations you want to delete
4. Ensure your API key has permissions for conversation deletion
5. Run the script: python delete_conversation.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Conversations API: https://developers.freshdesk.com/api/#conversations
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- ticket_id: ID of the ticket whose conversations will be deleted
- log_file: Name of the log file for operation tracking

OUTPUT:
- Deletes all conversations for the specified ticket
- Creates detailed log file with operation results
- Console output showing progress and results
- No file output - results displayed in console and log file

CONVERSATION DELETION PROCESS:
- Fetches all conversations for the specified ticket
- Deletes each conversation individually
- Handles pagination if ticket has many conversations
- Includes delays between deletion requests to avoid rate limits

ERROR HANDLING:
- Handles HTTP 403 (permission denied) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles HTTP 5xx (server) errors with retry and backoff
- Validates API responses and displays error details
- Continues processing even if individual conversations fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Includes 1-second delays between deletion requests
- Monitors API usage to avoid exceeding limits

LOGGING:
- Creates detailed log file with timestamps
- Logs to both file and console simultaneously
- Tracks successful deletions and failures
- Includes retry attempts and error details

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has conversation deletion permissions
- Check that ticket ID is valid and accessible
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Remove sensitive information from ticket conversations
- Clean up test data or spam conversations
- Prepare tickets for data migration or archiving
- Remove inappropriate or confidential content
- Audit trail maintenance and compliance
"""

import requests
import base64
import time
import logging
import sys

# Set up logging to both file and console
log_file = 'delete_conversations_log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Freshdesk API credentials
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'
ticket_id = 259708  # The ticket ID for which to delete all conversations

# Encode API Key
encoded_api_key = base64.b64encode(f"{api_key}:X".encode("utf-8")).decode("utf-8")

# Base URL for the Freshdesk API
base_url = f"https://{domain}/api/v2"

# Headers for the API requests
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_api_key}'
}

def get_conversations(ticket_id):
    """Fetch all conversations for the given ticket ID."""
    conversations_url = f"{base_url}/tickets/{ticket_id}/conversations"
    response = requests.get(conversations_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to retrieve conversations for ticket {ticket_id}: {response.status_code}")
        return []

def delete_conversation(conversation_id):
    """Attempt to delete a conversation and return success or failure."""
    delete_url = f"{base_url}/conversations/{conversation_id}"
    delete_response = requests.delete(delete_url, headers=headers)

    if delete_response.status_code == 204:
        logging.info(f"Conversation {conversation_id} deleted successfully.")
        return True
    elif delete_response.status_code == 403:
        logging.warning(f"Failed to delete conversation {conversation_id}: 403 Forbidden - Check permissions.")
        return False
    elif delete_response.status_code in [429, 500, 503]:
        retry_after = int(delete_response.headers.get('Retry-After', 5))
        logging.warning(f"Rate limit or server error encountered. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return delete_conversation(conversation_id)
    else:
        logging.error(f"Failed to delete conversation {conversation_id}: {delete_response.status_code}")
        return False

def delete_all_conversations(ticket_id):
    """Delete all conversations for a given ticket, retrying if necessary."""
    logging.info(f"Starting deletion of all conversations for ticket {ticket_id}")
    print(f"Starting deletion of all conversations for ticket {ticket_id}")

    while True:
        conversations = get_conversations(ticket_id)
        if not conversations:
            logging.info("No more conversations left to delete or failed to retrieve conversations.")
            print("No more conversations left to delete or failed to retrieve conversations.")
            break

        for conversation in conversations:
            conversation_id = conversation['id']
            delete_conversation(conversation_id)
            time.sleep(1)  # Add a short delay to avoid overwhelming the API

        logging.info("Finished a pass over the conversations. Checking for any remaining...")
        print("Finished a pass over the conversations. Checking for any remaining...")

    logging.info(f"Conversation deletion completed for ticket {ticket_id}")
    print(f"Conversation deletion completed for ticket {ticket_id}")

delete_all_conversations(ticket_id)

<<<<<<< Current (Your changes)
delete_all_conversations(ticket_id)

=======
>>>>>>> Incoming (Background Agent changes)
