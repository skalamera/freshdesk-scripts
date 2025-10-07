import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import base64
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f'{API_KEY}:X'.encode()).decode()}"
}

# Get tickets with association type 'tracker' and created in the last 7 days
seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
query = f"(association_type:3 AND created_at:>'{seven_days_ago}')"

logging.debug(f"Original Query: {query}")

encoded_query = urllib.parse.quote(query)
logging.debug(f"Encoded Query: {encoded_query}")

# Use formatted string for URL
search_url = f"{BASE_URL}/search/tickets?query={encoded_query}"
logging.debug(f"Search URL: {search_url}")

response = requests.get(search_url, headers=HEADERS)
logging.debug(f"Response Status Code: {response.status_code}")
logging.debug(f"Response Text: {response.text}")

response.raise_for_status()
tickets = response.json().get('results', [])
logging.info(f"Number of tickets retrieved: {len(tickets)}")

ticket_data = []

for ticket in tickets:
    ticket_id = ticket['id']
    created_date = ticket['created_at']
    company_id = ticket['company_id']
    logging.debug(f"Processing ticket ID: {ticket_id}")

    # Fetch company name
    if company_id:
        logging.debug(f"Fetching company details for company ID: {company_id}")
        company_response = requests.get(f"{BASE_URL}/companies/{company_id}", headers=HEADERS)
        logging.debug(f"Company Response Status Code: {company_response.status_code}")
        logging.debug(f"Company Response Text: {company_response.text}")
        company_response.raise_for_status()
        company_name = company_response.json().get('name', 'N/A')
    else:
        company_name = 'N/A'
    logging.debug(f"Company Name: {company_name}")

    # Fetch associated tickets
    associated_url = f"{BASE_URL}/tickets/{ticket_id}/associated_tickets"
    logging.debug(f"Fetching associated tickets from URL: {associated_url}")
    associated_response = requests.get(associated_url, headers=HEADERS)
    logging.debug(f"Associated Tickets Response Status Code: {associated_response.status_code}")
    logging.debug(f"Associated Tickets Response Text: {associated_response.text}")
    associated_response.raise_for_status()
    associated_tickets = associated_response.json().get('tickets', [])

    number_of_associated_tickets = len(associated_tickets)
    logging.debug(f"Number of associated tickets: {number_of_associated_tickets}")

    # Check for VIP tickets
    vip_flag = any('VIP' in associated_ticket['tags'] or associated_ticket['custom_fields'].get('cf_vip', False)
                   for associated_ticket in associated_tickets)
    logging.debug(f"VIP Flag: {vip_flag}")

    ticket_data.append({
        'Ticket ID': ticket_id,
        'Created Date': created_date,
        'Company Name': company_name,
        'Number of Associated Tickets': number_of_associated_tickets,
        'VIP Flag': vip_flag
    })

# Create a DataFrame and export to Excel
df = pd.DataFrame(ticket_data)
output_file = 'tracker_tickets.xlsx'
df.to_excel(output_file, index=False)

logging.info(f"Excel file '{output_file}' has been created successfully.")

