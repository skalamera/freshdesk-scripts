import pandas as pd
import requests
import time
from requests.auth import HTTPBasicAuth
import logging

# Constants for Freshdesk API
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
AUTH = HTTPBasicAuth(API_KEY, 'X')

# Input and output file paths
input_file = 'C:/Users/skala/Projects/FD Ticket Updater/delete_contacts.xlsx'
output_file = 'C:/Users/skala/Projects/FD Ticket Updater/output_with_ticket_ids.xlsx'
log_file = 'C:/Users/skala/Projects/FD Ticket Updater/process_log.txt'

# Set up logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the spreadsheet
df = pd.read_excel(input_file)

# Function to get ticket IDs by email
def get_ticket_ids_by_email(email):
    url = f"https://{DOMAIN}/api/v2/tickets"
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'email': email
    }

    while True:
        response = requests.get(url, headers=headers, params=params, auth=AUTH)
        if response.status_code == 200:
            tickets = response.json()
            return [ticket['id'] for ticket in tickets]
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            logging.info(f"Rate limit exceeded for email {email}. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
        else:
            logging.error(f"Failed to get tickets for {email}: {response.status_code}")
            return []

# Prepare the output DataFrame
output_data = []

# Process each email in the spreadsheet
for index, row in df.iterrows():
    email = row.iloc[0]
    if pd.isna(email):
        logging.warning(f"No email provided in row {index + 1}")
        output_data.append([email, 'No email provided'])
        continue
    ticket_ids = get_ticket_ids_by_email(email)
    if ticket_ids:
        logging.info(f"Found {len(ticket_ids)} tickets for email {email}: {ticket_ids}")
    else:
        logging.info(f"No tickets found for email {email}")
    output_data.append([email, ', '.join(map(str, ticket_ids))])

# Create a DataFrame for the output
output_df = pd.DataFrame(output_data, columns=['Email', 'Ticket IDs'])

# Save the output back to the spreadsheet
output_df.to_excel(output_file, index=False)

logging.info(f"Output saved to {output_file}")

print(f"Output saved to {output_file}. Check log file at {log_file} for details.")

