"""
Freshdesk Ticket Tag Filtering Script

DESCRIPTION:
This script retrieves specific tags (SIM and SEDCUST prefixes) for multiple
Freshdesk tickets. It filters ticket tags to show only those starting with
'SIM' or 'SEDCUST', which are commonly used for categorization.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to check
4. Ensure your API key has the necessary permissions for ticket access
5. Run the script: python get_tags.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- ticket_ids: List of ticket IDs to retrieve tags for
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain

OUTPUT:
- Displays filtered tags for each ticket ID
- Shows tags that start with 'SIM' or 'SEDCUST' only
- Handles errors and missing tickets gracefully

TAG FILTERING:
- Only shows tags starting with 'SIM' (e.g., 'SIM-123', 'SIM-TEST')
- Only shows tags starting with 'SEDCUST' (e.g., 'SEDCUST-456', 'SEDCUST-PROD')
- Filters out all other tags for cleaner output

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Retries the same request after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard

PERFORMANCE CONSIDERATIONS:
- Processes tickets sequentially to respect rate limits
- Includes small delays between requests if needed
- Large ticket lists may take significant time to process
"""

import requests
import time
import os
import logging
import sys

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain
BASE_URL = f"https://{DOMAIN}/api/v2/tickets/"

# List of ticket IDs to retrieve filtered tags for
# Replace this list with your actual ticket IDs
ticket_ids = [
    243190, 244272, 259594, 270008, 275282, 273468, 270285, 282900, 283045,
    283571, 284334, 284474, 284774, 284984, 285309, 285358, 285657, 285604,
    286194, 286658, 285898, 285178, 286344, 286549, 286691, 287080, 286936,
    286779, 287288, 287316, 287215, 287299, 287238, 287235, 287276, 287692,
    287404, 287535, 274595
]

# HTTP Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# Configure logging to both file and console
LOG_FILENAME = 'jira_tag_filtering.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_filtered_ticket_tags(ticket_id):
    """
    Retrieve and filter tags for a specific ticket.

    This function fetches all tags for a ticket and filters them to show
    only tags that start with 'SIM' or 'SEDCUST'.

    Args:
        ticket_id (int): The ticket ID to fetch tags for

    Returns:
        list or str: List of filtered tags, or error message if failed

    Note:
        - Only returns tags starting with 'SIM' or 'SEDCUST'
        - Handles rate limiting with automatic retry
        - Returns error messages for troubleshooting
    """
    try:
        # Make API request for ticket details
        response = requests.get(
            f"{BASE_URL}{ticket_id}",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )

        if response.status_code == 200:
            # Success - extract and filter tags
            ticket_data = response.json()
            all_tags = ticket_data.get("tags", [])

            # Filter tags that start with 'SIM' or 'SEDCUST'
            filtered_tags = [
                tag for tag in all_tags
                if tag.startswith("SIM") or tag.startswith("SEDCUST")
            ]

            print(f"✓ Retrieved {len(filtered_tags)} matching tags for ticket {ticket_id}")
            return filtered_tags

        elif response.status_code == 429:
            # Rate limit exceeded - retry after delay
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            return get_filtered_ticket_tags(ticket_id)  # Retry the same ticket

        elif response.status_code == 404:
            error_msg = f"Ticket ID {ticket_id} not found"
            print(f"⚠ {error_msg}")
            return error_msg

        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"✗ {error_msg}")
            return error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"Network error for ticket {ticket_id}: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg

def main():
    """
    Main function to process all tickets and display filtered tags.
    """
    print("Starting ticket tag filtering...")
    print(f"Processing {len(ticket_ids)} tickets...")
    print("=" * 60)
    logging.info("Starting ticket tag filtering...")
    logging.info(f"Processing {len(ticket_ids)} tickets...")

    # Process each ticket
    for i, ticket_id in enumerate(ticket_ids, 1):
        print(f"\nProcessing ticket {i}/{len(ticket_ids)}: ID {ticket_id}")
        logging.info(f"Processing ticket {i}/{len(ticket_ids)}: ID {ticket_id}")

        # Get filtered tags for this ticket
        filtered_tags = get_filtered_ticket_tags(ticket_id)

        # Display results
        if isinstance(filtered_tags, list):
            if filtered_tags:
                message = f"Filtered tags: {', '.join(filtered_tags)}"
                print(f"  {message}")
                logging.info(f"Ticket {ticket_id}: {message}")
            else:
                message = "No matching tags found"
                print(f"  {message}")
                logging.info(f"Ticket {ticket_id}: {message}")
        else:
            error_msg = f"Error: {filtered_tags}"
            print(f"  {error_msg}")
            logging.error(f"Ticket {ticket_id}: {error_msg}")

        # Small delay between requests to be respectful
        time.sleep(0.1)

    print("\n" + "=" * 60)
    print("Tag filtering completed!")
    logging.info("Tag filtering completed!")

    # Summary statistics
    total_tickets = len(ticket_ids)
    tickets_with_tags = sum(1 for ticket_id in ticket_ids
                           if isinstance(get_filtered_ticket_tags(ticket_id), list))
    summary_msg = f"Summary: Processed {total_tickets} tickets"
    print(summary_msg)
    logging.info(summary_msg)

# Run the script if executed directly
if __name__ == "__main__":
    main()

