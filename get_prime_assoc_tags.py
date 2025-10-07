import requests
import pandas as pd
import time

# API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
PRIME_ASSOCIATION_URL = f'https://{DOMAIN}/api/v2/tickets/{{}}/prime'
TICKETS_URL = f'https://{DOMAIN}/api/v2/tickets/{{}}'

# Ticket IDs to process
ticket_ids = [242803, 
247584, 
]

# Prepare the output data
output_data = []

# Function to make authenticated requests
def make_request(url):
    response = requests.get(url, auth=(API_KEY, 'X'))
    while response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        response = requests.get(url, auth=(API_KEY, 'X'))
    response.raise_for_status()
    return response.json()

# Process each ticket ID to retrieve prime association ticket ID and tags
for ticket_id in ticket_ids:
    try:
        # Step 1: Get the prime association ticket ID
        prime_response = make_request(PRIME_ASSOCIATION_URL.format(ticket_id))
        prime_ticket_id = prime_response.get("id")

        # Step 2: Get tags for the prime association ticket
        tags = []
        if prime_ticket_id:
            ticket_response = make_request(TICKETS_URL.format(prime_ticket_id))
            tags = [tag for tag in ticket_response.get("tags", []) if tag.startswith("SIM") or tag.startswith("SEDCUST")]
        
        # Step 3: Append data to the output list
        output_data.append({
            "Ticket ID": ticket_id,
            "Prime Association Ticket ID": prime_ticket_id,
            "Tags": ", ".join(tags) if tags else ""
        })

    except requests.RequestException as e:
        print(f"Error processing ticket ID {ticket_id}: {e}")

# Convert data to DataFrame and export to Excel
df = pd.DataFrame(output_data)
output_file = '/mnt/data/freshdesk_prime_tags.xlsx'
df.to_excel(output_file, index=False)

print(f"Data has been saved to {output_file}")

