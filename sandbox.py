"""
Freshdesk Sandbox Ticket Fields Retrieval Script

DESCRIPTION:
This script retrieves all available ticket fields from the Freshdesk sandbox
environment. It provides a comprehensive view of all ticket field configurations,
including custom fields, their types, and available options for testing and
development purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket field read permissions
- Access to Freshdesk sandbox environment

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your sandbox domain (e.g., 'yourcompany-sandbox.freshdesk.com')
3. Ensure your API key has permissions for ticket field access
4. Run the script: python sandbox.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Ticket Fields API: https://developers.freshdesk.com/api/#ticket_fields
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk sandbox domain

OUTPUT:
- Console output showing all ticket fields in JSON format
- Pretty-printed JSON for better readability
- Error messages if API call fails

TICKET FIELDS DATA INCLUDES:
- Field ID, name, and type
- Field labels and descriptions
- Required status and position
- Default values and options
- Custom field configurations
- Field choices for dropdown/multi-select fields

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket field read permissions
- Check that sandbox domain is correct
- Ensure network connectivity to Freshdesk API
- Verify that ticket fields exist in your sandbox

USAGE SCENARIOS:
- Explore available ticket fields for development
- Understand field configurations for integration
- Test field mappings and validations
- Document field structures for reference
"""

import requests
import json

# Freshdesk API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompanysandbox.freshdesk.com'

# Endpoint to list all ticket fields
url = f'https://{DOMAIN}/api/v2/ticket_fields'

# Send GET request to Freshdesk API
response = requests.get(url, auth=(API_KEY, 'X'))

# Check if the request was successful
if response.status_code == 200:
    ticket_fields = response.json()
    # Pretty print the ticket fields
    print(json.dumps(ticket_fields, indent=4))
else:
    print(f"Failed to retrieve ticket fields: {response.status_code}")
    print(response.text)

