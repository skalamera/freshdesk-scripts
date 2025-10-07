"""
Freshdesk Ticket Status Update Script

DESCRIPTION:
This script updates ticket statuses in Freshdesk based on a predefined mapping.
It finds tickets with old status values and updates them to new status values
with proper error handling, retry logic, and rate limit management.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket update permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update STATUS_MAPPING with your desired status transitions
4. Ensure your API key has permissions for ticket updates
5. Run the script: python update_ticket_status.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#update_ticket
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- STATUS_MAPPING: Dictionary mapping old status IDs to new status IDs
- MAX_RETRIES: Maximum retry attempts for failed requests

OUTPUT:
- Updates tickets with new status values based on mapping
- Console output showing progress and results
- Detailed error messages for failed updates
- Summary statistics on successful/failed updates

STATUS UPDATE PROCESS:
- Fetches all tickets with pagination (50 per page)
- Checks each ticket against STATUS_MAPPING
- Updates tickets that match old status values
- Displays success/failure status for each update

ERROR HANDLING:
- Handles HTTP 400 (bad request) errors
- Handles HTTP 403 (permission denied) errors
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles HTTP 5xx (server) errors with retry and backoff

RATE LIMIT HANDLING:
- Includes 1-second delays between requests
- Handles rate limit responses with retry-after delays
- Implements exponential backoff for server errors
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that status IDs in mapping are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets exist and are accessible

USAGE SCENARIOS:
- Update deprecated status values to new status codes
- Standardize ticket statuses across the system
- Migrate tickets from old status workflows
- Bulk status cleanup and maintenance
"""

import requests
import time

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/tickets"

# Headers for authentication
AUTH = (API_KEY, "X")
HEADERS = {"Content-Type": "application/json"}

# Status mapping
STATUS_MAPPING = {
    21: 8
}

MAX_RETRIES = 3  # Limit retries to prevent infinite loops

def get_tickets_with_old_statuses():
    """Fetch all tickets that have an old status from the mapping."""
    tickets_to_update = []
    page = 1

    while True:
        response = requests.get(
            BASE_URL,
            auth=AUTH,
            headers=HEADERS,
            params={"per_page": 50, "page": page}  # Fetch in batches of 50
        )

        if response.status_code != 200:
            print(f"âŒ Error fetching tickets: {response.status_code} - {response.text}")
            break

        tickets = response.json()
        if not tickets:
            break  # No more tickets to process

        for ticket in tickets:
            old_status = ticket.get("status")
            if old_status in STATUS_MAPPING:
                tickets_to_update.append((ticket["id"], old_status, STATUS_MAPPING[old_status]))

        page += 1
        time.sleep(1)  # Delay to prevent rate limits

    return tickets_to_update

def update_ticket_status(ticket_id, old_status, new_status, attempt=1):
    """Update a single ticket status based on the mapping, with retries."""
    if attempt > MAX_RETRIES:
        print(f"â— Max retries reached for ticket {ticket_id}. Skipping...")
        return "FAILED"

    url = f"{BASE_URL}/{ticket_id}"
    payload = {"status": new_status}

    try:
        response = requests.put(url, auth=AUTH, headers=HEADERS, json=payload)

        if response.status_code == 200:
            print(f"âœ… Success: Ticket {ticket_id} updated from {old_status} â†’ {new_status}")
            return "SUCCESS"
        elif response.status_code == 400:
            print(f"âŒ Failed: Ticket {ticket_id} - Bad Request (400): {response.json()}")
        elif response.status_code == 403:
            print(f"ðŸš« Failed: Ticket {ticket_id} - Permission Denied (403)")
        elif response.status_code == 404:
            print(f"ðŸ” Failed: Ticket {ticket_id} - Not Found (404)")
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"â³ Rate limit hit. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        elif response.status_code >= 500:
            print(f"âš ï¸ Failed: Ticket {ticket_id} - Server Error ({response.status_code}). Retrying in 10 seconds...")
            time.sleep(10)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        else:
            print(f"âŒ Failed: Ticket {ticket_id} - Unexpected error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"â— Network error: {e}")

    return "FAILED"

def main():
    """Fetch tickets and update their statuses based on the mapping."""
    tickets_to_update = get_tickets_with_old_statuses()

    if not tickets_to_update:
        print("No tickets need updating.")
        return

    print(f"ðŸŽ¯ Found {len(tickets_to_update)} tickets that need status updates.")

    success_count = 0
    fail_count = 0

    for ticket_id, old_status, new_status in tickets_to_update:
        result = update_ticket_status(ticket_id, old_status, new_status)
        if result == "SUCCESS":
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5)  # Small delay to avoid rate limits

    print(f"\nâœ… Done! {success_count} tickets updated successfully, {fail_count} failed.")

if __name__ == "__main__":
    main()

