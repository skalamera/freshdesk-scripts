"""
Freshdesk SLA Policy Matching Script

DESCRIPTION:
This script retrieves all SLA (Service Level Agreement) policies from Freshdesk
and matches them against a specific ticket based on group and ticket type. It
analyzes which SLA policy should be applied to a ticket and provides detailed
information about the matching process.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- Valid Freshdesk API key with SLA policy and ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update the ticket data in the main() function with your test ticket
4. Ensure your API key has permissions for SLA policy and ticket access
5. Run the script: python match_sla_policy.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- SLA Policies API: https://developers.freshdesk.com/api/#sla_policies
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_DATA: Test ticket with group_id, type, priority, and due_by

OUTPUT:
- Console output showing SLA policy matching results
- Log file with detailed operation information
- Analysis of which SLA policy should apply to the ticket

SLA POLICY MATCHING:
- Matches tickets to SLA policies based on group_id and ticket type
- Checks if ticket.group_id is in policy.applicable_to.group_ids
- Checks if ticket.type is in policy.applicable_to.ticket_types
- Returns the first matching policy found

ERROR HANDLING:
- Handles HTTP 404 (policies/tickets not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has SLA policy and ticket read permissions
- Check that the ticket and SLA policies exist
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Test SLA policy application for specific tickets
- Debug SLA policy configuration issues
- Analyze which policies apply to different ticket types
- Validate SLA policy setup and configuration
"""

import requests
import json
import time
import logging
import pandas as pd

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2'
HEADERS = {'Content-Type': 'application/json'}

# Logging setup
logging.basicConfig(filename='sla_policies.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_sla_policies():
    endpoint = f'{BASE_URL}/sla_policies'
    sla_policies = []
    page = 1
    while True:
        response = requests.get(endpoint, headers=HEADERS, auth=(API_KEY, 'X'), params={'page': page})
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            sla_policies.extend(data)
            page += 1
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logging.warning(f'Rate limit exceeded. Retrying after {retry_after} seconds...')
            time.sleep(retry_after)
        else:
            logging.error(f'Failed to fetch SLA policies. Status code: {response.status_code}, Response: {response.text}')
            break
    return sla_policies

def match_sla_policy(ticket, sla_policies):
    for policy in sla_policies:
        if ticket['group_id'] in policy['applicable_to']['group_ids'] and ticket['type'] in policy['applicable_to']['ticket_types']:
            return policy
    return None

def main(ticket):
    sla_policies = get_sla_policies()
    matched_policy = match_sla_policy(ticket, sla_policies)
    
    if matched_policy:
        logging.info(f"Matched SLA Policy: {matched_policy['name']}")
        print(f"Matched SLA Policy: {matched_policy['name']}")
    else:
        logging.info("No matching SLA policy found.")
        print("No matching SLA policy found.")

if __name__ == '__main__':
    ticket = {
        "id": 250128,
        "type": "Incident",
        "group_id": 67000578163,
        "priority": 3,
        "due_by": "2024-07-12T13:33:29Z"
    }
    main(ticket)

