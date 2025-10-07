import requests
import json

# Freshdesk API credentials
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# Endpoint to get the list of agents
url = f'https://{DOMAIN}/api/v2/agents'

# Headers for the API request
headers = {
    'Content-Type': 'application/json'
}

# Pagination variables
page = 1
per_page = 100  # Fetching maximum of 100 agents per page
agents = []

while True:
    params = {
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
        print(f"Failed to fetch agents: {response.status_code} - {response.text}")
        break

    data = response.json()
    if not data:
        break
    
    agents.extend(data)
    
    if len(data) < per_page:
        break
    
    page += 1

# Output the list of agents and their responder IDs
for agent in agents:
    print(f"Name: {agent['contact']['name']}, Responder ID: {agent['id']}")

# If needed, you can save this list to a file
with open('agents_list.txt', 'w', encoding='utf-8') as file:
    for agent in agents:
        file.write(f"Name: {agent['contact']['name']}, Responder ID: {agent['id']}\n")

print("List of agents and their responder IDs has been saved to 'agents_list.txt'")

