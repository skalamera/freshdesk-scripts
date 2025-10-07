import requests
import logging

# Setup logging configuration to print to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Freshdesk credentials
api_key = "5TMgbcZdRFY70hSpEdj"
domain = "benchmarkeducationcompany.freshdesk.com"

# List of primary ticket IDs
ticket_ids = [
    265148, 265239, 268186, 268479, 268481, 268506, 268506, 268638, 268638, 268953,
    269094, 269401, 269710, 269711, 269969, 270217, 270530, 270727, 270858, 270962,
    270988, 271077, 271077, 271120, 271319, 271320, 272016, 272445, 272700, 272701,
    273202, 273432, 274085, 274197, 274202, 274203, 274220, 275575, 275616, 275617,
    275618, 275619, 275620, 275621, 275622, 275624, 275625, 275628, 275629, 275630,
    275631, 275633, 275634, 275635, 275637, 275638, 275639, 275640, 275641, 275642,
    275643, 275644, 275645, 275646, 275647, 275648, 275650, 275653, 275654, 275655,
    275656, 275656, 275656, 276337
]

# Function to fetch assigned agent, group name, and status for each ticket
def fetch_ticket_details(ticket_id):
    logging.info(f"Fetching details for ticket {ticket_id}")
    
    # Fetch ticket details from Freshdesk API
    ticket_url = f"https://{domain}/api/v2/tickets/{ticket_id}"
    response = requests.get(ticket_url, auth=(api_key, "X"))
    
    if response.status_code == 200:
        ticket_data = response.json()
        
        # Extract assigned agent, group ID, and status
        agent_id = ticket_data.get("responder_id", None)
        group_id = ticket_data.get("group_id", None)
        status = ticket_data.get("status", None)
        
        logging.info(f"Ticket {ticket_id}: Agent ID: {agent_id}, Group ID: {group_id}, Status: {status}")
        
        # Fetch agent details if assigned
        agent_name = "No agent assigned"
        if agent_id:
            agent_url = f"https://{domain}/api/v2/agents/{agent_id}"
            agent_response = requests.get(agent_url, auth=(api_key, "X"))
            if agent_response.status_code == 200:
                agent_data = agent_response.json()
                agent_name = agent_data.get("contact", {}).get("name", "Unknown")
            else:
                logging.error(f"Failed to fetch agent details for ID {agent_id}: {agent_response.status_code}")
        
        # Fetch group name if assigned
        group_name = "No group assigned"
        if group_id:
            group_url = f"https://{domain}/api/v2/groups/{group_id}"
            group_response = requests.get(group_url, auth=(api_key, "X"))
            if group_response.status_code == 200:
                group_data = group_response.json()
                group_name = group_data.get("name", "Unknown Group")
            else:
                logging.error(f"Failed to fetch group details for ID {group_id}: {group_response.status_code}")
        
        # Status interpretation (if required to convert status ID to text)
        status_mapping = {
            2: "Open",
            3: "Pending",
            4: "Resolved",
            5: "Closed"
        }
        status_name = status_mapping.get(status, "Unknown Status")
        
        logging.info(f"Ticket {ticket_id}: Agent: {agent_name}, Group: {group_name}, Status: {status_name}")
        
        return {
            "ticket_id": ticket_id,
            "agent_name": agent_name,
            "group_name": group_name,
            "status_name": status_name
        }
    else:
        logging.error(f"Failed to fetch ticket {ticket_id}: {response.status_code}")
        return {
            "ticket_id": ticket_id,
            "agent_name": "Error fetching ticket",
            "group_name": "Error fetching ticket",
            "status_name": "Error fetching ticket"
        }

# Iterate over all ticket IDs and fetch the details
for ticket_id in ticket_ids:
    ticket_details = fetch_ticket_details(ticket_id)
    logging.info(f"Details for ticket {ticket_id}: {ticket_details}")

