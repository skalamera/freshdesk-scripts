import requests
import json

# Freshdesk API details
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# API endpoint
API_URL = f"https://{DOMAIN}/api/v2/contacts"

# HTTP headers for authentication and content type
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {API_KEY}:X'
}

def get_all_contacts():
    """Fetch all contacts from Freshdesk"""
    contacts = []
    page = 1
    while True:
        url = f"{API_URL}?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Error fetching contacts: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        contacts.extend(data)
        page += 1
    return contacts

def delete_contact(contact_id):
    """Delete a contact by ID"""
    delete_url = f"{API_URL}/{contact_id}"
    response = requests.delete(delete_url, headers=HEADERS)
    
    if response.status_code == 204:
        print(f"Contact {contact_id} deleted successfully.")
    else:
        print(f"Failed to delete contact {contact_id}: {response.status_code}")

def filter_and_delete_contacts(contacts):
    """Filter contacts by domain and delete"""
    for contact in contacts:
        email = contact.get('email', '')
        if '@columbusk12.incidentiq.com' in email or '@parkway.incidentiq.com' in email:
            contact_id = contact['id']
            print(f"Deleting contact with email: {email}")
            delete_contact(contact_id)

def main():
    # Step 1: Fetch all contacts
    contacts = get_all_contacts()
    
    if not contacts:
        print("No contacts found.")
        return

    # Step 2: Filter and delete contacts with the specified domains
    filter_and_delete_contacts(contacts)

if __name__ == "__main__":
    main()

