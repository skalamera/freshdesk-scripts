import requests
import json

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

# Make the API request to create the rule
url = f'https://{domain}/api/v2/automations/{automation_type_id}/rules'
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(automation_rule))

if response.status_code == 201:
    print("Automation rule created successfully.")
else:
    print("Failed to create automation rule.")
    print("Status Code:", response.status_code)
    print("Response:", response.json())

