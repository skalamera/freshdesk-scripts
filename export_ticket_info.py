import json
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def extract_ticket_info(tickets, contacts):
    # Ensure contacts is a list
    if isinstance(contacts, dict) and 'contacts' in contacts:
        contacts = contacts['contacts']
    
    contact_dict = {contact['id']: contact for contact in contacts if 'id' in contact}

    ticket_info_list = []
    for ticket in tickets:
        ticket_id = ticket.get('ticket_id')
        created_at = ticket.get('created_at')
        contact_details = ticket.get('contact_details', {})
        
        contact_name = contact_details.get('name', 'N/A')
        contact_email = contact_details.get('email', 'N/A')
        
        ticket_info_list.append({
            'Ticket ID': ticket_id,
            'Created Date': created_at,
            'Contact Name': contact_name,
            'Contact Email': contact_email
        })

    return ticket_info_list

def save_to_csv(ticket_info_list, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Ticket ID', 'Created Date', 'Contact Name', 'Contact Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for ticket_info in ticket_info_list:
            writer.writerow(ticket_info)

def main():
    # Load data from JSON files
    logging.info("Loading tickets and contacts from JSON files")
    tickets = load_json('tickets.json')
    contacts = load_json('contacts.json')

    # Extract relevant ticket information
    logging.info("Extracting ticket information")
    ticket_info_list = extract_ticket_info(tickets, contacts)

    # Save to CSV
    logging.info("Saving ticket information to CSV")
    save_to_csv(ticket_info_list, 'ticket_info.csv')
    logging.info("Ticket information saved to ticket_info.csv")

if __name__ == "__main__":
    main()

