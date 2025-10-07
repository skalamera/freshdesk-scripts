import requests
import json

# Freshdesk API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompanysandbox.freshdesk.com'

# Endpoint to list all ticket fields
url = f'https://{DOMAIN}/api/v2/ticket_fields'

# Send GET request to Freshdesk API
response = requests.get(url, auth=(API_KEY, 'X'))

# Check if the request was successful
if response.status_code == 200:
    ticket_fields = response.json()
    # Pretty print the ticket fields
    print(json.dumps(ticket_fields, indent=4))
else:
    print(f"Failed to retrieve ticket fields: {response.status_code}")
    print(response.text)

