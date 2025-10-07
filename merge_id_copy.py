import requests
import re
import logging
import pandas as pd
import time
from collections import defaultdict

# Freshdesk credentials and domain
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# Freshdesk API URL and headers
headers = {
    "Content-Type": "application/json"
}

STATUS_MAPPING = {
    2: 'Open',
    3: 'Pending',
    4: 'Resolved',
    5: 'Closed'
}

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to extract merged ticket IDs from the conversation body
def extract_merged_ticket_ids(conversation_body):
    merged_ticket_ids = re.findall(r'https:\/\/benchmarkeducationcompany\.freshdesk\.com\/a\/tickets\/(\d+)', conversation_body)
    return merged_ticket_ids

# Function to get all conversations for a given ticket ID
def get_conversations_for_ticket(ticket_id):
    conversations_url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}/conversations"
    response = requests.get(conversations_url, auth=(API_KEY, 'X'), headers=headers)

    if response.status_code == 200:
        conversations = response.json()
        merged_ticket_ids = []

        for conversation in conversations:
            merged_ticket_ids.extend(extract_merged_ticket_ids(conversation['body']))

        return list(set(merged_ticket_ids))  # Return unique ticket IDs
    else:
        logging.error(f"Failed to retrieve conversations for ticket {ticket_id}: {response.status_code} - {response.text}")
        return []

# Function to get details of a specific ticket including subject and tags
def get_ticket_details(ticket_id):
    ticket_url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}"
    response = requests.get(ticket_url, auth=(API_KEY, 'X'), headers=headers)

    if response.status_code == 200:
        ticket = response.json()
        return {
            'ticket_id': ticket['id'],
            'created_at': ticket['created_at'],
            'status': STATUS_MAPPING.get(ticket['status'], f"Unknown ({ticket['status']})"),
            'subject': ticket.get('subject', 'No Subject'),
            'tags': ', '.join(ticket.get('tags', []))  # Combine tags into a single string
        }
    else:
        logging.error(f"Failed to retrieve details for ticket {ticket_id}: {response.status_code} - {response.text}")
        return None

# Main function to extract merged tickets and save to Excel
def extract_merged_tickets(ticket_ids):
    grouped_tickets = defaultdict(list)
    tickets_data = []

    for ticket_id in ticket_ids:
        merged_tickets = get_conversations_for_ticket(ticket_id)
        if merged_tickets:
            for merged_ticket_id in merged_tickets:
                ticket_details = get_ticket_details(merged_ticket_id)
                if ticket_details:
                    grouped_tickets[ticket_id].append({
                        'ticket_id': ticket_details['ticket_id'],
                        'created_at': ticket_details['created_at'],
                        'status': ticket_details['status'],
                        'subject': ticket_details['subject'],
                        'tags': ticket_details['tags']
                    })
                    
                    # Add data to tickets_data for Excel output
                    tickets_data.append({
                        'Original Ticket ID': ticket_id,
                        'Merged Ticket ID': ticket_details['ticket_id'],
                        'Created At': ticket_details['created_at'],
                        'Status': ticket_details['status'],
                        'Subject': ticket_details['subject'],
                        'Tags': ticket_details['tags']
                    })

        # Add a delay to avoid hitting rate limits
        time.sleep(1)

    # Convert tickets_data to a pandas DataFrame
    df = pd.DataFrame(tickets_data)

    # Save the DataFrame to an Excel file
    output_filename = 'merged_tickets.xlsx'
    df.to_excel(output_filename, index=False)

    print(f"Excel file '{output_filename}' has been generated with the merged ticket details.")


if __name__ == '__main__':
    # List of ticket IDs to process
    ticket_ids = [
280805, 
280859, 
280943, 
281360, 
281736, 
282019, 
282031, 
282048, 
282055, 
282209
    ]

    # Split ticket IDs into batches of manageable size, for example, batches of 100
    batch_size = 100
    for i in range(0, len(ticket_ids), batch_size):
        current_batch = ticket_ids[i:i + batch_size]
        logging.info(f"Processing batch {i // batch_size + 1}: Tickets {current_batch[0]} to {current_batch[-1]}")
        extract_merged_tickets(current_batch)
        # Add a delay between batches if necessary
        time.sleep(5)

