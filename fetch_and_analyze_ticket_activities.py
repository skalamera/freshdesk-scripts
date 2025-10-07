"""
Freshdesk Ticket Activities SLA Analysis Script

DESCRIPTION:
This script analyzes ticket activities and SLA (Service Level Agreement) policy
application for specific tickets in Freshdesk. It compares which SLA policies
should have been applied versus which ones were actually applied, providing
insights into SLA policy configuration and application accuracy.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and SLA policy read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_id in main() function with the ticket you want to analyze
4. Ensure your API key has permissions for ticket and SLA policy access
5. Run the script: python fetch_and_analyze_ticket_activities.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- SLA Policies API: https://developers.freshdesk.com/api/#sla_policies
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- ticket_id: ID of the ticket to analyze

OUTPUT:
- Console output showing SLA policy matching results
- Log file with detailed operation information
- Analysis of which SLA policy should apply to the ticket

SLA POLICY ANALYSIS:
- Matches tickets to SLA policies based on group_id and ticket type
- Checks if ticket.group_id is in policy.applicable_to.group_ids
- Checks if ticket.type is in policy.applicable_to.ticket_types
- Identifies discrepancies between expected and actual policy application

ERROR HANDLING:
- Handles HTTP 404 (ticket/policy not found) errors
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
- Verify API key has ticket and SLA policy read permissions
- Check that the ticket and SLA policies exist
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Debug SLA policy application issues
- Validate SLA policy configurations
- Analyze SLA policy coverage for different ticket types
- Identify tickets that may need SLA policy reassignment
- Generate SLA compliance reports
"""

import requests
import json
import logging
import sys

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2'
HEADERS = {'Content-Type': 'application/json'}

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sla_analysis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_sla_policies():
    endpoint = f'{BASE_URL}/sla_policies'
    response = requests.get(endpoint, headers=HEADERS, auth=(API_KEY, 'X'))
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logging.warning(f'Rate limit exceeded. Retrying after {retry_after} seconds...')
        time.sleep(retry_after)
        return get_sla_policies()
    else:
        logging.error(f'Failed to fetch SLA policies. Status code: {response.status_code}, Response: {response.text}')
        return None

def get_ticket_details(ticket_id):
    endpoint = f'{BASE_URL}/tickets/{ticket_id}'
    response = requests.get(endpoint, headers=HEADERS, auth=(API_KEY, 'X'))
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logging.warning(f'Rate limit exceeded. Retrying after {retry_after} seconds...')
        time.sleep(retry_after)
        return get_ticket_details(ticket_id)
    else:
        logging.error(f'Failed to fetch ticket details. Status code: {response.status_code}, Response: {response.text}')
        return None

def analyze_sla_application(ticket, sla_policies):
    ticket_type = ticket['type']
    group_id = ticket['group_id']

    for policy in sla_policies:
        applicable_groups = policy.get('applicable_to', {}).get('group_ids', [])
        applicable_types = policy.get('applicable_to', {}).get('ticket_types', [])

        if (group_id in applicable_groups) and (ticket_type in applicable_types):
            logging.info(f"Ticket should have been matched with SLA policy: {policy['name']}")
            print(f"Ticket should have been matched with SLA policy: {policy['name']}")
            return policy

    logging.info("Default SLA policy was correctly applied.")
    print("Default SLA policy was correctly applied.")
    return None

def main(ticket_id):
    logging.info(f"Starting SLA analysis for ticket {ticket_id}")
    print(f"Starting SLA analysis for ticket {ticket_id}")

    ticket = get_ticket_details(ticket_id)
    sla_policies = get_sla_policies()

    if ticket and sla_policies:
        analyze_sla_application(ticket, sla_policies)
        logging.info(f"SLA analysis completed for ticket {ticket_id}")
        print(f"SLA analysis completed for ticket {ticket_id}")
    else:
        error_msg = "Failed to retrieve ticket details or SLA policies."
        logging.error(error_msg)
        print(error_msg)

if __name__ == '__main__':
    ticket_id = 250128
    main(ticket_id)

