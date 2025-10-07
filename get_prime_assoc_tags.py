"""
Freshdesk Prime Association Tags Retrieval Script

DESCRIPTION:
This script retrieves prime association information and tags for specific tickets
in Freshdesk. It fetches prime association ticket IDs and then retrieves tags
from those tickets, filtering for tags that start with 'SIM' or 'SEDCUST' for
analysis and reporting purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to analyze
4. Ensure your API key has permissions for ticket access
5. Run the script: python get_prime_assoc_tags.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Prime Association API: https://developers.freshdesk.com/api/#prime_association
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- ticket_ids: List of ticket IDs to process
- output_file: Excel file for results (default shown)

OUTPUT:
- Excel file with prime association and tag information
- Console output showing processing progress
- Detailed error messages for failed lookups

PRIME ASSOCIATION PROCESS:
- Fetches prime association ticket ID for each input ticket
- Retrieves tags from prime association tickets
- Filters tags that start with 'SIM' or 'SEDCUST'
- Exports results to Excel for analysis

TAG FILTERING:
- Only includes tags starting with 'SIM' (e.g., 'SIM-123', 'SIM-TEST')
- Only includes tags starting with 'SEDCUST' (e.g., 'SEDCUST-456', 'SEDCUST-PROD')
- Filters out all other tags for cleaner analysis

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that ticket IDs are valid
- Ensure network connectivity to Freshdesk API
- Check that prime associations exist for tickets
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Analyze ticket categorization and tagging patterns
- Identify tickets with specific SIM or SEDCUST tags
- Generate reports for management review
- Validate ticket tagging consistency
- Support workflow analysis and optimization
"""

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

