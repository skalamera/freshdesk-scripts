"""
Freshdesk Agent Ticket Activities Retrieval Script

DESCRIPTION:
This script retrieves all ticket activities for a specific agent from the
previous day and exports them to a text file. It fetches tickets updated
yesterday that are assigned to the specified agent, then gets their activities
and filters for activities that occurred within the same date range.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and activity read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update AGENT_ID with the ID of the agent you want to analyze
4. Ensure your API key has permissions for ticket and activity access
5. Run the script: python get_ticket_activities.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- AGENT_ID: ID of the agent to analyze activities for

OUTPUT:
- Text file with detailed activity information
- Console output showing progress and results

ACTIVITY DATA INCLUDES:
- Ticket ID and Activity ID
- Creation timestamp
- Activity type (reply, note, status change, etc.)
- Activity description/details
- Separation between different activities

DATE RANGE:
- Automatically calculates yesterday's date range
- From: 00:00:00 UTC yesterday
- To: 23:59:59 UTC yesterday
- Filters both ticket updates and activity timestamps

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining tickets after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and activity read permissions
- Check that AGENT_ID is a valid agent ID in your Freshdesk
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that the agent has tickets assigned yesterday

PERFORMANCE CONSIDERATIONS:
- Processes tickets in pages (100 per page)
- Handles pagination automatically
- Large numbers of tickets may take significant time to process
- Rate limiting may cause delays in processing
"""

import requests
from datetime import datetime, timedelta, timezone
import time
import os
import logging
import sys

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# Agent ID to analyze activities for
# TODO: Replace with the actual agent ID you want to analyze
AGENT_ID = 67038975154  # Replace with your agent ID

# HTTP Headers for API requests
HEADERS = {
    'Content-Type': 'application/json'
}

# Configure logging to both file and console
LOG_FILENAME = 'agent_ticket_activities_analysis.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_yesterday_date_range():
    """
    Calculate yesterday's date range for filtering.

    Returns:
        tuple: (start_date_iso, end_date_iso) in ISO format
    """
    # Get yesterday's date in UTC
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)

    # Start of yesterday (00:00:00)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of yesterday (23:59:59)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_date.isoformat(), end_date.isoformat()

def fetch_tickets_with_pagination(start_date, end_date):
    """
    Fetch all tickets updated within the specified date range using pagination.

    Args:
        start_date (str): Start date in ISO format
        end_date (str): End date in ISO format

    Returns:
        list: List of ticket dictionaries
    """
    print(f"Fetching tickets updated between {start_date} and {end_date}...")

    # API endpoint for tickets
    url = f'https://{DOMAIN}/api/v2/tickets'

    # Pagination variables
    page = 1
    per_page = 100  # Maximum tickets per page
    all_tickets = []

    while True:
        # Prepare request parameters
        params = {
            'updated_since': start_date,
            'page': page,
            'per_page': per_page
        }

        # Make the API request
        response = requests.get(url, auth=(API_KEY, 'X'), headers=HEADERS, params=params)

        if response.status_code == 429:
            # Handle rate limit errors
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        if response.status_code != 200:
            print(f"Failed to fetch tickets: {response.status_code} - {response.text}")
            break

        # Parse response data
        data = response.json()
        if not data:
            break

        # Add tickets to our collection
        all_tickets.extend(data)
        print(f"Fetched page {page} ({len(data)} tickets)")

        # Check if there are more pages
        if 'link' not in response.headers or 'rel="next"' not in response.headers['link']:
            break

        page += 1

    print(f"Total tickets fetched: {len(all_tickets)}")
    return all_tickets

def fetch_ticket_activities(ticket, start_date, end_date):
    """
    Fetch activities for a specific ticket within the date range.

    Args:
        ticket (dict): Ticket dictionary
        start_date (str): Start date in ISO format
        end_date (str): End date in ISO format

    Returns:
        list: List of filtered activity dictionaries
    """
    ticket_id = ticket['id']

    try:
        # API endpoint for ticket activities
        activities_url = f'https://{DOMAIN}/api/v2/tickets/{ticket_id}/activities'

        # Make the API request
        response = requests.get(activities_url, auth=(API_KEY, 'X'), headers=HEADERS)

        if response.status_code == 429:
            # Handle rate limit errors
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded for ticket {ticket_id}. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            return fetch_ticket_activities(ticket, start_date, end_date)  # Retry

        if response.status_code != 200:
            print(f"Failed to fetch activities for ticket {ticket_id}: {response.status_code} - {response.text}")
            return []

        # Parse activities
        activities = response.json()

        # Filter activities within our date range
        filtered_activities = [
            activity for activity in activities
            if start_date <= activity['created_at'] <= end_date
        ]

        if filtered_activities:
            print(f"Found {len(filtered_activities)} activities for ticket {ticket_id}")

        return filtered_activities

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching activities for ticket {ticket_id}: {e}")
        return []

def export_activities_to_file(activities, filename):
    """
    Export activities to a text file.

    Args:
        activities (list): List of activity dictionaries
        filename (str): Output filename
    """
    print(f"Exporting {len(activities)} activities to {filename}...")

    with open(filename, 'w', encoding='utf-8') as file:
        for activity in activities:
            file.write(f"Ticket ID: {activity['ticket_id']}\n")
            file.write(f"Activity ID: {activity['id']}\n")
            file.write(f"Created At: {activity['created_at']}\n")
            file.write(f"Activity Type: {activity['activity_type']}\n")
            file.write(f"Description: {activity['description']}\n")
            file.write("-" * 40 + "\n")

def main():
    """
    Main function to orchestrate the entire process.
    """
    print("Freshdesk Agent Activity Analysis")
    print("=" * 50)
    logging.info("Starting Freshdesk Agent Activity Analysis")

    # Get yesterday's date range
    start_date, end_date = get_yesterday_date_range()
    print(f"Analyzing activities for date range: {start_date} to {end_date}")
    logging.info(f"Analyzing activities for date range: {start_date} to {end_date}")

    # Fetch all tickets updated yesterday
    all_tickets = fetch_tickets_with_pagination(start_date, end_date)
    logging.info(f"Fetched {len(all_tickets)} tickets total")

    # Filter tickets assigned to our agent
    agent_tickets = [ticket for ticket in all_tickets if ticket.get('responder_id') == AGENT_ID]

    print(f"Tickets assigned to agent {AGENT_ID}: {len(agent_tickets)}")
    logging.info(f"Tickets assigned to agent {AGENT_ID}: {len(agent_tickets)}")

    if not agent_tickets:
        print("No tickets found for the specified agent in the date range.")
        logging.warning("No tickets found for the specified agent in the date range.")
        return

    # Fetch activities for each ticket
    all_activities = []
    for ticket in agent_tickets:
        ticket_activities = fetch_ticket_activities(ticket, start_date, end_date)
        all_activities.extend(ticket_activities)

        # Small delay between requests to be respectful
        time.sleep(0.1)

    # Export activities to file
    if all_activities:
        filename = 'ticket_activities_yesterday.txt'
        export_activities_to_file(all_activities, filename)
        print(f"\n✓ Successfully exported {len(all_activities)} activities to {filename}")
        logging.info(f"Successfully exported {len(all_activities)} activities to {filename}")
    else:
        print("\n⚠ No activities found for the specified date range and agent.")
        logging.warning("No activities found for the specified date range and agent.")

    print("\n" + "=" * 50)
    print("Analysis completed!")
    logging.info("Analysis completed!")

# Run the script if executed directly
if __name__ == "__main__":
    main()

