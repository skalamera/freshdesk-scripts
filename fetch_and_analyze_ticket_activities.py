import requests
import json
import logging

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2'
HEADERS = {'Content-Type': 'application/json'}

# Logging setup
logging.basicConfig(filename='sla_analysis.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    ticket = get_ticket_details(ticket_id)
    sla_policies = get_sla_policies()

    if ticket and sla_policies:
        analyze_sla_application(ticket, sla_policies)
    else:
        logging.error("Failed to retrieve ticket details or SLA policies.")

if __name__ == '__main__':
    ticket_id = 250128
    main(ticket_id)

