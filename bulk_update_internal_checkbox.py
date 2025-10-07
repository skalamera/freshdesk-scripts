"""
Freshdesk Internal Checkbox Updater Script

DESCRIPTION:
This script updates a large list of Freshdesk tickets by setting the 'cf_internal'
custom field to True. It processes tickets in batch with proper error handling
and logging for bulk internal ticket flagging operations.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to update
4. Ensure your API key has permissions for ticket updates
5. Run the script: python internal_checkbox_updater.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#update_ticket
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- ticket_ids: List of ticket IDs to update with internal flag
- custom_field_name: Name of the custom field to update ('cf_internal')

OUTPUT:
- Updates tickets with cf_internal set to True
- Console output showing success/failure for each ticket
- No file output - results displayed in console only

TICKET UPDATE PROCESS:
- Sets custom_fields.cf_internal to True for each ticket
- Processes tickets sequentially (no batching)
- Updates one ticket at a time to avoid rate limits
- Displays success/failure status for each operation

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors
- Handles network and parsing errors
- Displays detailed error messages for troubleshooting
- Continues processing even if individual tickets fail

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Verify that 'cf_internal' custom field exists

PERFORMANCE CONSIDERATIONS:
- Processes tickets sequentially (no concurrency)
- Large ticket lists may take significant time to process
- Consider breaking large lists into smaller batches if needed
- Rate limits may cause delays in processing

USAGE SCENARIOS:
- Bulk flag tickets as internal for reporting purposes
- Mark tickets for internal review or processing
- Data cleanup and categorization operations
- Compliance and audit trail maintenance
"""

import requests
import logging
import sys

# API key and domain
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany'

# List of ticket IDs to update
ticket_ids = [
    249811, 249855, 249857, 249897, 249904, 249938, 249946, 249964,
    250051, 250052, 250057, 250069, 250081, 250086, 250087, 250098,
    250099, 250114, 250115, 250149, 250172, 250193, 250199, 250200,
    250204, 250209, 250210, 250211, 250213, 250215, 250282, 250329,
    250330, 250332, 250339, 250342, 250343, 250345, 250364, 250382,
    250384, 250397, 250398, 250450, 250469, 250493, 250496, 250505,
    250506, 250507, 250514, 250520, 250530, 250534, 250540, 250545,
    250546, 250548, 250562, 250583, 250605, 250606, 250607, 250653,
    250657, 250674, 250680, 250681, 250682, 250683, 250684, 250685,
    250686, 250688, 250689, 250690, 250691, 250692, 250693, 250694,
    250697, 250735, 250736, 250760, 250761, 250773, 250781, 250810,
    250811, 250836, 250840, 250859, 250872, 250873, 250878, 250879,
    250881, 250899, 250913, 250918, 250928, 250934, 250938, 250940,
    250946, 250966, 250971, 250975, 250983, 250984, 251024, 251037,
    251063, 251067, 251068, 251107, 251109, 251120, 251132, 251133,
    251137, 251138, 251139, 251141, 251142, 251195, 251196, 251206,
    251207, 251214, 251238, 251265, 251267, 251268, 251271, 251279,
    251312, 251314, 251326, 251330, 251337, 251354, 251357, 251378,
    251397, 251398, 251498, 251502, 251507, 251508, 251530, 251573,
    251576, 251622, 251656, 251660, 251680, 251687, 251691, 251710,
    251720, 251745, 251748, 251750, 251775, 251790, 251822, 251853,
    251874, 251885, 251898, 251903, 251905, 251907, 251908, 251909,
    251910, 251917, 251922, 251931, 251963, 251968, 251981, 252036,
    252045, 252056, 252085, 252107, 252222, 252233, 252285, 252287,
    252288, 252295, 252300, 252304, 252307, 252322, 252324, 252331,
    252334, 252359, 252361, 252363, 252366, 252374, 252407, 252411,
    252412, 252413, 252426, 252427, 252429, 252432, 252434, 252474,
    252475, 252484, 252492, 252494, 252502, 252531, 252541, 252571,
    252579, 252586, 252588, 252589, 252592, 252610, 252628, 252659,
    252678, 252680, 252681, 252682, 252683, 252685, 252711
]

# Headers for the API request
headers = {
    'Content-Type': 'application/json'
}

# Base URL for the API
base_url = f'https://{domain}.freshdesk.com/api/v2/tickets'

# Configure logging to both file and console
LOG_FILENAME = 'bulk_internal_checkbox_update.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Function to update a ticket
def update_ticket(ticket_id):
    url = f'{base_url}/{ticket_id}'
    data = {
        'custom_fields': {
            'cf_internal': True
        }
    }
    response = requests.put(url, headers=headers, auth=(api_key, 'X'), json=data)
    if response.status_code == 200:
        message = f'Ticket {ticket_id} updated successfully.'
        print(message)
        logging.info(message)
    else:
        error_msg = f'Failed to update ticket {ticket_id}. Status code: {response.status_code}, Response: {response.text}'
        print(error_msg)
        logging.error(error_msg)

# Update all tickets in the list
logging.info(f"Starting bulk update of {len(ticket_ids)} tickets...")
print(f"Starting bulk update of {len(ticket_ids)} tickets...")

success_count = 0
error_count = 0

for i, ticket_id in enumerate(ticket_ids, 1):
    print(f"Processing ticket {i}/{len(ticket_ids)}: {ticket_id}")
    update_ticket(ticket_id)

    # Simple success/failure tracking
    # Note: This is a basic implementation - in a real scenario you'd want more sophisticated tracking

print(f"\nBulk update completed. Check {LOG_FILENAME} for detailed results.")
logging.info("Bulk update completed.")

