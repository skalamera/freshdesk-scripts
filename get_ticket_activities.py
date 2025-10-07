import requests
from datetime import datetime, timedelta, timezone
import time

# Freshdesk API credentials
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# Agent ID
AGENT_ID = 67038975154

# Calculate date range for yesterday
yesterday = datetime.now(timezone.utc) - timedelta(days=1)
start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

# Endpoint for fetching tickets
url = f'https://{DOMAIN}/api/v2/tickets'

# Headers for the API request
headers = {
    'Content-Type': 'application/json'
}

# Pagination variables
page = 1
per_page = 100  # Fetching maximum of 100 tickets per page
tickets = []

# Fetch all tickets updated within the date range
while True:
    params = {
        'updated_since': start_date,
        'page': page,
        'per_page': per_page
    }
    
    response = requests.get(url, auth=(API_KEY, 'X'), headers=headers, params=params)
    
    if response.status_code == 429:
        # Handle rate limit errors
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        continue
    
    if response.status_code != 200:
        print(f"Failed to fetch tickets: {response.status_code} - {response.text}")
        break

    data = response.json()
    if not data:
        break
    
    tickets.extend(data)
    if 'link' not in response.headers or 'rel="next"' not in response.headers['link']:
        break
    
    page += 1

# Filter tickets assigned to the specified agent
filtered_tickets = [ticket for ticket in tickets if ticket['responder_id'] == AGENT_ID]

# Fetching activities for each filtered ticket
activities_url_template = f'https://{DOMAIN}/api/v2/tickets/{{ticket_id}}/activities'
all_activities = []

for ticket in filtered_tickets:
    activities_url = activities_url_template.format(ticket_id=ticket['id'])
    response = requests.get(activities_url, auth=(API_KEY, 'X'), headers=headers)
    
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        continue
    
    if response.status_code != 200:
        print(f"Failed to fetch activities for ticket {ticket['id']}: {response.status_code} - {response.text}")
        continue
    
    activities = response.json()
    
    # Filter activities that occurred within the date range
    filtered_activities = [
        activity for activity in activities 
        if start_date <= activity['created_at'] <= end_date
    ]
    
    all_activities.extend(filtered_activities)

# Output the fetched activities to a .txt file
with open('ticket_activities_yesterday.txt', 'w', encoding='utf-8') as file:
    for activity in all_activities:
        file.write(f"Ticket ID: {activity['ticket_id']}\n")
        file.write(f"Activity ID: {activity['id']}\n")
        file.write(f"Created At: {activity['created_at']}\n")
        file.write(f"Activity Type: {activity['activity_type']}\n")
        file.write(f"Description: {activity['description']}\n")
        file.write("-" * 40 + "\n")

print("Ticket activities have been saved to 'ticket_activities_yesterday.txt'")

