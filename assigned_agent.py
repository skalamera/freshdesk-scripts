"""
Freshdesk Ticket Assignment Analysis Script

DESCRIPTION:
This script analyzes ticket assignments by fetching assigned agent, group,
and status information for a list of tickets. It provides detailed insights
into ticket distribution, agent workload, and assignment patterns across
your Freshdesk helpdesk system.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket, agent, and group read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TICKET_IDS list with the ticket IDs you want to analyze
4. Ensure your API key has permissions for:
   - Ticket read access
   - Agent read access
   - Group read access
5. Run the script: python assigned_agent.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_IDS: List of ticket IDs to analyze
- OUTPUT_FILENAME: CSV file for results (default: 'ticket_assignments.csv')

OUTPUT:
- Console output showing assignment details for each ticket
- CSV file with structured assignment data
- Detailed logging for troubleshooting
- Summary statistics on agent and group assignments

TICKET ASSIGNMENT DATA INCLUDES:
- Ticket ID and basic information
- Assigned agent name and ID
- Assigned group name and ID
- Current ticket status (Open, Pending, Resolved, Closed)
- Assignment timestamps and details

CSV OUTPUT FORMAT:
Ticket ID,Agent Name,Agent ID,Group Name,Group ID,Status,Subject
12345,John Doe,67012345,Support Team,67001234,Open,Login Issue
12346,Jane Smith,67023456,Escalation Team,67002345,Pending,Feature Request

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining tickets after rate limit delay
- Logs rate limit events for monitoring

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket, agent, and group read permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes tickets sequentially to respect rate limits
- Makes separate API calls for agent and group details
- Large ticket lists may take significant time to process
- Consider batching for very large datasets

ANALYSIS FEATURES:
- Identifies unassigned tickets
- Shows agent workload distribution
- Highlights group assignment patterns
- Tracks status distribution across assignments
- Provides data for workload balancing decisions
"""

import requests
import logging
import time
import csv
import os
import sys
from collections import defaultdict, Counter

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# Script Configuration
OUTPUT_FILENAME = 'ticket_assignments.csv'
LOG_FILENAME = 'assignment_analysis.log'
REQUEST_TIMEOUT = 30  # 30 seconds timeout for API requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Status mapping for better readability
STATUS_MAPPING = {
    2: "Open",
    3: "Pending",
    4: "Resolved",
    5: "Closed"
}

# List of ticket IDs to analyze
# Replace this list with your actual ticket IDs
TICKET_IDS = [
    265148, 265239, 268186, 268479, 268481, 268506, 268506, 268638, 268638, 268953,
    269094, 269401, 269710, 269711, 269969, 270217, 270530, 270727, 270858, 270962,
    270988, 271077, 271077, 271120, 271319, 271320, 272016, 272445, 272700, 272701,
    273202, 273432, 274085, 274197, 274202, 274203, 274220, 275575, 275616, 275617,
    275618, 275619, 275620, 275621, 275622, 275624, 275625, 275628, 275629, 275630,
    275631, 275633, 275634, 275635, 275637, 275638, 275639, 275640, 275641, 275642,
    275643, 275644, 275645, 275646, 275647, 275648, 275650, 275653, 275654, 275655,
    275656, 275656, 275656, 276337
]

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

    if not TICKET_IDS:
        logging.error("TICKET_IDS list is empty. Please add ticket IDs to analyze.")
        print("❌ TICKET_IDS list is empty. Please add ticket IDs to analyze.")
        return False

    return True

def make_api_request(url):
    """
    Make a rate-limited API request to Freshdesk.

    Args:
        url (str): Full URL for the API request

    Returns:
        dict or None: API response data, or None if failed
    """
    try:
        logging.debug(f"Making API request to: {url}")
        response = requests.get(url, auth=(API_KEY, 'X'), timeout=REQUEST_TIMEOUT)
    
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
            return make_api_request(url)  # Retry the same request
        else:
            logging.error(f"API request failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for URL {url}: {e}")
        return None

def get_ticket_details(ticket_id):
    """
    Fetch detailed information for a specific ticket.

    Args:
        ticket_id (int): The ticket ID to fetch details for

    Returns:
        dict or None: Ticket details if successful, None if failed
    """
    url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}"
    return make_api_request(url)

def get_agent_details(agent_id):
    """
    Fetch agent information by agent ID.

    Args:
        agent_id (int): The agent ID to fetch details for

    Returns:
        dict or None: Agent details if successful, None if failed
    """
    if not agent_id:
        return None

    url = f"https://{DOMAIN}/api/v2/agents/{agent_id}"
    return make_api_request(url)

def get_group_details(group_id):
    """
    Fetch group information by group ID.

    Args:
        group_id (int): The group ID to fetch details for

    Returns:
        dict or None: Group details if successful, None if failed
    """
    if not group_id:
        return None

    url = f"https://{DOMAIN}/api/v2/groups/{group_id}"
    return make_api_request(url)

def fetch_ticket_assignment_details(ticket_id):
    """
    Fetch complete assignment details for a ticket including agent and group info.

    Args:
        ticket_id (int): The ticket ID to analyze

    Returns:
        dict: Complete assignment information for the ticket
    """
    print(f"Processing ticket {ticket_id}...")

    # Fetch ticket details
    ticket_data = get_ticket_details(ticket_id)

    if not ticket_data:
        logging.error(f"Failed to fetch ticket {ticket_id}")
        return {
            "ticket_id": ticket_id,
            "agent_name": "Error fetching ticket",
            "agent_id": None,
            "group_name": "Error fetching ticket",
            "group_id": None,
            "status": "Error fetching ticket",
            "status_id": None,
            "subject": "Error fetching ticket"
        }

    # Extract basic ticket information
    ticket_info = {
        "ticket_id": ticket_id,
        "subject": ticket_data.get("subject", "No subject"),
        "status_id": ticket_data.get("status"),
        "status": STATUS_MAPPING.get(ticket_data.get("status"), "Unknown Status"),
        "agent_id": ticket_data.get("responder_id"),
        "group_id": ticket_data.get("group_id")
    }

    # Fetch agent details if assigned
    agent_data = get_agent_details(ticket_info["agent_id"])
    if agent_data:
        ticket_info["agent_name"] = agent_data.get("contact", {}).get("name", "Unknown Agent")
    else:
        ticket_info["agent_name"] = "No agent assigned"

    # Fetch group details if assigned
    group_data = get_group_details(ticket_info["group_id"])
    if group_data:
        ticket_info["group_name"] = group_data.get("name", "Unknown Group")
    else:
        ticket_info["group_name"] = "No group assigned"

    # Log the results
    logging.info(f"Ticket {ticket_id}: {ticket_info['agent_name']} -> {ticket_info['group_name']} ({ticket_info['status']})")

    return ticket_info

def save_assignments_to_csv(assignments_data, filename):
    """
    Save assignment data to CSV file.

    Args:
        assignments_data (list): List of assignment dictionaries
        filename (str): Output CSV filename

    Returns:
        bool: True if save successful, False otherwise
    """
    if not assignments_data:
        logging.warning("No assignment data to save")
        print("⚠ No assignment data to save")
        return False

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all unique fieldnames
            fieldnames = set()
            for assignment in assignments_data:
                fieldnames.update(assignment.keys())

            fieldnames = sorted(fieldnames)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data rows
            for assignment in assignments_data:
                writer.writerow(assignment)

        file_size = os.path.getsize(filename)
        logging.info(f"Successfully saved {len(assignments_data)} assignments to {filename} ({file_size} bytes)")
        print(f"✓ Saved {len(assignments_data)} assignments to {filename}")
        return True

    except PermissionError:
        error_msg = f"Permission denied writing to {filename}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error saving CSV file: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def analyze_assignments(assignments_data):
    """
    Analyze assignment patterns and provide insights.

    Args:
        assignments_data (list): List of assignment dictionaries

    Returns:
        dict: Analysis results and insights
    """
    if not assignments_data:
        return {}

    analysis = {
        "total_tickets": len(assignments_data),
        "assigned_tickets": 0,
        "unassigned_tickets": 0,
        "agent_distribution": Counter(),
        "group_distribution": Counter(),
        "status_distribution": Counter(),
        "problematic_tickets": []
    }

    for assignment in assignments_data:
        # Count assignments vs unassigned
        if assignment.get("agent_name") not in ["No agent assigned", "Error fetching ticket"]:
            analysis["assigned_tickets"] += 1
        else:
            analysis["unassigned_tickets"] += 1

        # Agent distribution
        agent_name = assignment.get("agent_name", "Unassigned")
        analysis["agent_distribution"][agent_name] += 1

        # Group distribution
        group_name = assignment.get("group_name", "Unassigned")
        analysis["group_distribution"][group_name] += 1

        # Status distribution
        status = assignment.get("status", "Unknown")
        analysis["status_distribution"][status] += 1

        # Identify problematic tickets
        if assignment.get("agent_name") in ["Error fetching ticket", "No agent assigned"] or \
           assignment.get("group_name") in ["Error fetching ticket", "No group assigned"]:
            analysis["problematic_tickets"].append(assignment.get("ticket_id"))

    return analysis

def main():
    """
    Main function to orchestrate the ticket assignment analysis.
    """
    print("Freshdesk Ticket Assignment Analysis Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Ticket Assignment Analysis")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    # Check for duplicate ticket IDs
    unique_tickets = list(set(TICKET_IDS))
    if len(unique_tickets) != len(TICKET_IDS):
        duplicates = len(TICKET_IDS) - len(unique_tickets)
        logging.warning(f"Found {duplicates} duplicate ticket IDs in the list")
        print(f"⚠ Found {duplicates} duplicate ticket IDs (removed automatically)")

    print(f"Processing {len(unique_tickets)} unique tickets...")

    # Fetch assignment details for all tickets
    assignments_data = []
    success_count = 0
    error_count = 0

    for i, ticket_id in enumerate(unique_tickets, 1):
        print(f"  [{i}/{len(unique_tickets)}] Ticket {ticket_id}")

        try:
            assignment_details = fetch_ticket_assignment_details(ticket_id)
            assignments_data.append(assignment_details)

            if assignment_details.get("agent_name") not in ["Error fetching ticket", "No agent assigned"]:
                success_count += 1
            else:
                error_count += 1

        except Exception as e:
            logging.error(f"Error processing ticket {ticket_id}: {e}")
            error_count += 1
            continue

        # Small delay between requests to be respectful
        time.sleep(0.1)

    print(f"\n✓ Processed {len(assignments_data)} tickets")
    print(f"  Successfully analyzed: {success_count}")
    print(f"  Errors: {error_count}")

    if not assignments_data:
        print("❌ No assignment data collected. Check logs for errors.")
        return 1

    # Save to CSV
    print("
Saving results to CSV...")
    if save_assignments_to_csv(assignments_data, OUTPUT_FILENAME):
        # Analyze the data
        print("
Analyzing assignment patterns...")
        analysis = analyze_assignments(assignments_data)

        # Display analysis results
        print("
📊 ASSIGNMENT ANALYSIS:"        print(f"  Total tickets: {analysis['total_tickets']}")
        print(f"  Assigned tickets: {analysis['assigned_tickets']}")
        print(f"  Unassigned tickets: {analysis['unassigned_tickets']}")

        print("
👥 AGENT DISTRIBUTION (Top 5):"        for agent, count in analysis['agent_distribution'].most_common(5):
            print(f"  {agent}: {count} tickets")

        print("
🏢 GROUP DISTRIBUTION (Top 5):"        for group, count in analysis['group_distribution'].most_common(5):
            print(f"  {group}: {count} tickets")

        print("
📈 STATUS DISTRIBUTION:"        for status, count in analysis['status_distribution'].most_common():
            print(f"  {status}: {count} tickets")

        if analysis['problematic_tickets']:
            print(f"\n⚠ PROBLEMATIC TICKETS ({len(analysis['problematic_tickets'])}):")
            for ticket_id in analysis['problematic_tickets'][:10]:  # Show first 10
                print(f"  Ticket {ticket_id}")
            if len(analysis['problematic_tickets']) > 10:
                print(f"  ... and {len(analysis['problematic_tickets']) - 10} more")

        # Final summary
        print("
" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"✓ Analysis completed successfully!")
        print(f"  Tickets analyzed: {len(assignments_data)}")
        print(f"  Results saved to: {OUTPUT_FILENAME}")
        print(f"  Log file: {LOG_FILENAME}")

        if analysis['unassigned_tickets'] > 0:
            print(f"\n⚠ Found {analysis['unassigned_tickets']} unassigned tickets")
            print("  Consider reviewing these for proper assignment")

        if analysis['problematic_tickets']:
            print(f"\n⚠ Found {len(analysis['problematic_tickets'])} tickets with fetch errors")
            print("  Check logs for detailed error information")

        logging.info("=" * 60)
        logging.info("TICKET ASSIGNMENT ANALYSIS COMPLETED")
        logging.info("=" * 60)
        logging.info(f"Tickets processed: {len(assignments_data)}")
        logging.info(f"Successfully analyzed: {success_count}")
        logging.info(f"Errors: {error_count}")
        logging.info(f"Results saved to: {OUTPUT_FILENAME}")
        logging.info("=" * 60)

        return 0
    else:
        print("❌ Failed to save results. Check logs for details.")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

