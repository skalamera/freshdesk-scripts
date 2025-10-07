"""
Freshdesk Agent Responder ID Retrieval Script

DESCRIPTION:
This script retrieves all agents from your Freshdesk account and displays
their responder IDs along with detailed agent information. Agent responder
IDs are essential for ticket assignment operations and API integrations.
The script provides both console output and file export capabilities.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with agent read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for agent read access
4. Run the script: python get_responder_id.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Agents API: https://developers.freshdesk.com/api/#agents
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- OUTPUT_FILENAME: File for agent data (default: 'agents_list.txt')

OUTPUT:
- Console output showing agent names and responder IDs
- Text file with agent information for reference
- Detailed logging for troubleshooting

AGENT DATA INCLUDES:
- Agent ID (responder_id for ticket assignments)
- Agent name and contact information
- Email address and phone number
- Agent role and permissions
- Account status (active/inactive)
- Creation and update timestamps

FILE OUTPUT FORMAT:
Name: John Doe, Responder ID: 67012345, Email: john.doe@company.com
Name: Jane Smith, Responder ID: 67023456, Email: jane.smith@company.com

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
- Generate agent reference lists for reports
- Data migration and backup operations
- Integration with other business systems
"""

import requests
import json
import logging
import time
import os
import sys

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# Script Configuration
OUTPUT_FILENAME = 'agents_list.txt'
LOG_FILENAME = 'agent_responder_retrieval.log'
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
    params = {
        'page': page,
                'per_page': 100  # Maximum allowed per page
            }

            response_data = make_api_request(base_url, params)

            if response_data is None:
                # Error occurred
                logging.error(f"Failed to fetch agents on page {page}")
                print(f"❌ Failed to fetch page {page}")
        break

            if not response_data:
                # No more data available
                logging.info(f"Completed fetching all agents. Total pages: {page - 1}")
        break
    
            # Add this page of agents to our collection
            agents.extend(response_data)
            logging.info(f"Fetched page {page} ({len(response_data)} agents)")
            print(f"  Page {page}: {len(response_data)} agents retrieved")
    
    page += 1

        except Exception as e:
            logging.error(f"Unexpected error on page {page}: {e}")
            print(f"❌ Unexpected error on page {page}: {e}")
            break

    total_agents = len(agents)
    logging.info(f"Successfully retrieved {total_agents} agents total")
    print(f"✓ Retrieved {total_agents} agents total")

    return agents

def normalize_agent_data(agent):
    """
    Normalize agent data for consistent output and error handling.

    Args:
        agent (dict): Raw agent data from API

    Returns:
        dict: Normalized agent information with safe fallbacks
    """
    try:
        # Extract basic agent information with safe fallbacks
        agent_id = agent.get('id', 'Unknown')
        contact_info = agent.get('contact', {})

        # Build normalized agent record
        normalized = {
            'Agent ID': agent_id,
            'Name': contact_info.get('name', 'Unknown Agent'),
            'Email': contact_info.get('email', 'N/A'),
            'Phone': contact_info.get('phone', 'N/A'),
            'Mobile': contact_info.get('mobile', 'N/A'),
            'Active': 'Yes' if agent.get('active', False) else 'No',
            'Role': 'Admin' if agent.get('administrator', False) else 'Agent',
            'Created At': agent.get('created_at', 'N/A'),
            'Updated At': agent.get('updated_at', 'N/A'),
            'Last Login At': agent.get('last_login_at', 'N/A')
        }

        # Add role-specific information
        if agent.get('administrator'):
            normalized['Admin Privileges'] = 'Yes'
        else:
            normalized['Admin Privileges'] = 'No'

        # Add availability information if available
        if 'available' in agent:
            normalized['Available'] = 'Yes' if agent.get('available') else 'No'
        else:
            normalized['Available'] = 'N/A'

        return normalized

    except Exception as e:
        logging.error(f"Error normalizing agent data: {e}")
        return {
            'Agent ID': agent.get('id', 'Error'),
            'Name': 'Error processing agent data',
            'Email': 'N/A',
            'Phone': 'N/A',
            'Active': 'Error',
            'Role': 'Error',
            'Error': str(e)
        }

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

    # Sort agents by name for better readability
    sorted_agents = sorted(agents_data, key=lambda x: x.get('Name', ''))

    for i, agent in enumerate(sorted_agents, 1):
        print(f"\n👤 AGENT #{i}")
        print(f"{'-' * 30}")
        print(f"Name: {agent.get('Name', 'N/A')}")
        print(f"Responder ID: {agent.get('Agent ID', 'N/A')}")
        print(f"Email: {agent.get('Email', 'N/A')}")
        print(f"Role: {agent.get('Role', 'N/A')}")
        print(f"Active: {agent.get('Active', 'N/A')}")

        # Show admin status if applicable
        if agent.get('Admin Privileges') == 'Yes':
            print("Admin: Yes"
        # Show availability if available
        if agent.get('Available') != 'N/A':
            print(f"Available: {agent.get('Available')}")

        # Show creation date if available
        if agent.get('Created At') != 'N/A':
            print(f"Created: {agent.get('Created At')}")

    print(f"\n{'=' * 80}")

def save_agents_to_file(agents_data, filename):
    """
    Save agent information to a text file for reference.

    Args:
        agents_data (list): List of normalized agent dictionaries
        filename (str): Output filename

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

        with open(filename, 'w', encoding='utf-8') as file:
            # Write header
            file.write("Freshdesk Agents List\n")
            file.write("=" * 50 + "\n")
            file.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            file.write(f"Total Agents: {len(agents_data)}\n\n")

            # Sort agents by name for better readability
            sorted_agents = sorted(agents_data, key=lambda x: x.get('Name', ''))

            # Write agent details
            for agent in sorted_agents:
                file.write(f"Name: {agent.get('Name', 'N/A')}\n")
                file.write(f"Responder ID: {agent.get('Agent ID', 'N/A')}\n")
                file.write(f"Email: {agent.get('Email', 'N/A')}\n")
                file.write(f"Role: {agent.get('Role', 'N/A')}\n")
                file.write(f"Active: {agent.get('Active', 'N/A')}\n")

                if agent.get('Admin Privileges') == 'Yes':
                    file.write("Admin Privileges: Yes\n")

                if agent.get('Available') != 'N/A':
                    file.write(f"Available: {agent.get('Available')}\n")

                file.write(f"Created: {agent.get('Created At', 'N/A')}\n")
                file.write("-" * 50 + "\n")

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
        error_msg = f"Error saving file: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def analyze_agents(agents_data):
    """
    Analyze agent data and provide insights.

    Args:
        agents_data (list): List of normalized agent dictionaries

    Returns:
        dict: Analysis results and statistics
    """
    if not agents_data:
        return {}

    analysis = {
        "total_agents": len(agents_data),
        "active_agents": 0,
        "inactive_agents": 0,
        "admin_agents": 0,
        "regular_agents": 0,
        "available_agents": 0,
        "unavailable_agents": 0,
        "agents_with_issues": []
    }

    for agent in agents_data:
        # Count active vs inactive
        if agent.get('Active') == 'Yes':
            analysis["active_agents"] += 1
        else:
            analysis["inactive_agents"] += 1

        # Count admin vs regular agents
        if agent.get('Admin Privileges') == 'Yes':
            analysis["admin_agents"] += 1
        else:
            analysis["regular_agents"] += 1

        # Count availability
        if agent.get('Available') == 'Yes':
            analysis["available_agents"] += 1
        elif agent.get('Available') == 'No':
            analysis["unavailable_agents"] += 1

        # Identify agents with potential issues
        if agent.get('Name') in ['Unknown Agent', 'Error processing agent data']:
            analysis["agents_with_issues"].append(agent.get('Agent ID', 'Unknown'))

    return analysis

def main():
    """
    Main function to orchestrate the agent responder ID retrieval process.
    """
    print("Freshdesk Agent Responder ID Retrieval Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Agent Responder ID Retrieval")

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

        # Display agents in console (first 10 for brevity)
        print("\nDisplaying agent information (first 10 agents)...")
        display_agents_console(normalized_agents[:10])

        if len(normalized_agents) > 10:
            print(f"\n... and {len(normalized_agents) - 10} more agents")
            print(f"Full list saved to {OUTPUT_FILENAME}")

        # Save to file
        print("
Saving agents to file...")
        if save_agents_to_file(normalized_agents, OUTPUT_FILENAME):
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
            print(f"  Available agents: {analysis['available_agents']}")
            print(f"  Unavailable agents: {analysis['unavailable_agents']}")

            if analysis['agents_with_issues']:
                print(f"\n⚠ AGENTS WITH ISSUES ({len(analysis['agents_with_issues'])}):")
                for agent_id in analysis['agents_with_issues'][:5]:  # Show first 5
                    print(f"  Agent ID: {agent_id}")
                if len(analysis['agents_with_issues']) > 5:
                    print(f"  ... and {len(analysis['agents_with_issues']) - 5} more")

            # Show key responder IDs for easy reference
            print("
🔑 KEY RESPONDER IDS (Active Agents):"            active_agents = [agent for agent in normalized_agents if agent.get('Active') == 'Yes']
            for agent in active_agents[:10]:  # Show first 10 active agents
                print(f"  {agent.get('Name', 'N/A')}: {agent.get('Agent ID', 'N/A')}")
            if len(active_agents) > 10:
                print(f"  ... and {len(active_agents) - 10} more active agents")

            # Final summary
            print("
" + "=" * 60)
            print("RETRIEVAL SUMMARY")
            print("=" * 60)
            print(f"✓ Retrieval completed successfully!")
            print(f"  Agents retrieved: {len(normalized_agents)}")
            print(f"  Results saved to: {OUTPUT_FILENAME}")
            print(f"  Log file: {LOG_FILENAME}")

            # Show recommendations
            if analysis['inactive_agents'] > 0:
                print(f"\n⚠ Found {analysis['inactive_agents']} inactive agents")
                print("  Consider reviewing agent accounts for cleanup")

            if analysis['unavailable_agents'] > 0:
                print(f"\n⚠ Found {analysis['unavailable_agents']} unavailable agents")
                print("  These agents may be on break or offline")

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

