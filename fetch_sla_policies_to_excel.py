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

def save_to_excel(data, file_name):
    df = pd.json_normalize(data)
    df.to_excel(file_name, index=False)
    logging.info(f'Successfully saved SLA policies to {file_name}')

def main():
    sla_policies = get_sla_policies()
    if sla_policies:
        save_to_excel(sla_policies, 'sla_policies.xlsx')
        logging.info(f'Successfully retrieved and saved {len(sla_policies)} SLA policies.')
    else:
        logging.info('No SLA policies found.')

if __name__ == '__main__':
    main()

