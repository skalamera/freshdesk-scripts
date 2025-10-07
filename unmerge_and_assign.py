import requests
import json
import logging

# Setup logging configuration to print to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Freshdesk credentials
api_key = "5TMgbcZdRFY70hSpEdj"
domain = "benchmarkeducationcompany.freshdesk.com"

# Group ID mapping based on regions
group_mapping = {
    "West": 67000578161,
    "Northeast": 67000578163,
    "Central Southwest": 67000578162,
    "Central Southeast": 67000578164,
    "Triage": 67000578235  # Add the Triage group here for fallback
}

# State to Region mapping (as per images)
state_to_region = {
    # West
    "CA": "West", "CO": "West", "ID": "West", "MT": "West", "NV": "West", "OR": "West",
    "UT": "West", "WA": "West", "WY": "West", "AZ": "West",
    # Central Southeast
    "AL": "Central Southeast", "FL": "Central Southeast", "GA": "Central Southeast", "IL": "Central Southeast",
    "IN": "Central Southeast", "KY": "Central Southeast", "MI": "Central Southeast", "MN": "Central Southeast",
    "ND": "Central Southeast", "OH": "Central Southeast", "SC": "Central Southeast", "SD": "Central Southeast",
    "TN": "Central Southeast", "WI": "Central Southeast",
    # Northeast
    "CT": "Northeast", "DC": "Northeast", "DE": "Northeast", "MA": "Northeast", "MD": "Northeast", 
    "ME": "Northeast", "NC": "Northeast", "NH": "Northeast", "NJ": "Northeast", "NY": "Northeast",
    "PA": "Northeast", "RI": "Northeast", "VA": "Northeast", "VT": "Northeast", "WV": "Northeast",
    # Central Southwest
    "AK": "Central Southwest", "AR": "Central Southwest", "HI": "Central Southwest", "IA": "Central Southwest",
    "KS": "Central Southwest", "LA": "Central Southwest", "MO": "Central Southwest", "MS": "Central Southwest",
    "NM": "Central Southwest", "OK": "Central Southwest", "TX": "Central Southwest", "NE": "Central Southwest"
}

# Function to assign a ticket to a group and set status to 'Open'
def assign_ticket_to_region(ticket_id):
    logging.info(f"Processing ticket {ticket_id}")
    
    # Step 1: Fetch ticket details to get the company_id
    ticket_url = f"https://{domain}/api/v2/tickets/{ticket_id}"
    logging.info(f"Fetching ticket details from {ticket_url}")
    response = requests.get(ticket_url, auth=(api_key, "X"))
    
    if response.status_code == 200:
        ticket_data = response.json()
        company_id = ticket_data.get('company_id')
        
        if company_id:
            logging.info(f"Ticket {ticket_id} is associated with company ID {company_id}")
            
            # Step 2: Fetch the company details to get the state
            company_url = f"https://{domain}/api/v2/companies/{company_id}"
            logging.info(f"Fetching company details from {company_url}")
            company_response = requests.get(company_url, auth=(api_key, "X"))
            
            if company_response.status_code == 200:
                company_data = company_response.json()
                company_state = company_data['custom_fields'].get('state')
                logging.info(f"Company {company_id} is in state: {company_state}")
                
                if company_state:
                    # Step 3: Determine the region based on the state
                    region = state_to_region.get(company_state)
                    if region:
                        group_id = group_mapping.get(region)
                        logging.info(f"Assigning ticket {ticket_id} to region '{region}' with group ID {group_id}")
                    else:
                        # If no region mapping, assign to Triage group
                        group_id = group_mapping.get("Triage")
                        logging.warning(f"State '{company_state}' is not mapped to any region. Assigning to Triage group.")
                    
                    # Step 4: Update the ticket's group and set status to 'Open'
                    ticket_update = {
                        "group_id": group_id,
                        "status": 2  # Status 2 corresponds to 'Open'
                    }
                    headers = {"Content-Type": "application/json"}
                    update_response = requests.put(ticket_url, auth=(api_key, "X"), headers=headers, data=json.dumps(ticket_update))
                    
                    if update_response.status_code == 200:
                        logging.info(f"Successfully assigned ticket {ticket_id} to group ID {group_id} with status set to 'Open'")
                    else:
                        logging.error(f"Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
                else:
                    # If company has no state, assign to Triage group and set status to 'Open'
                    group_id = group_mapping.get("Triage")
                    logging.warning(f"Company {company_id} does not have a 'state' field. Assigning ticket {ticket_id} to Triage group.")
                    
                    # Update the ticket's group and set status to 'Open'
                    ticket_update = {
                        "group_id": group_id,
                        "status": 2  # Status 2 corresponds to 'Open'
                    }
                    headers = {"Content-Type": "application/json"}
                    update_response = requests.put(ticket_url, auth=(api_key, "X"), headers=headers, data=json.dumps(ticket_update))
                    
                    if update_response.status_code == 200:
                        logging.info(f"Successfully assigned ticket {ticket_id} to Triage group (Group ID: {group_id}) with status set to 'Open'")
                    else:
                        logging.error(f"Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
            else:
                logging.error(f"Failed to retrieve company {company_id}: {company_response.status_code} - {company_response.text}")
        else:
            # If no company associated with the ticket, assign to Triage group and set status to 'Open'
            group_id = group_mapping.get("Triage")
            logging.warning(f"Ticket {ticket_id} does not have a company associated. Assigning to Triage group.")
            
            # Update the ticket's group and set status to 'Open'
            ticket_update = {
                "group_id": group_id,
                "status": 2  # Status 2 corresponds to 'Open'
            }
            headers = {"Content-Type": "application/json"}
            update_response = requests.put(ticket_url, auth=(api_key, "X"), headers=headers, data=json.dumps(ticket_update))
            
            if update_response.status_code == 200:
                logging.info(f"Successfully assigned ticket {ticket_id} to Triage group (Group ID: {group_id}) with status set to 'Open'")
            else:
                logging.error(f"Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
    else:
        logging.error(f"Failed to retrieve ticket {ticket_id}: {response.status_code} - {response.text}")

# Example: List of ticket IDs to process
tickets = [268490, 
268490, 
268520, 
268518, 
268642, 
268644, 
268972, 
269174, 
269419, 
269821, 
269822, 
270049, 
270299, 
270532, 
270829, 
270875, 
271494, 
271484, 
271480, 
271479, 
271469, 
271456, 
271444, 
272113, 
272875, 
272787, 
272840, 
273209, 
273605, 
274277, 
274201, 
274201, 
274201, 
274411, 
275794, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275613, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275627, 
275658, 
275662, 
276459]

# Process each ticket
for ticket_id in tickets:
    assign_ticket_to_region(ticket_id)

