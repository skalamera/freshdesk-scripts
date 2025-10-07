"""
Freshdesk Ticket Details Retrieval Script

DESCRIPTION:
This script retrieves detailed information about a specific ticket from Freshdesk.
Freshdesk is a cloud-based customer support platform that helps businesses
manage customer inquiries, support requests, and service tickets through a
unified interface.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Replace TRACKER_ID with the ID of the ticket you want to retrieve
4. Ensure your API key has the necessary permissions for ticket access
5. Run the script: python get_ticket_details.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- TRACKER_ID: The unique identifier of the ticket to retrieve
  (found in the ticket URL or ticket details in Freshdesk)

OUTPUT:
- Complete ticket details in JSON format if successful
- Error message with status code and response if failed

TICKET DATA INCLUDES:
- Basic info: ID, subject, description, status, priority
- Requester info: name, email, contact details
- Assignment info: assigned group, assigned agent
- Timestamps: created, updated, resolved dates
- Custom fields and tags
- Conversation history and notes

ERROR HANDLING:
- Checks HTTP status codes for success/failure
- Displays detailed error messages for troubleshooting
- Handles authentication and permission errors

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that TRACKER_ID is a valid ticket number
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
"""

import requests
import json
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain
TRACKER_ID = 299766  # Replace with the ticket ID you want to retrieve

def get_ticket_details(ticket_id):
    """
    Retrieve detailed information about a specific Freshdesk ticket.

    Args:
        ticket_id (int): The unique identifier of the ticket

    Returns:
        dict or None: Complete ticket data if successful, None if failed
    """
    # Construct the API URL for the specific ticket
    url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}"

    # Make the API request
    response = requests.get(url, auth=(API_KEY, "X"))

    if response.status_code == 200:
        # Success - return the ticket data
        ticket_data = response.json()
        print(f"✓ Successfully retrieved ticket details for ID: {ticket_id}")
        return ticket_data
    else:
        # Error - display detailed error information
        print(f"✗ Failed to fetch ticket details for ID {ticket_id}")
        print(f"  HTTP Status Code: {response.status_code}")
        print(f"  Error Response: {response.text}")
        return None

def display_ticket_summary(ticket_data):
    """
    Display a formatted summary of the ticket information.

    Args:
        ticket_data (dict): The ticket data from the API
    """
    if not ticket_data:
        print("No ticket data to display.")
        return

    print("\n" + "=" * 60)
    print("TICKET SUMMARY")
    print("=" * 60)

    # Basic ticket information
    print(f"Ticket ID: {ticket_data.get('id', 'N/A')}")
    print(f"Subject: {ticket_data.get('subject', 'N/A')}")
    print(f"Status: {ticket_data.get('status', 'N/A')}")
    print(f"Priority: {ticket_data.get('priority', 'N/A')}")
    print(f"Created: {ticket_data.get('created_at', 'N/A')}")
    print(f"Updated: {ticket_data.get('updated_at', 'N/A')}")

    # Requester information
    requester = ticket_data.get('requester', {})
    if requester:
        print(f"Requester: {requester.get('name', 'N/A')} ({requester.get('email', 'N/A')})")

    # Assignment information
    group_id = ticket_data.get('group_id')
    responder_id = ticket_data.get('responder_id')
    print(f"Assigned Group ID: {group_id if group_id else 'Unassigned'}")
    print(f"Assigned Agent ID: {responder_id if responder_id else 'Unassigned'}")

    # Tags
    tags = ticket_data.get('tags', [])
    if tags:
        print(f"Tags: {', '.join(tags)}")

    print("=" * 60)

def main():
    """
    Main function to retrieve and display ticket details.
    """
    print("Freshdesk Ticket Details Retrieval")
    print(f"Retrieving details for ticket ID: {TRACKER_ID}")

    # Retrieve ticket details
    ticket_data = get_ticket_details(TRACKER_ID)

    if ticket_data:
        # Display formatted summary
        display_ticket_summary(ticket_data)

        # Optionally save detailed JSON to file
        save_to_file = input("\nSave detailed JSON to file? (y/n): ").lower().strip()
        if save_to_file == 'y':
            filename = f"ticket_{TRACKER_ID}_details.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Detailed ticket data saved to: {filename}")
    else:
        print("❌ Unable to retrieve ticket details. Please check:")
        print("  - Ticket ID is correct")
        print("  - API key has read permissions")
        print("  - Network connectivity to Freshdesk")

# Run the script if executed directly
if __name__ == "__main__":
    main()

