import requests
import time

# Freshdesk API credentials
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# List of specific ticket IDs to fetch
TICKET_IDS = [
    296989,
]

# Headers for the API request
headers = {
    'Content-Type': 'application/json'
}

# Fetching conversations for each ticket
conversations_url_template = f'https://{DOMAIN}/api/v2/tickets/{{ticket_id}}/conversations'
all_conversations = []

for ticket_id in TICKET_IDS:
    conversations_url = conversations_url_template.format(ticket_id=ticket_id)
    response = requests.get(conversations_url, auth=(API_KEY, 'X'), headers=headers)
    
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        continue
    
    if response.status_code != 200:
        print(f"Failed to fetch conversations for ticket {ticket_id}: {response.status_code} - {response.text}")
        continue
    
    conversations = response.json()
    all_conversations.extend(conversations)

# Output the fetched conversations to a .txt file
with open('specific_conversations.txt', 'w', encoding='utf-8') as file:
    for conv in all_conversations:
        file.write(f"Ticket ID: {conv['ticket_id']}\n")
        file.write(f"Conversation ID: {conv['id']}\n")
        file.write(f"Updated At: {conv['updated_at']}\n")
        file.write(f"Body: {conv['body']}\n")
        file.write("-" * 40 + "\n")

print("Conversations have been saved to 'specific_conversations.txt'")

