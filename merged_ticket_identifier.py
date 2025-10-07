"""
Freshdesk Merged Ticket Analysis Script

DESCRIPTION:
This script analyzes Freshdesk tickets to identify merged tickets by scanning
conversation bodies for ticket references. It extracts detailed information
about merged tickets including their status, creation dates, subjects, and tags,
then exports the results to an Excel file for analysis.
This script analyzes Freshdesk tickets to identify merged tickets by scanning conversation bodies for ticket references and exports detailed information to Excel

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with ticket and conversation read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to analyze
4. Ensure your API key has permissions for ticket and conversation access
5. Run the script: python merge_id.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Conversations API: https://developers.freshdesk.com/api/#conversations
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- ticket_ids: List of ticket IDs to analyze for merged tickets
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- BATCH_SIZE: Number of tickets to process in each batch (default: 100)

OUTPUT:
- Excel file with detailed information about merged tickets
- Log file with operation details and error information
- Console output showing progress and statistics

EXCEL OUTPUT INCLUDES:
- Original Ticket ID: ID of the ticket being analyzed
- Merged Ticket ID: ID of referenced merged tickets
- Created At: Creation timestamp of merged ticket
- Status: Current status of merged ticket
- Subject: Subject line of merged ticket
- Tags: Tags associated with merged ticket

MERGED TICKET DETECTION:
- Scans conversation bodies for Freshdesk ticket URLs
- Uses regex pattern to extract ticket IDs from URLs
- Only processes unique ticket references per conversation
- Handles multiple merged tickets per original ticket

ERROR HANDLING:
- Handles HTTP 404 (ticket/conversation not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual requests fail

RATE LIMIT HANDLING:
- Processes tickets in configurable batches
- Includes delays between batches to respect rate limits
- Handles rate limit responses with automatic retry

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and conversation read permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes tickets in batches to manage API rate limits
- Each ticket requires 2 API calls (ticket + conversations)
- Large ticket lists may take significant time to process
- Adjust batch size based on your rate limits
"""

import requests
import re
import logging
import pandas as pd
import time
from collections import defaultdict
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# HTTP Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# Status code to name mapping for better readability
STATUS_MAPPING = {
    2: 'Open',
    3: 'Pending',
    4: 'Resolved',
    5: 'Closed'
}

# Configuration
BATCH_SIZE = 100  # Number of tickets to process in each batch
OUTPUT_FILENAME = 'merged_tickets.xlsx'
LOG_FILENAME = 'merged_ticket_analysis.log'

def extract_merged_ticket_ids(conversation_body):
    """
    Extract ticket IDs from Freshdesk ticket URLs in conversation text.

    This function uses regex to find Freshdesk ticket URLs in conversation
    bodies and extracts the ticket IDs from them.

    Args:
        conversation_body (str): The text content of a conversation

    Returns:
        list: List of unique ticket IDs found in the conversation

    Note:
        - Looks for URLs in format: https://domain.freshdesk.com/a/tickets/ID
        - Returns unique ticket IDs only (removes duplicates)
        - Case-sensitive matching for the specific domain
    """
    # Regex pattern to match Freshdesk ticket URLs and extract ticket IDs
    # Pattern: https://benchmarkeducationcompany.freshdesk.com/a/tickets/(digits)
    pattern = r'https://benchmarkeducationcompany\.freshdesk\.com\/a\/tickets\/(\d+)'

    # Find all matches and extract ticket IDs
    merged_ticket_ids = re.findall(pattern, conversation_body)

    # Return unique ticket IDs only
    return list(set(merged_ticket_ids))

def get_conversations_for_ticket(ticket_id):
    """
    Retrieve all conversations for a specific ticket.

    This function fetches conversations for a ticket and extracts
    any merged ticket references from the conversation bodies.

    Args:
        ticket_id (int): ID of the ticket to get conversations for

    Returns:
        list: List of unique merged ticket IDs found in conversations

    Note:
        - Returns empty list if no conversations or no merged tickets found
        - Handles API errors gracefully with logging
    """
    # API endpoint for ticket conversations
    conversations_url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}/conversations"

    try:
        # Make the API request
        response = requests.get(conversations_url, auth=(API_KEY, 'X'), headers=HEADERS)

        if response.status_code == 200:
            # Success - parse conversations
            conversations = response.json()
            merged_ticket_ids = []

            # Extract merged ticket IDs from each conversation
            for conversation in conversations:
                conversation_body = conversation.get('body', '')
                conversation_merged_ids = extract_merged_ticket_ids(conversation_body)
                merged_ticket_ids.extend(conversation_merged_ids)

            # Return unique ticket IDs only
            unique_merged_ids = list(set(merged_ticket_ids))
            print(f"✓ Found {len(unique_merged_ids)} merged ticket references in ticket {ticket_id}")
            return unique_merged_ids

        elif response.status_code == 429:
            # Rate limit exceeded - retry after delay
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...")
            logging.warning(f'Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...')
            time.sleep(retry_after)
            return get_conversations_for_ticket(ticket_id)  # Retry the same ticket

        else:
            # Other error
            print(f"✗ Failed to retrieve conversations for ticket {ticket_id}: {response.status_code}")
            logging.error(f"Failed to retrieve conversations for ticket {ticket_id}: {response.status_code} - {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error for ticket {ticket_id}: {e}")
        logging.error(f"Network error for ticket {ticket_id}: {e}")
        return []

def get_ticket_details(ticket_id):
    """
    Retrieve detailed information about a specific ticket.

    This function fetches complete ticket information including status,
    creation date, subject, and tags.

    Args:
        ticket_id (int): ID of the ticket to get details for

    Returns:
        dict or None: Ticket details dictionary, None if error

    Note:
        - Maps numeric status codes to readable names
        - Combines tags into comma-separated string
        - Handles missing fields gracefully
    """
    # API endpoint for ticket details
    ticket_url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}"

    try:
        # Make the API request
        response = requests.get(ticket_url, auth=(API_KEY, 'X'), headers=HEADERS)

        if response.status_code == 200:
            # Success - parse ticket data
            ticket = response.json()

            # Extract and format ticket information
            ticket_details = {
                'ticket_id': ticket['id'],
                'created_at': ticket['created_at'],
                'status': STATUS_MAPPING.get(ticket['status'], f"Unknown ({ticket['status']})"),
                'subject': ticket.get('subject', 'No Subject'),
                'tags': ', '.join(ticket.get('tags', []))  # Combine tags into string
            }

            print(f"✓ Retrieved details for merged ticket {ticket_id}")
            return ticket_details

        elif response.status_code == 429:
            # Rate limit exceeded - retry after delay
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...")
            logging.warning(f'Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...')
            time.sleep(retry_after)
            return get_ticket_details(ticket_id)  # Retry the same ticket

        else:
            # Other error
            print(f"✗ Failed to retrieve details for ticket {ticket_id}: {response.status_code}")
            logging.error(f"Failed to retrieve details for ticket {ticket_id}: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error for ticket {ticket_id}: {e}")
        logging.error(f"Network error for ticket {ticket_id}: {e}")
        return None

def extract_merged_tickets(ticket_ids, all_tickets_data):
    """
    Extract merged ticket information from a batch of tickets.

    This function processes a batch of tickets, finds merged ticket references
    in their conversations, and retrieves detailed information about each
    merged ticket.

    Args:
        ticket_ids (list): List of ticket IDs to process in this batch
        all_tickets_data (list): Shared list to store all merged ticket data

    Note:
        - Processes tickets sequentially within the batch
        - Includes delay between tickets to respect rate limits
        - Collects data for Excel export
    """
    print(f"Processing batch of {len(ticket_ids)} tickets...")

    for i, ticket_id in enumerate(ticket_ids, 1):
        print(f"  Processing ticket {i}/{len(ticket_ids)}: {ticket_id}")

        # Get conversations for this ticket and extract merged ticket IDs
        merged_tickets = get_conversations_for_ticket(ticket_id)

        if merged_tickets:
            print(f"    Found {len(merged_tickets)} merged ticket references")

            for merged_ticket_id in merged_tickets:
                # Get detailed information about the merged ticket
                ticket_details = get_ticket_details(merged_ticket_id)

                if ticket_details:
                    # Add to Excel export data
                    all_tickets_data.append({
                        'Original Ticket ID': ticket_id,
                        'Merged Ticket ID': ticket_details['ticket_id'],
                        'Created At': ticket_details['created_at'],
                        'Status': ticket_details['status'],
                        'Subject': ticket_details['subject'],
                        'Tags': ticket_details['tags']
                    })

                    print(f"      ✓ Added merged ticket {merged_ticket_id} to export")
        else:
            print("    No merged tickets found")

        # Rate limiting delay between tickets
        time.sleep(1)  # 1 second delay between tickets

def setup_logging():
    """
    Set up logging to both file and console.
    """
    # Ensure log directory exists (create if needed)
    log_dir = os.path.dirname(LOG_FILENAME) if os.path.dirname(LOG_FILENAME) else '.'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILENAME),
            logging.StreamHandler()  # Also log to console
        ]
    )

def validate_ticket_ids(ticket_ids):
    """
    Validate that ticket IDs are valid integers.

    Args:
        ticket_ids (list): List of ticket IDs to validate

    Returns:
        bool: True if all IDs are valid, False otherwise
    """
    for ticket_id in ticket_ids:
        if not isinstance(ticket_id, int) or ticket_id <= 0:
            print(f"✗ Invalid ticket ID: {ticket_id}")
            return False
    return True

def main():
    """
    Main function to orchestrate the entire merged ticket analysis process.
    """
    print("Freshdesk Merged Ticket Analysis Tool")
    print("=" * 70)
    print(f"Total tickets to analyze: {len(ticket_ids)}")
    print(f"Batch size: {BATCH_SIZE} tickets per batch")
    print("=" * 70)

    # Setup logging
    setup_logging()

    # Validate ticket IDs
    if not validate_ticket_ids(ticket_ids):
        print("❌ Invalid ticket IDs found. Please check the ticket_ids list.")
        return

    # Initialize data collection
    all_tickets_data = []

    # Process tickets in batches
    total_batches = (len(ticket_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(ticket_ids), BATCH_SIZE):
        current_batch = ticket_ids[i:i + BATCH_SIZE]
        batch_number = i // BATCH_SIZE + 1

        print(f"\n--- Batch {batch_number}/{total_batches} ---")
        print(f"Processing tickets {current_batch[0]} to {current_batch[-1]}...")

        # Track data size before this batch
        before_count = len(all_tickets_data)

        # Process this batch of tickets
        extract_merged_tickets(current_batch, all_tickets_data)

        # Count merged tickets found in this batch
        batch_merged_count = len(all_tickets_data) - before_count

        print(f"Batch {batch_number} complete. Found {batch_merged_count} merged ticket references.")

        # Progress delay between batches (respectful API usage)
        if batch_number < total_batches:
            print("Waiting 5 seconds before next batch...")
            time.sleep(5)

    # Create and save Excel file
    if all_tickets_data:
        print(f"\nCreating Excel file with {len(all_tickets_data)} merged ticket records...")

        try:
            # Convert to DataFrame
            df = pd.DataFrame(all_tickets_data)

            # Reorder columns for better readability
            column_order = [
                'Original Ticket ID', 'Merged Ticket ID', 'Status',
                'Subject', 'Created At', 'Tags'
            ]
            df = df[column_order]

            # Save to Excel
            df.to_excel(OUTPUT_FILENAME, index=False)

            print(f"✓ Excel file '{OUTPUT_FILENAME}' created successfully!")
            print(f"  Total merged ticket references found: {len(all_tickets_data)}")

        except Exception as e:
            print(f"✗ Failed to create Excel file: {e}")
            logging.error(f"Failed to create Excel file: {e}")

    else:
        print("⚠ No merged tickets found in any of the analyzed tickets.")

    # Final summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Original tickets analyzed: {len(ticket_ids)}")
    print(f"Batches processed: {total_batches}")
    print(f"Merged ticket references found: {len(all_tickets_data)}")

    if all_tickets_data:
        unique_merged = len(set(item['Merged Ticket ID'] for item in all_tickets_data))
        print(f"Unique merged tickets: {unique_merged}")

    print(f"Excel file: {OUTPUT_FILENAME}")
    print(f"Log file: {LOG_FILENAME}")
    print("=" * 70)

# Run the script if executed directly
if __name__ == "__main__":
    main()
