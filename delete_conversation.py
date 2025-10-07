import requests
import base64
import time
import logging

# Set up logging
log_file = 'delete_conversations_log.txt'
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

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
    while True:
        conversations = get_conversations(ticket_id)
        if not conversations:
            logging.info("No more conversations left to delete or failed to retrieve conversations.")
            break

        for conversation in conversations:
            conversation_id = conversation['id']
            delete_conversation(conversation_id)
            time.sleep(1)  # Add a short delay to avoid overwhelming the API

        logging.info("Finished a pass over the conversations. Checking for any remaining...")

delete_all_conversations(ticket_id)

