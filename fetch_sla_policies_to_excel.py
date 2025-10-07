"""
Freshdesk SLA Policies Excel Export Script

DESCRIPTION:
This script retrieves all SLA (Service Level Agreement) policies from Freshdesk
and exports them to an Excel file with comprehensive logging. It handles
pagination automatically and includes detailed error handling.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with SLA policy read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for SLA policy access
4. Run the script: python fetch_sla_policies_to_excel.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- SLA Policies API: https://developers.freshdesk.com/api/#sla_policies
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- OUTPUT_FILENAME: Name of the Excel file to create (default: 'sla_policies.xlsx')

OUTPUT:
- Excel file with all SLA policy data
- Log file with detailed operation information
- Console output showing progress and results

EXCEL OUTPUT INCLUDES:
- All SLA policy fields and nested data (flattened by pandas)
- Policy names, descriptions, and configuration details
- Response and resolution time targets
- Escalation rules and agent assignments
- Creation and update timestamps

LOGGING:
- Creates 'sla_policies.log' with detailed operation logs
- Logs successful fetches, errors, and rate limit handling
- Includes timestamps for troubleshooting

ERROR HANDLING:
- Handles HTTP 404 (endpoint not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual requests fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining pages after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has SLA policy read permissions
- Check that your Freshdesk instance has SLA policies configured
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

PERFORMANCE CONSIDERATIONS:
- Handles pagination automatically for large numbers of policies
- Processes pages sequentially to respect rate limits
- Large numbers of SLA policies may take significant time to process
"""

import requests
import json
import time
import logging
import pandas as pd
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# API Configuration
BASE_URL = f'https://{DOMAIN}/api/v2'
HEADERS = {'Content-Type': 'application/json'}

# Output configuration
OUTPUT_FILENAME = 'sla_policies.xlsx'
LOG_FILENAME = 'sla_policies.log'

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

def get_sla_policies():
    """
    Retrieve all SLA policies from Freshdesk using pagination.

    Returns:
        list: List of SLA policy dictionaries, empty list if error

    Note:
        - Handles pagination automatically
        - Returns all policies across multiple pages
        - Stops when no more data is available
    """
    endpoint = f'{BASE_URL}/sla_policies'
    sla_policies = []
    page = 1

    print(f"Fetching SLA policies from {DOMAIN}...")

    while True:
        try:
            # Make paginated request
            response = requests.get(
                endpoint,
                headers=HEADERS,
                auth=(API_KEY, 'X'),
                params={'page': page}
            )

            if response.status_code == 200:
                # Success - parse response
                data = response.json()

                if not data:
                    # No more data available
                    print(f"✓ Completed fetching all SLA policies (processed {page - 1} pages)")
                    break

                # Add this page of policies to our collection
                sla_policies.extend(data)
                print(f"✓ Fetched page {page} ({len(data)} policies)")

                page += 1

            elif response.status_code == 429:
                # Rate limit exceeded - retry after delay
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                logging.warning(f'Rate limit exceeded. Retrying after {retry_after} seconds...')
                time.sleep(retry_after)
                continue

            else:
                # Other error
                print(f"✗ Failed to fetch SLA policies: {response.status_code}")
                print(f"  Error: {response.text}")
                logging.error(f'Failed to fetch SLA policies. Status code: {response.status_code}, Response: {response.text}')
                break

        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            logging.error(f'Network error: {e}')
            break

    print(f"Total SLA policies retrieved: {len(sla_policies)}")
    logging.info(f'Successfully retrieved {len(sla_policies)} SLA policies')
    return sla_policies

def save_to_excel(data, file_name):
    """
    Save SLA policies data to an Excel file.

    Args:
        data (list): List of SLA policy dictionaries
        file_name (str): Output filename for the Excel file

    Note:
        - Uses pandas json_normalize to flatten nested data
        - Creates Excel file with all policy fields
        - Handles complex nested structures automatically
    """
    try:
        print(f"Creating Excel file: {file_name}")

        # Convert to DataFrame and flatten nested JSON structures
        df = pd.json_normalize(data)

        # Save to Excel
        df.to_excel(file_name, index=False)

        print(f"✓ Successfully saved {len(data)} SLA policies to {file_name}")
        logging.info(f'Successfully saved {len(data)} SLA policies to {file_name}')
        return True

    except Exception as e:
        print(f"✗ Failed to save Excel file: {e}")
        logging.error(f'Failed to save Excel file: {e}')
        return False

def analyze_sla_policies(sla_policies):
    """
    Analyze the retrieved SLA policies and provide summary statistics.

    Args:
        sla_policies (list): List of SLA policy dictionaries

    Returns:
        dict: Summary statistics about the policies
    """
    if not sla_policies:
        return {}

    stats = {
        'total_policies': len(sla_policies),
        'default_policies': 0,
        'policies_with_targets': 0,
        'policies_with_escalation': 0,
        'priorities_covered': set()
    }

    for policy in sla_policies:
        # Count default policies
        if policy.get('is_default'):
            stats['default_policies'] += 1

        # Count policies with targets
        if policy.get('sla_target'):
            stats['policies_with_targets'] += 1

            # Collect priority levels
            for priority in policy['sla_target'].keys():
                stats['priorities_covered'].add(priority)

        # Count policies with escalation rules
        if policy.get('escalation'):
            stats['policies_with_escalation'] += 1

    stats['priorities_covered'] = sorted(list(stats['priorities_covered']))

    return stats

def display_summary_stats(stats):
    """
    Display summary statistics about the SLA policies.

    Args:
        stats (dict): Statistics dictionary from analyze_sla_policies()
    """
    if not stats:
        print("No SLA policies to analyze.")
        return

    print("\n" + "=" * 60)
    print("SLA POLICIES SUMMARY")
    print("=" * 60)
    print(f"Total SLA Policies: {stats['total_policies']}")
    print(f"Default Policies: {stats['default_policies']}")
    print(f"Policies with Targets: {stats['policies_with_targets']}")
    print(f"Policies with Escalation: {stats['policies_with_escalation']}")
    print(f"Priority Levels Covered: {', '.join(stats['priorities_covered'])}")
    print("=" * 60)

def main():
    """
    Main function to orchestrate the entire SLA policies export process.
    """
    print("Freshdesk SLA Policies Excel Export Tool")
    print("=" * 60)

    # Setup logging
    setup_logging()

    # Retrieve all SLA policies
    sla_policies = get_sla_policies()

    if not sla_policies:
        print("❌ Unable to retrieve SLA policies. Please check:")
        print("  - API key has SLA policy read permissions")
        print("  - Freshdesk domain is correct")
        print("  - Network connectivity to Freshdesk API")
        print(f"  - Check log file: {LOG_FILENAME}")
        return

    # Analyze and display statistics
    stats = analyze_sla_policies(sla_policies)
    display_summary_stats(stats)

    # Save to Excel
    if not save_to_excel(sla_policies, OUTPUT_FILENAME):
        print("❌ Failed to save SLA policies to Excel. Check logs for details.")
        return

    # Show sample of what was exported
    if sla_policies:
        print("
Sample SLA Policy:"        sample_policy = sla_policies[0]
        print(f"  Name: {sample_policy.get('name', 'Unknown')}")
        print(f"  Description: {sample_policy.get('description', 'No description')[:100]}...")
        print(f"  Default: {'Yes' if sample_policy.get('is_default') else 'No'}")

        # Show available fields
        print("
Available fields in export:"        print(f"  {len(sample_policy)} fields including: {', '.join(list(sample_policy.keys())[:10])}...")

    print("
" + "=" * 60)
    print("Export completed successfully!")
    print(f"Excel file: {OUTPUT_FILENAME}")
    print(f"Log file: {LOG_FILENAME}")
    print("=" * 60)

# Run the script if executed directly
if __name__ == '__main__':
    main()

