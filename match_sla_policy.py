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

