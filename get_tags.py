import requests
import time

# Freshdesk API credentials
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/tickets/"

# List of ticket IDs
ticket_ids = [
    243190, 244272, 259594, 270008, 275282, 273468, 270285, 282900, 283045,
    283571, 284334, 284474, 284774, 284984, 285309, 285358, 285657, 285604,
    286194, 286658, 285898, 285178, 286344, 286549, 286691, 287080, 286936,
    286779, 287288, 287316, 287215, 287299, 287238, 287235, 287276, 287692,
    287404, 287535, 274595
]

# Function to fetch and filter tags for a ticket
def get_filtered_ticket_tags(ticket_id):
    url = f"{BASE_URL}{ticket_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, auth=(API_KEY, "X"), headers=headers)

    if response.status_code == 200:
        ticket_data = response.json()
        # Filter tags that start with 'SIM' or 'SEDCUST'
        tags = [tag for tag in ticket_data.get("tags", []) if tag.startswith("SIM") or tag.startswith("SEDCUST")]
        return tags
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # Default to 1 second if not provided
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return get_filtered_ticket_tags(ticket_id)  # Retry the same ticket
    elif response.status_code == 404:
        return f"Ticket ID {ticket_id} not found."
    else:
        return f"Error {response.status_code}: {response.text}"

# Main script
if __name__ == "__main__":
    for ticket_id in ticket_ids:
        filtered_tags = get_filtered_ticket_tags(ticket_id)
        print(f"Ticket ID {ticket_id} Tags: {filtered_tags}")

