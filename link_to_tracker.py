import requests
import json

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"

# Ticket and tracker IDs
TRACKER_ID = 299766
TICKET_ID = 299585

# API endpoint to update the tracker ticket
url = f"https://{DOMAIN}/api/v2/tickets/{TRACKER_ID}"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Data payload to associate both tickets
data = {
    "association_type": 3,  # Ensure the tracker is explicitly defined
    "related_ticket_ids": [TRACKER_ID, TICKET_ID]  # Include both tracker and ticket
}

# Make the request
response = requests.put(
    url,
    auth=(API_KEY, "X"),
    headers=headers,
    data=json.dumps(data)
)

# Output the response
if response.status_code == 200:
    print("Ticket successfully linked to tracker!")
    print(response.json())
else:
    print(f"Failed to link ticket. Status Code: {response.status_code}")
    print(response.text)

