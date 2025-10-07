import requests
import pandas as pd
import time

# Constants for the Freshdesk API
API_KEY = '5TMgbcZdRFY70hSpEdj'
BASE_URL = 'https://benchmarkeducationcompany.freshdesk.com/api/v2/tickets/'
HEADERS = {
    'Content-Type': 'application/json'
}
MAX_CALLS_PER_MINUTE = 700  # Rate limit per minute

# Initialize requests session
session = requests.Session()
session.auth = (API_KEY, 'X')  # API Key as Basic Auth with any character for password

def fetch_prime_association(ticket_id):
    """Fetch prime association for a given ticket ID."""
    url = f"{BASE_URL}{ticket_id}/prime_association"
    response = session.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit reached, waiting before retrying...")
        time.sleep(60)  # wait 60 seconds if rate-limited
        return fetch_prime_association(ticket_id)
    else:
        print(f"Failed to fetch prime association for ticket ID {ticket_id}: {response.status_code}")
        return {}

def process_prime_associations(ticket_ids):
    """Process each ticket ID, fetching prime associations and storing the results."""
    data = []
    for ticket_id in ticket_ids:
        prime_association = fetch_prime_association(ticket_id)
        if prime_association:
            data.append({
                'Ticket ID': ticket_id,
                'Prime Association': prime_association
            })
            print(f"Processed Ticket ID {ticket_id}: Prime Association - {prime_association}")  # Print each processed ticket
        # Respect rate limits by sleeping for a short duration after each call
        time.sleep(1)  # to avoid hitting rate limits on bulk requests

    return data

def export_prime_associations_to_excel(data, filename="prime_associations_export.xlsx"):
    """Export prime association data to an Excel file."""
    # Convert the 'Prime Association' dictionary data into separate columns in DataFrame
    df = pd.json_normalize(data, sep='_')
    df.to_excel(filename, index=False)
    print(f"Data successfully exported to {filename}")

# Main execution
if __name__ == "__main__":
    # Test ticket IDs
    ticket_ids = [242803, 
247584, 
250875, 
251733, 
251736, 
251739, 
251741, 
252387, 
252388, 
252389, 
252390, 
252391, 
252393, 
252394, 
252395, 
252396, 
252398, 
252599, 
255531, 
255612, 
256482, 
259564, 
274472, 
277628, 
277633, 
282444, 
283577, 
283847, 
284268, 
284281, 
284717, 
284747, 
284870, 
285464, 
285705, 
285727, 
285729, 
285791, 
285873, 
286710, 
286912, 
286924, 
287191, 
287400, 
287937, 
287964, 
288026, 
288599, 
288924, 
288935, 
289552, 
289641, 
289702, 
289843, 
289848, 
289849, 
289860, 
289911, 
290013, 
290015, 
290090, 
290121, 
290164, 
290181, 
292551, 
]
    
    # Fetch prime associations for each ID
    prime_association_data = process_prime_associations(ticket_ids)
    
    # Export the data to an Excel file
    export_prime_associations_to_excel(prime_association_data)

