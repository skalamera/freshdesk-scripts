"""
Freshdesk Agent Information Retrieval Script

DESCRIPTION:
This script retrieves and displays information about all agents in your
Freshdesk account, including their names, IDs, contact information, and
roles. It's useful for getting agent responder IDs for ticket assignment
operations and understanding your team's structure.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with agent read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for agent read access
4. Run the script: python get_agent_ids.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Agents API: https://developers.freshdesk.com/api/#agents
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- OUTPUT_FILENAME: CSV file for agent data (default: 'agents_export.csv')

OUTPUT:
- Console output showing agent names and responder IDs
- CSV file with detailed agent information
- Detailed logging for troubleshooting

AGENT DATA INCLUDES:
- Agent ID (responder_id for ticket assignments)
- Agent name and contact information
- Email address and phone number
- Agent role and permissions
- Account status (active/inactive)
- Creation and update timestamps

CSV OUTPUT FORMAT:
Agent ID,Name,Email,Role,Active,Created At
67012345,John Doe,john.doe@company.com,Admin,true,2023-01-15T10:30:00Z
67023456,Jane Smith,jane.smith@company.com,Agent,true,2023-01-16T09:15:00Z

ERROR HANDLING:
- Handles HTTP 404 (no agents found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure
- Continues processing even if individual agents fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining pages after rate limit delay
- Logs rate limit events for monitoring

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has agent read permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes agents in pages (default page size varies by API)
- Handles pagination automatically
- Large numbers of agents may take significant time to process
- Rate limiting may cause delays in processing

USAGE SCENARIOS:
- Get responder IDs for ticket assignment scripts
- Audit agent accounts and permissions
- Generate agent contact lists
- Data migration and backup operations
- Integration with other business systems
"""

import requests
import logging
import time
import csv
import os
import sys
from collections import defaultdict

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# Script Configuration
OUTPUT_FILENAME = 'agents_export.csv'
LOG_FILENAME = 'agent_retrieval.log'
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

def get_agents():
    """
    Retrieve all agents from Freshdesk with pagination support.

    Returns:
        list: List of agent dictionaries, or empty list if failed

    Note:
        - Handles pagination automatically
        - Implements rate limiting with retry logic
        - Logs progress for monitoring
    """
    base_url = f"https://{DOMAIN}/api/v2/agents"
        agents = []
        page = 1

    logging.info(f"Starting agent retrieval from {DOMAIN}")
    print("Fetching agents..."
        while True:
        try:
            # Make API request for current page
            response = requests.get(
                f"{base_url}?page={page}",
                auth=(API_KEY, 'X'),
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                # Success - parse response data
            data = response.json()

            if not data:
                    # No more data available
                    logging.info(f"Completed fetching all agents. Total pages: {page - 1}")
                break

                # Add this page of agents to our collection
            agents.extend(data)
                logging.info(f"Fetched page {page} ({len(data)} agents)")
                print(f"  Page {page}: {len(data)} agents retrieved")

            page += 1

            elif response.status_code == 429:
                # Rate limit exceeded - retry after delay
                retry_after = int(response.headers.get('Retry-After', 60))
                logging.warning(f"Rate limit exceeded on page {page}. Retrying after {retry_after} seconds...")
                print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue  # Retry the same page

            else:
                # Other error
                logging.error(f"Failed to fetch agents on page {page}. Status: {response.status_code}")
                logging.error(f"Response: {response.text}")
                print(f"❌ Failed to fetch page {page}: {response.status_code}")
                break

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error on page {page}: {e}")
            print(f"❌ Network error on page {page}: {e}")
            break

    total_agents = len(agents)
    logging.info(f"Successfully retrieved {total_agents} agents total")
    print(f"✓ Retrieved {total_agents} agents total")
        
        return agents

def normalize_agent_data(agent):
    """
    Normalize and enrich agent data for consistent output.

    Args:
        agent (dict): Raw agent data from API

    Returns:
        dict: Normalized agent information
    """
    try:
        # Extract basic agent information
        agent_id = agent.get('id')
        contact_info = agent.get('contact', {})

        # Build normalized agent record
        normalized = {
            'Agent ID': agent_id,
            'Name': contact_info.get('name', 'Unknown'),
            'Email': contact_info.get('email', 'N/A'),
            'Phone': contact_info.get('phone', 'N/A'),
            'Mobile': contact_info.get('mobile', 'N/A'),
            'Active': agent.get('active', False),
            'Role': 'Admin' if agent.get('administrator', False) else 'Agent',
            'Created At': agent.get('created_at', 'N/A'),
            'Updated At': agent.get('updated_at', 'N/A'),
            'Last Login At': agent.get('last_login_at', 'N/A'),
            'Ticket Scope': agent.get('ticket_scope', 'N/A'),
            'Signature': agent.get('signature', 'N/A')[:100] + '...' if agent.get('signature') and len(agent.get('signature', '')) > 100 else agent.get('signature', 'N/A')
        }

        # Add role-specific information
        if agent.get('administrator'):
            normalized['Admin Privileges'] = 'Yes'
        else:
            normalized['Admin Privileges'] = 'No'

        # Add availability information if available
        if 'available' in agent:
            normalized['Available'] = agent.get('available')
        else:
            normalized['Available'] = 'N/A'

        return normalized

    except Exception as e:
        logging.error(f"Error normalizing agent data: {e}")
        return {
            'Agent ID': agent.get('id', 'Unknown'),
            'Name': 'Error processing agent data',
            'Email': 'N/A',
            'Phone': 'N/A',
            'Active': False,
            'Role': 'Error',
            'Error': str(e)
        }

def save_agents_to_csv(agents_data, filename):
    """
    Save agent data to CSV file.

    Args:
        agents_data (list): List of normalized agent dictionaries
        filename (str): Output CSV filename

    Returns:
        bool: True if save successful, False otherwise
    """
    if not agents_data:
        logging.warning("No agent data to save")
        print("⚠ No agent data to save")
        return False

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all unique fieldnames
            fieldnames = set()
            for agent in agents_data:
                fieldnames.update(agent.keys())

            fieldnames = sorted(fieldnames)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data rows
            for agent in agents_data:
                writer.writerow(agent)

        file_size = os.path.getsize(filename)
        logging.info(f"Successfully saved {len(agents_data)} agents to {filename} ({file_size} bytes)")
        print(f"✓ Saved {len(agents_data)} agents to {filename}")
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

def analyze_agents(agents_data):
    """
    Analyze agent data and provide insights.

    Args:
        agents_data (list): List of normalized agent dictionaries

    Returns:
        dict: Analysis results and insights
    """
    if not agents_data:
        return {}

    analysis = {
        "total_agents": len(agents_data),
        "active_agents": 0,
        "inactive_agents": 0,
        "admin_agents": 0,
        "regular_agents": 0,
        "role_distribution": defaultdict(int),
        "status_distribution": defaultdict(int),
        "agents_with_issues": []
    }

    for agent in agents_data:
        # Count active vs inactive
        if agent.get('Active', False):
            analysis["active_agents"] += 1
        else:
            analysis["inactive_agents"] += 1

        # Count admin vs regular agents
        if agent.get('Admin Privileges') == 'Yes':
            analysis["admin_agents"] += 1
        else:
            analysis["regular_agents"] += 1

        # Role distribution
        role = agent.get('Role', 'Unknown')
        analysis["role_distribution"][role] += 1

        # Status distribution (availability)
        available = agent.get('Available', 'N/A')
        analysis["status_distribution"][str(available)] += 1

        # Identify agents with potential issues
        if agent.get('Name') in ['Unknown', 'Error processing agent data']:
            analysis["agents_with_issues"].append(agent.get('Agent ID', 'Unknown'))

    return analysis

def display_agents_console(agents_data):
    """
    Display agent information in a formatted console output.

    Args:
        agents_data (list): List of normalized agent dictionaries
    """
    if not agents_data:
        print("No agents to display.")
        return

    print(f"\n{'=' * 80}")
    print("FRESHdesk AGENTS SUMMARY")
    print(f"{'=' * 80}")

    for i, agent in enumerate(agents_data, 1):
        print(f"\n👤 AGENT #{i}")
        print(f"{'-' * 30}")
        print(f"Name: {agent.get('Name', 'N/A')}")
        print(f"Agent ID: {agent.get('Agent ID', 'N/A')}")
        print(f"Email: {agent.get('Email', 'N/A')}")
        print(f"Role: {agent.get('Role', 'N/A')}")
        print(f"Active: {'Yes' if agent.get('Active') else 'No'}")
        print(f"Created: {agent.get('Created At', 'N/A')}")

        # Show admin status if applicable
        if agent.get('Admin Privileges') == 'Yes':
            print("Admin: Yes"
        # Show availability if available
        if agent.get('Available') != 'N/A':
            print(f"Available: {agent.get('Available')}")

    print(f"\n{'=' * 80}")

def main():
    """
    Main function to orchestrate the agent information retrieval process.
    """
    print("Freshdesk Agent Information Retrieval Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Agent Information Retrieval")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    try:
        # Retrieve agents
        agents_data = get_agents()

        if not agents_data:
            logging.error("No agents retrieved from Freshdesk")
            print("❌ No agents found. Please check:")
            print("  - API key has agent read permissions")
            print("  - Freshdesk domain is correct")
            print("  - Network connectivity to Freshdesk")
            print("  - Agents exist in your Freshdesk account")
            return 1

        # Normalize agent data
        print("\nProcessing agent data...")
        normalized_agents = []
        for agent in agents_data:
            normalized = normalize_agent_data(agent)
            normalized_agents.append(normalized)

        # Display agents in console
        print("\nDisplaying agent information...")
        display_agents_console(normalized_agents)

        # Save to CSV
        print("
Saving agents to CSV file...")
        if save_agents_to_csv(normalized_agents, OUTPUT_FILENAME):
            # Analyze the data
            print("
Analyzing agent data...")
            analysis = analyze_agents(normalized_agents)

            # Display analysis results
            print("
📊 AGENT ANALYSIS:"            print(f"  Total agents: {analysis['total_agents']}")
            print(f"  Active agents: {analysis['active_agents']}")
            print(f"  Inactive agents: {analysis['inactive_agents']}")
            print(f"  Admin agents: {analysis['admin_agents']}")
            print(f"  Regular agents: {analysis['regular_agents']}")

            print("
👥 ROLE DISTRIBUTION:"            for role, count in analysis['role_distribution'].items():
                print(f"  {role}: {count}")

            print("
📈 AVAILABILITY STATUS:"            for status, count in analysis['status_distribution'].items():
                print(f"  {status}: {count}")

            if analysis['agents_with_issues']:
                print(f"\n⚠ AGENTS WITH ISSUES ({len(analysis['agents_with_issues'])}):")
                for agent_id in analysis['agents_with_issues'][:5]:  # Show first 5
                    print(f"  Agent ID: {agent_id}")
                if len(analysis['agents_with_issues']) > 5:
                    print(f"  ... and {len(analysis['agents_with_issues']) - 5} more")

            # Final summary
            print("
" + "=" * 60)
            print("RETRIEVAL SUMMARY")
            print("=" * 60)
            print(f"✓ Retrieval completed successfully!")
            print(f"  Agents retrieved: {len(normalized_agents)}")
            print(f"  Results saved to: {OUTPUT_FILENAME}")
            print(f"  Log file: {LOG_FILENAME}")

            # Show key insights
            if analysis['inactive_agents'] > 0:
                print(f"\n⚠ Found {analysis['inactive_agents']} inactive agents")
                print("  Consider reviewing agent accounts for cleanup")

            if analysis['agents_with_issues']:
                print(f"\n⚠ Found {len(analysis['agents_with_issues'])} agents with data issues")
                print("  Check logs for detailed error information")

            logging.info("=" * 60)
            logging.info("AGENT RETRIEVAL COMPLETED SUCCESSFULLY")
            logging.info("=" * 60)
            logging.info(f"Agents retrieved: {len(normalized_agents)}")
            logging.info(f"Active agents: {analysis['active_agents']}")
            logging.info(f"Inactive agents: {analysis['inactive_agents']}")
            logging.info(f"Results saved to: {OUTPUT_FILENAME}")
            logging.info("=" * 60)

            return 0
        else:
            print("❌ Failed to save results. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Retrieval interrupted by user")
        logging.info("Retrieval interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during retrieval: {e}")
        logging.error(f"Unexpected error during retrieval: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

