import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
API_URL = f"https://{DOMAIN}/api/v2/tickets"

# Headers for authentication
HEADERS = {
    "Content-Type": "application/json"
}

# List of ticket IDs
ticket_ids = [
    292584, 292599, 294867, 294931, 294934, 295987, 297199, 297302, 297903, 298495,
    298514, 298681, 299126, 299921, 294741, 295051, 297006, 294032, 294298, 295213,
    297286, 297988, 294145, 294302, 295478, 295740, 296020, 296247, 297695, 298415,
    298575, 293115, 294340, 295541, 296529, 296964, 297102, 298239, 298479, 298502,
    298951, 297907, 295037, 295053, 296045, 297278, 293650, 294805, 296043, 292670,
    294201, 294967, 295184, 294792, 293707, 296573, 296806, 297227, 297487, 293588,
    295979, 296422, 298171, 293839, 294441, 294618, 295397, 296436, 297201, 297725,
    297862, 297948, 298116, 298179, 299217, 294538, 294099, 296638, 296764, 297311,
    297315, 297393, 297512, 297612, 294438, 294725, 295505, 293406, 294264, 299218
]

def update_ticket_tags(ticket_id):
    """Function to add 'qa' tag to a given ticket."""
    try:
        # Fetch existing ticket details
        response = requests.get(f"{API_URL}/{ticket_id}", auth=(API_KEY, "X"), headers=HEADERS)
        
        if response.status_code == 200:
            ticket_data = response.json()
            existing_tags = ticket_data.get("tags", [])

            # If 'qa' tag is already present, skip updating
            if "qa" in existing_tags:
                logging.info(f"Ticket {ticket_id} already has 'qa' tag. Skipping.")
                return
            
            # Add 'qa' tag
            updated_tags = list(set(existing_tags + ["qa"]))
            payload = {"tags": updated_tags}

            # Update ticket with new tags
            update_response = requests.put(f"{API_URL}/{ticket_id}", auth=(API_KEY, "X"), json=payload, headers=HEADERS)

            if update_response.status_code == 200:
                logging.info(f"Successfully added 'qa' tag to ticket {ticket_id}")
            else:
                logging.error(f"Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")

        elif response.status_code == 404:
            logging.warning(f"Ticket {ticket_id} not found.")
        else:
            logging.error(f"Error fetching ticket {ticket_id}: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for ticket {ticket_id}: {str(e)}")

def main():
    """Main function to process ticket updates with rate-limit handling."""
    for index, ticket_id in enumerate(ticket_ids, start=1):
        update_ticket_tags(ticket_id)

        # Handle rate limits: Max 700 API calls per minute, so wait every 50 requests
        if index % 50 == 0:
            logging.info("Pausing for rate limit...")
            time.sleep(10)

if __name__ == "__main__":
    main()

