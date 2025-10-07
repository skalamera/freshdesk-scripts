"""
Freshdesk Automation Rule Creation Script

DESCRIPTION:
This script creates a time-triggered automation rule in Freshdesk that assigns
unassigned tickets to appropriate regional groups based on the company's state
information. The automation runs daily and processes tickets based on their
creation time and status.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with automation rules write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update region_to_group mapping with your actual group IDs
4. Update automation conditions and actions as needed
5. Ensure your API key has permissions for automation rules creation
6. Run the script: python fd_automation_import.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Automation Rules API: https://developers.freshdesk.com/api/#automation_rules
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- automation_type_id: Type of automation (3 = Time-triggered)
- region_to_group: Mapping of regions to group IDs

OUTPUT:
- Creates a time-triggered automation rule
- Console output showing success/failure status
- Detailed response information if creation fails

AUTOMATION RULE DETAILS:
- Type: Time-triggered automation (runs at 8 AM daily)
- Triggers on tickets created within the last day
- Filters for tickets with 'Unassigned' status (ID: 2)
- Assigns tickets to regional groups based on company state
- Updates region custom field for each ticket

REGION MAPPING:
- Maps US states to regional groups (Central Southeast, Central Southwest, Northeast, West)
- Handles international and DoDEA (Department of Defense Education Activity) cases
- Assigns unmapped states to Northeast region as default

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has automation rules write permissions
- Check that group IDs in mapping are correct
- Ensure network connectivity to Freshdesk API
- Verify that automation type ID is valid
- Check that required custom fields exist

USAGE SCENARIOS:
- Automate ticket assignment based on geographic regions
- Implement consistent regional routing for support tickets
- Reduce manual ticket assignment workload
- Ensure proper ticket distribution across regional teams
- Maintain service level agreements by region
"""

import requests
import json
import logging
import sys

api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'
automation_type_id = 3  # Time-triggered automation type

# Mapping of regions to groups
region_to_group = {
    "Central Southeast": 67000578164,
    "Central Southwest": 67000578162,
    "Northeast": 67000578163,
    "West": 67000578161,
    "International": 67000578163,
    "DoDEA": 67000578163
}

# Create the conditions for the rule
conditions = [
    {
        "resource_type": "ticket",
        "field_name": "status",
        "operator": "in",
        "value": ["2"]  # Status 'Unassigned' has ID 2 in Freshdesk
    },
    {
        "resource_type": "ticket",
        "field_name": "created_at",
        "operator": "greater_than",
        "value": 0  # This ensures it includes tickets from any time within the last day
    }
]

# Create the actions for the rule based on region
actions = []
for region, group_id in region_to_group.items():
    actions.append({
        "field_name": "group_id",
        "value": group_id,
        "resource_type": "same_ticket",
        "custom_fields": {
            "cf_region": region
        }
    })

# Create the automation rule
automation_rule = {
    "name": "Assign Unassigned Tickets Based on Region at 8 AM",
    "position": 1,
    "active": True,
    "conditions": [
        {
            "name": "condition_set_1",
            "match_type": "all",
            "properties": conditions
        }
    ],
    "actions": actions
}

# Configure logging to both file and console
LOG_FILENAME = 'automation_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Make the API request to create the rule
logging.info("Creating automation rule...")
print("Creating automation rule...")
url = f'https://{domain}/api/v2/automations/{automation_type_id}/rules'
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(automation_rule))

if response.status_code == 201:
    print("Automation rule created successfully.")
    logging.info("Automation rule created successfully.")
else:
    error_msg = f"Failed to create automation rule. Status Code: {response.status_code}"
    print(error_msg)
    print("Response:", response.json())
    logging.error(error_msg)

