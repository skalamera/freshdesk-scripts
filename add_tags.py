"""
Freshdesk Ticket Tag Addition Script

DESCRIPTION:
This script adds 'qa' tags to multiple Freshdesk tickets in batch. It processes
a predefined list of ticket IDs, checks if they already have the 'qa' tag,
and adds it if missing. Includes rate limiting and comprehensive logging.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read/write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to tag
4. Ensure your API key has permissions for ticket updates
5. Run the script: python add_tags.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- ticket_ids: List of ticket IDs to add 'qa' tags to
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain

OUTPUT:
- Updates tickets with 'qa' tag if not already present
- Comprehensive logging to console and file
- Progress tracking and rate limit handling

LOGGING:
- Creates detailed logs of all operations
- Logs successful updates, skips, and errors
- Includes timestamps for troubleshooting

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles network and connection errors
- Validates existing tags before updating
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Processes tickets in batches with delays
- Waits 10 seconds every 50 requests
- Respects Freshdesk API rate limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Batch processing with rate limit delays
- Large ticket lists may take significant time to process
- Adjust batch size and delays based on your rate limits
"""

import requests
import time
import logging
import os

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ticket_tag_addition.log"),
        logging.StreamHandler()  # Also log to console
    ]
)

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain
API_URL = f"https://{DOMAIN}/api/v2/tickets"

# HTTP Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# List of ticket IDs to add 'qa' tags to
# Replace this list with your actual ticket IDs
ticket_ids = [
    292584, 292599, 294867, 294931, 294934, 295987, 297199, 297302, 297903, 298495,
    298514, 298681, 299126, 299921, 294741, 295051, 297006, 294032, 294298, 295213,
    297286, 297988, 294145, 294302, 295478, 295740, 296020, 296247, 297695, 298415,
    298575, 293115, 294340, 295541, 296529, 296964, 297102, 298239, 298479, 298502,
    298951, 297907, 295037, 295053, 296045, 297278, 293650, 294805, 296043, 292670,
    294201, 294967, 295184, 294792, 293707, 296573, 296806, 297227, 297487, 293588,
    295979, 296422, 298171, 293839, 294441, 294618, 295397, 296436, 297201, 297725,
    297862, 297948, 298116, 298179, 299217, 294538, 294099, 296638, 296764, 297311,
    297315, 297393, 297512, 297612, 294438, 294725, 295505, 293406, 294264, 299218
]

def update_ticket_tags(ticket_id):
    """
    Add 'qa' tag to a specific ticket if not already present.

    This function fetches the current ticket details, checks if the 'qa' tag
    already exists, and adds it if missing.

    Args:
        ticket_id (int): The ticket ID to update

    Returns:
        bool: True if successfully updated, False otherwise
    """
    try:
        # Fetch existing ticket details
        response = requests.get(
            f"{API_URL}/{ticket_id}",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )

        if response.status_code == 200:
            ticket_data = response.json()
            existing_tags = ticket_data.get("tags", [])

            # Check if 'qa' tag is already present
            if "qa" in existing_tags:
                logging.info(f"Ticket {ticket_id} already has 'qa' tag. Skipping.")
                return True

            # Add 'qa' tag to existing tags (remove duplicates)
            updated_tags = list(set(existing_tags + ["qa"]))
            payload = {"tags": updated_tags}

            # Update ticket with new tags
            update_response = requests.put(
                f"{API_URL}/{ticket_id}",
                auth=(API_KEY, "X"),
                json=payload,
                headers=HEADERS
            )

            if update_response.status_code == 200:
                logging.info(f"✓ Successfully added 'qa' tag to ticket {ticket_id}")
                return True
            else:
                logging.error(f"✗ Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
                return False

        elif response.status_code == 404:
            logging.warning(f"⚠ Ticket {ticket_id} not found (404)")
            return False
        else:
            logging.error(f"✗ Error fetching ticket {ticket_id}: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"✗ Request error for ticket {ticket_id}: {str(e)}")
        return False

def main():
    """
    Main function to process all tickets with rate limiting.
    """
    print("Starting batch ticket tag addition...")
    print(f"Processing {len(ticket_ids)} tickets...")
    print("=" * 60)

    success_count = 0
    skip_count = 0
    error_count = 0

    # Process tickets in batches with rate limiting
    for index, ticket_id in enumerate(ticket_ids, start=1):
        print(f"Processing ticket {index}/{len(ticket_ids)}: ID {ticket_id}")

        # Update the ticket
        if update_ticket_tags(ticket_id):
            success_count += 1
        elif "already has" in str(logging.getLogger().handlers[0].stream.getvalue()):
            skip_count += 1
        else:
            error_count += 1

        # Handle rate limits: pause every 50 requests
        if index % 50 == 0:
            print(f"Processed {index} tickets. Pausing for rate limit...")
            logging.info(f"Pausing for rate limit after {index} requests...")
            time.sleep(10)

    # Print final summary
    print("\n" + "=" * 60)
    print("BATCH UPDATE SUMMARY")
    print("=" * 60)
    print(f"Total tickets processed: {len(ticket_ids)}")
    print(f"Successfully updated: {success_count}")
    print(f"Already had 'qa' tag: {skip_count}")
    print(f"Errors/failures: {error_count}")
    print("=" * 60)

    logging.info(f"Batch update completed. Success: {success_count}, Skipped: {skip_count}, Errors: {error_count}")

# Run the script if executed directly
if __name__ == "__main__":
    main()

