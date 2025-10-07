import requests
import json
import time

# Your Freshdesk credentials and domain
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'

# Freshdesk API URL for ticket creation
url = f"https://{DOMAIN}/api/v2/tickets"

# Ticket details
ticket_data = {
    "email": "skalamera@gmail.com",
    "subject": "Subscription Fulfillment",
    "priority": 1,
    "description": "I:X159685 Q:1, I:X104568 Q:2, I:X158687 Q:3, I:8563586 Q:4",
    "status": 2  # Open status
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Function to handle rate limits and retry
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False

# Function to create ticket
def create_ticket():
    while True:
        try:
            # Make the request to Freshdesk API
            response = requests.post(url, auth=(API_KEY, "X"), headers=headers, data=json.dumps(ticket_data))

            # Check for rate limit and retry if necessary
            if handle_rate_limit(response):
                continue

            # Check if the request was successful
            if response.status_code == 201:
                print("Ticket created successfully!")
                print("Ticket details:", response.json())
                break
            else:
                print(f"Failed to create ticket. Status Code: {response.status_code}, Response: {response.text}")
                break

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

# Run the function
create_ticket()

