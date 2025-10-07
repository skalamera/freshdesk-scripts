import requests
import pandas as pd
import time
import logging
import base64

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2/contacts'

# Encode API key in Base64
encoded_api_key = base64.b64encode(f'{API_KEY}:X'.encode('utf-8')).decode('utf-8')
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_api_key}'
}

# Setup logging
logging.basicConfig(level=logging.INFO, filename='delete_contacts.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load email addresses from Excel file
file_path = 'delete_contacts.xlsx'  # Update this if the file is located elsewhere
emails_df = pd.read_excel(file_path)
email_addresses = emails_df['Email'].tolist()

def get_contact_id(email):
    """Get the contact ID using the email address."""
    response = requests.get(BASE_URL, headers=HEADERS, params={'email': email})
    if response.status_code == 200:
        contacts = response.json()
        if contacts:
            return contacts[0]['id']
    elif response.status_code == 429:
        logging.warning('Rate limit exceeded. Waiting for a minute...')
        time.sleep(60)
        return get_contact_id(email)
    else:
        logging.error(f"Failed to fetch contact ID for email {email}: {response.status_code} {response.text}")
    return None

def delete_contact(contact_id):
    """Hard delete the contact permanently using the contact ID."""
    response = requests.delete(f"{BASE_URL}/{contact_id}/hard_delete?force=true", headers=HEADERS)
    if response.status_code == 204:
        logging.info(f"Successfully deleted contact ID {contact_id}")
    elif response.status_code == 429:
        logging.warning('Rate limit exceeded. Waiting for a minute...')
        time.sleep(60)
        delete_contact(contact_id)
    else:
        logging.error(f"Failed to delete contact ID {contact_id}: {response.status_code} {response.text}")

def main():
    for email in email_addresses:
        contact_id = get_contact_id(email)
        if contact_id:
            delete_contact(contact_id)
        else:
            logging.warning(f"No contact found for email {email}")

if __name__ == "__main__":
    main()

