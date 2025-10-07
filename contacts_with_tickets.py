"""
Freshdesk Contacts with Tickets Relationship Script

DESCRIPTION:
This script retrieves tickets from Freshdesk that have been updated in the
last 30 days and enriches them with detailed contact information. It creates
two separate JSON files: one with ticket-contact relationships and another
with unique contact details. This is useful for analyzing customer behavior,
generating contact lists, and understanding ticket distribution patterns.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and contact read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update DAYS_BACK if you want a different time range (default: 30 days)
4. Ensure your API key has permissions for ticket and contact read access
5. Run the script: python contacts_with_tickets.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Contacts API: https://developers.freshdesk.com/api/#contacts
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- DAYS_BACK: Number of days to look back for tickets (default: 30)
- OUTPUT_FILENAMES: Output JSON filenames

OUTPUT:
- tickets_with_contacts.json: Tickets with enriched contact information
- unique_contacts.json: Unique contact details from tickets
- Console output showing progress and results
- Detailed logging for troubleshooting

TICKET DATA INCLUDES:
- Ticket ID and creation timestamp
- Requester contact ID and details
- Contact name, email, and phone information
- Unique contacts list (no duplicates)

CONTACT DATA INCLUDES:
- Contact ID, name, email, phone
- Company association (if available)
- Contact creation and update timestamps
- Address and other contact details

ERROR HANDLING:
- Handles HTTP 404 (ticket/contact not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure
- Continues processing even if individual items fail

RATE LIMIT HANDLING:
- Monitors API rate limits automatically
- Implements delays when rate limits are reached
- Continues processing after rate limit reset
- Logs rate limit events for monitoring

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and contact read permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets exist in the specified time range

PERFORMANCE CONSIDERATIONS:
- Processes tickets in pages (100 per page by default)
- Fetches contact details individually for accuracy
- Large datasets may take significant time to process
- Rate limiting may cause delays in processing

USAGE SCENARIOS:
- Generate contact lists for marketing campaigns
- Analyze customer ticket patterns and frequency
- Create customer relationship management data
- Data migration and backup operations
- Customer support analytics and reporting
"""

import requests
import json
import time
import logging
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# Script Configuration
DAYS_BACK = 30  # Number of days to look back for tickets
TICKETS_PER_PAGE = 100  # Tickets per API page
REQUEST_TIMEOUT = 30  # Timeout for API requests

# Output configuration
OUTPUT_FILENAMES = {
    'tickets': 'tickets_with_contacts.json',
    'contacts': 'unique_contacts.json',
    'log': 'contacts_tickets_export.log'
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_FILENAMES['log'], encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def validate_configuration():
    """
    Validate that all required configuration is present and valid.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if not API_KEY or API_KEY == "5TMgbcZdRFY70hSpEdj":
        logging.error("API_KEY not configured. Please set your actual Freshdesk API key.")
        print("❌ API_KEY not configured. Please update the script with your API key.")
        return False

    if not DOMAIN or DOMAIN == "benchmarkeducationcompany.freshdesk.com":
        logging.error("DOMAIN not configured. Please set your actual Freshdesk domain.")
        print("❌ DOMAIN not configured. Please update the script with your domain.")
        return False

    if DAYS_BACK <= 0:
        logging.error("DAYS_BACK must be a positive number.")
        print("❌ DAYS_BACK must be a positive number.")
        return False

    return True

def calculate_date_range(days_back):
    """
    Calculate the date range for ticket filtering.

    Args:
        days_back (int): Number of days to look back

    Returns:
        tuple: (start_date_iso, end_date_iso) in ISO format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    return start_date.isoformat(), end_date.isoformat()

def make_api_request(url, params=None):
    """
    Make a rate-limited API request to Freshdesk.

    Args:
        url (str): Full URL for the API request
        params (dict, optional): Query parameters for the request

    Returns:
        dict or None: API response data, or None if failed
    """
    try:
        logging.debug(f"Making API request to: {url}")
        response = requests.get(
            url,
            auth=(API_KEY, 'X'),
            timeout=REQUEST_TIMEOUT,
            params=params or {}
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logging.warning(f"Resource not found: {url}")
            return None
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return make_api_request(url, params)  # Retry the same request
        else:
            logging.error(f"API request failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for URL {url}: {e}")
        return None

def get_tickets(start_date, end_date):
    """
    Retrieve tickets updated within the specified date range.

    Args:
        start_date (str): Start date in ISO format
        end_date (str): End date in ISO format

    Returns:
        list: List of ticket dictionaries, or empty list if failed

    Note:
        - Uses pagination to handle large datasets
        - Implements rate limiting with automatic delays
        - Filters tickets by update date
    """
    base_url = f"https://{DOMAIN}/api/v2/tickets"
    all_tickets = []
    page = 1

    logging.info(f"Fetching tickets updated between {start_date} and {end_date}")
    print("Fetching tickets..."
    while True:
        try:
            # Prepare request parameters
            params = {
                'page': page,
                'per_page': TICKETS_PER_PAGE,
                'updated_since': start_date
            }

            logging.info(f"Fetching tickets page {page}")
            response_data = make_api_request(base_url, params)

            if response_data is None:
                # Error occurred
                logging.error(f"Failed to fetch tickets on page {page}")
                print(f"❌ Failed to fetch page {page}")
            break

            if not response_data:
                # No more data available
                logging.info(f"Completed fetching all tickets. Total pages: {page - 1}")
            break

            # Add this page of tickets to our collection
            all_tickets.extend(response_data)
            logging.info(f"Fetched page {page} ({len(response_data)} tickets)")
            print(f"  Page {page}: {len(response_data)} tickets retrieved")

            page += 1

        except Exception as e:
            logging.error(f"Unexpected error on page {page}: {e}")
            print(f"❌ Unexpected error on page {page}: {e}")
            break

    total_tickets = len(all_tickets)
    logging.info(f"Successfully retrieved {total_tickets} tickets total")
    print(f"✓ Retrieved {total_tickets} tickets total")

    return all_tickets

def get_contact_details(contact_id):
    """
    Retrieve detailed information for a specific contact.

    Args:
        contact_id (int): The contact ID to fetch details for

    Returns:
        dict or None: Contact details if successful, None if failed
    """
    if not contact_id:
        logging.warning("No contact ID provided")
        return None

    url = f"https://{DOMAIN}/api/v2/contacts/{contact_id}"
    return make_api_request(url)

def normalize_ticket_data(ticket):
    """
    Normalize ticket data for consistent output.

    Args:
        ticket (dict): Raw ticket data from API

    Returns:
        dict: Normalized ticket information
    """
    try:
        # Extract basic ticket information
        normalized = {
            'ticket_id': ticket.get('id'),
            'ticket_number': ticket.get('id'),  # For compatibility
            'subject': ticket.get('subject', 'No subject'),
            'description': ticket.get('description', 'No description'),
            'status': ticket.get('status'),
            'priority': ticket.get('priority'),
            'created_at': ticket.get('created_at'),
            'updated_at': ticket.get('updated_at'),
            'requester_id': ticket.get('requester_id'),
            'group_id': ticket.get('group_id'),
            'agent_id': ticket.get('responder_id'),
            'source': ticket.get('source'),
            'tags': ticket.get('tags', []),
            'custom_fields': ticket.get('custom_fields', {})
        }

        # Add status and priority names for better readability
        status_mapping = {2: 'Open', 3: 'Pending', 4: 'Resolved', 5: 'Closed'}
        priority_mapping = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent'}

        normalized['status_name'] = status_mapping.get(normalized['status'], 'Unknown')
        normalized['priority_name'] = priority_mapping.get(normalized['priority'], 'Unknown')

        return normalized

    except Exception as e:
        logging.error(f"Error normalizing ticket data: {e}")
        return {
            'ticket_id': ticket.get('id', 'Error'),
            'error': str(e)
        }

def normalize_contact_data(contact):
    """
    Normalize contact data for consistent output.

    Args:
        contact (dict): Raw contact data from API

    Returns:
        dict: Normalized contact information
    """
    try:
        # Extract basic contact information
        normalized = {
            'contact_id': contact.get('id'),
            'name': contact.get('name', 'Unknown Contact'),
            'email': contact.get('email', 'N/A'),
            'phone': contact.get('phone', 'N/A'),
            'mobile': contact.get('mobile', 'N/A'),
            'company_id': contact.get('company_id'),
            'active': contact.get('active', True),
            'created_at': contact.get('created_at'),
            'updated_at': contact.get('updated_at'),
            'address': contact.get('address', 'N/A'),
            'twitter_id': contact.get('twitter_id', 'N/A'),
            'unique_external_id': contact.get('unique_external_id', 'N/A'),
            'custom_fields': contact.get('custom_fields', {})
        }

        # Add company information if available
        if normalized['company_id']:
            # We could fetch company details here if needed
            normalized['has_company'] = True
    else:
            normalized['has_company'] = False

        return normalized

    except Exception as e:
        logging.error(f"Error normalizing contact data: {e}")
        return {
            'contact_id': contact.get('id', 'Error'),
            'name': 'Error processing contact data',
            'email': 'N/A',
            'error': str(e)
        }

def extract_ticket_contact_relationships(tickets):
    """
    Extract ticket information and enrich with contact details.

    Args:
        tickets (list): List of ticket dictionaries

    Returns:
        tuple: (enriched_tickets, unique_contacts)
    """
    if not tickets:
        logging.warning("No tickets provided for processing")
        return [], []

    logging.info(f"Processing {len(tickets)} tickets for contact enrichment")
    print("Processing tickets and contacts..."

    enriched_tickets = []
    unique_contacts = {}
    processed_count = 0
    error_count = 0

    for ticket in tickets:
        try:
            # Normalize ticket data
            normalized_ticket = normalize_ticket_data(ticket)
            requester_id = normalized_ticket.get('requester_id')

            if not requester_id:
                logging.warning(f"Ticket {normalized_ticket.get('ticket_id')} has no requester_id")
                normalized_ticket['contact_details'] = {
                    'name': 'No requester ID',
                    'email': 'N/A',
                    'phone': 'N/A'
                }
                enriched_tickets.append(normalized_ticket)
                continue

            # Fetch contact details
            contact_data = get_contact_details(requester_id)

            if contact_data:
                # Normalize contact data
                normalized_contact = normalize_contact_data(contact_data)

                # Add contact details to ticket
                normalized_ticket['contact_details'] = {
                    'contact_id': normalized_contact.get('contact_id'),
                    'name': normalized_contact.get('name'),
                    'email': normalized_contact.get('email'),
                    'phone': normalized_contact.get('phone'),
                    'mobile': normalized_contact.get('mobile'),
                    'company_id': normalized_contact.get('company_id'),
                    'active': normalized_contact.get('active')
                }

                # Add to unique contacts (avoid duplicates)
                if requester_id not in unique_contacts:
                    unique_contacts[requester_id] = normalized_contact

            else:
                # Contact not found or error
                logging.warning(f"Could not fetch contact details for ID {requester_id}")
                normalized_ticket['contact_details'] = {
                    'contact_id': requester_id,
                    'name': 'Contact not found',
                    'email': 'N/A',
                    'phone': 'N/A'
                }

            enriched_tickets.append(normalized_ticket)
            processed_count += 1

        except Exception as e:
            logging.error(f"Error processing ticket {ticket.get('id', 'unknown')}: {e}")
            error_count += 1
            continue

        # Small delay between requests to be respectful
        time.sleep(0.1)

    logging.info(f"Processed {processed_count} tickets, {error_count} errors")
    print(f"✓ Processed {processed_count} tickets, {error_count} errors")

    return enriched_tickets, list(unique_contacts.values())

def save_data_to_json(data, filename):
    """
    Save data to JSON file with proper formatting.

    Args:
        data: Data to save (list or dict)
        filename (str): Output filename

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False, default=str)

        file_size = os.path.getsize(filename)
        logging.info(f"Successfully saved {len(data)} records to {filename} ({file_size} bytes)")
        print(f"✓ Saved {len(data)} records to {filename}")
        return True

    except PermissionError:
        error_msg = f"Permission denied writing to {filename}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error saving JSON file: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def analyze_relationships(tickets_data, contacts_data):
    """
    Analyze the ticket-contact relationships and provide insights.

    Args:
        tickets_data (list): Enriched ticket data
        contacts_data (list): Contact data

    Returns:
        dict: Analysis results and insights
    """
    if not tickets_data or not contacts_data:
        return {}

    analysis = {
        "total_tickets": len(tickets_data),
        "total_contacts": len(contacts_data),
        "tickets_with_contacts": 0,
        "tickets_without_contacts": 0,
        "active_contacts": 0,
        "inactive_contacts": 0,
        "contacts_with_companies": 0,
        "contacts_without_companies": 0,
        "status_distribution": defaultdict(int),
        "priority_distribution": defaultdict(int)
    }

    # Analyze tickets
    for ticket in tickets_data:
        if ticket.get('contact_details', {}).get('name') not in ['Contact not found', 'No requester ID']:
            analysis["tickets_with_contacts"] += 1
        else:
            analysis["tickets_without_contacts"] += 1

        # Status and priority distribution
        status_name = ticket.get('status_name', 'Unknown')
        priority_name = ticket.get('priority_name', 'Unknown')
        analysis["status_distribution"][status_name] += 1
        analysis["priority_distribution"][priority_name] += 1

    # Analyze contacts
    for contact in contacts_data:
        if contact.get('active', True):
            analysis["active_contacts"] += 1
        else:
            analysis["inactive_contacts"] += 1

        if contact.get('company_id'):
            analysis["contacts_with_companies"] += 1
        else:
            analysis["contacts_without_companies"] += 1

    return analysis

def main():
    """
    Main function to orchestrate the ticket-contact relationship extraction.
    """
    print("Freshdesk Contacts with Tickets Relationship Tool")
    print("=" * 70)

    logging.info("Starting Freshdesk Contacts with Tickets Relationship Tool")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    try:
        # Step 1: Calculate date range
        start_date, end_date = calculate_date_range(DAYS_BACK)
        print(f"Step 1: Analyzing tickets from {start_date} to {end_date}")

        # Step 2: Retrieve tickets
        print("Step 2: Fetching tickets...")
        tickets = get_tickets(start_date, end_date)

        if not tickets:
            logging.error("No tickets retrieved from Freshdesk")
            print("❌ No tickets found. Please check:")
            print("  - API key has ticket read permissions")
            print("  - Freshdesk domain is correct")
            print("  - Network connectivity to Freshdesk")
            print(f"  - Tickets exist in the last {DAYS_BACK} days")
            return 1

        print(f"✓ Retrieved {len(tickets)} tickets")

        # Step 3: Extract and enrich ticket-contact relationships
        print("Step 3: Enriching tickets with contact information...")
        enriched_tickets, unique_contacts = extract_ticket_contact_relationships(tickets)

        if not enriched_tickets:
            print("❌ No ticket data could be processed.")
            return 1

        # Step 4: Save data to files
        print("Step 4: Saving data to files...")
        tickets_saved = save_data_to_json(enriched_tickets, OUTPUT_FILENAMES['tickets'])
        contacts_saved = save_data_to_json(unique_contacts, OUTPUT_FILENAMES['contacts'])

        if not (tickets_saved and contacts_saved):
            print("❌ Failed to save data files.")
            return 1

        # Step 5: Analyze relationships
        print("Step 5: Analyzing relationships...")
        analysis = analyze_relationships(enriched_tickets, unique_contacts)

        # Display analysis results
        print("
📊 RELATIONSHIP ANALYSIS:"        print(f"  Total tickets: {analysis['total_tickets']}")
        print(f"  Tickets with contacts: {analysis['tickets_with_contacts']}")
        print(f"  Tickets without contacts: {analysis['tickets_without_contacts']}")
        print(f"  Unique contacts found: {analysis['total_contacts']}")
        print(f"  Active contacts: {analysis['active_contacts']}")
        print(f"  Inactive contacts: {analysis['inactive_contacts']}")

        print("
📈 TICKET STATUS DISTRIBUTION:"        for status, count in analysis['status_distribution'].items():
            print(f"  {status}: {count} tickets")

        print("
🎯 TICKET PRIORITY DISTRIBUTION:"        for priority, count in analysis['priority_distribution'].items():
            print(f"  {priority}: {count} tickets")

        # Show sample data
        if enriched_tickets:
            print("
📋 SAMPLE ENRICHED TICKET:"            sample_ticket = enriched_tickets[0]
            print(f"  Ticket ID: {sample_ticket.get('ticket_id')}")
            print(f"  Subject: {sample_ticket.get('subject', 'N/A')[:50]}...")
            print(f"  Status: {sample_ticket.get('status_name')}")
            print(f"  Contact: {sample_ticket.get('contact_details', {}).get('name', 'N/A')}")
            print(f"  Contact Email: {sample_ticket.get('contact_details', {}).get('email', 'N/A')}")

        # Final summary
        print("
" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"✓ Extraction completed successfully!")
        print(f"  Tickets processed: {len(enriched_tickets)}")
        print(f"  Unique contacts found: {len(unique_contacts)}")
        print(f"  Date range: {DAYS_BACK} days")
        print(f"  Tickets file: {OUTPUT_FILENAMES['tickets']}")
        print(f"  Contacts file: {OUTPUT_FILENAMES['contacts']}")
        print(f"  Log file: {OUTPUT_FILENAMES['log']}")

        # Show recommendations
        if analysis['tickets_without_contacts'] > 0:
            print(f"\n⚠ Found {analysis['tickets_without_contacts']} tickets without contact info")
            print("  These tickets may have invalid requester IDs")

        if analysis['inactive_contacts'] > 0:
            print(f"\n⚠ Found {analysis['inactive_contacts']} inactive contacts")
            print("  Consider reviewing contact status in Freshdesk")

        logging.info("=" * 70)
        logging.info("CONTACT-TICKET RELATIONSHIP EXTRACTION COMPLETED")
        logging.info("=" * 70)
        logging.info(f"Tickets processed: {len(enriched_tickets)}")
        logging.info(f"Unique contacts found: {len(unique_contacts)}")
        logging.info(f"Date range: {DAYS_BACK} days")
        logging.info(f"Output files: {', '.join(OUTPUT_FILENAMES.values())}")
        logging.info("=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n⚠ Extraction interrupted by user")
        logging.info("Extraction interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during extraction: {e}")
        logging.error(f"Unexpected error during extraction: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
