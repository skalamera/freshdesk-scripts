"""
Freshdesk Email to Ticket ID Mapping Script

DESCRIPTION:
This script reads email addresses from an Excel file and retrieves all
associated ticket IDs from Freshdesk for each email. It then creates
a new Excel file with the mapping between emails and their ticket IDs.

REQUIREMENTS:
- Python 3.x
- pandas library (install with: pip install pandas)
- requests library (install with: pip install requests)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update input_file path to point to your Excel file with email addresses
4. Update output_file path for where you want the results saved
5. Ensure your API key has permissions for ticket access
6. Run the script: python fetch_ticket_ids.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT:
- Excel file with email addresses in the first column
- File should be readable by pandas (xlsx, xls, csv formats supported)

OUTPUT:
- New Excel file with Email and Ticket IDs columns
- Log file with detailed processing information
- Console output showing progress

EXCEL INPUT FORMAT:
- Column A (first column): Email addresses
- One email per row
- Empty cells will be logged as warnings

EXCEL OUTPUT FORMAT:
- Column A: Original email address
- Column B: Comma-separated list of ticket IDs (or error message)

ERROR HANDLING:
- Handles HTTP 404 (email not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Logs all operations for troubleshooting

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining emails after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that input file exists and is readable
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes emails sequentially to respect rate limits
- Large email lists may take significant time to process
- Consider breaking large files into smaller batches if needed
"""

import pandas as pd
import requests
import time
from requests.auth import HTTPBasicAuth
import logging
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain
AUTH = HTTPBasicAuth(API_KEY, 'X')

# File paths - UPDATE THESE PATHS FOR YOUR ENVIRONMENT
input_file = 'C:/Users/skala/Projects/FD Ticket Updater/delete_contacts.xlsx'  # Input Excel file with emails
output_file = 'C:/Users/skala/Projects/FD Ticket Updater/output_with_ticket_ids.xlsx'  # Output Excel file
log_file = 'C:/Users/skala/Projects/FD Ticket Updater/process_log.txt'  # Log file

# HTTP Headers for API requests
HEADERS = {
    'Content-Type': 'application/json'
}

def setup_logging():
    """
    Set up logging to both file and console.
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )

def validate_file_paths():
    """
    Validate that input file exists and output directory is writable.

    Returns:
        bool: True if validation passes, False otherwise
    """
    # Check input file exists
    if not os.path.exists(input_file):
        print(f"✗ Input file not found: {input_file}")
        logging.error(f"Input file not found: {input_file}")
        return False

    # Check output directory is writable
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"✓ Created output directory: {output_dir}")
        except Exception as e:
            print(f"✗ Cannot create output directory: {e}")
            logging.error(f"Cannot create output directory: {e}")
            return False

    return True

def get_ticket_ids_by_email(email):
    """
    Retrieve all ticket IDs associated with a specific email address.

    Args:
        email (str): Email address to search for tickets

    Returns:
        list: List of ticket IDs, empty list if none found or error occurred
    """
    # API endpoint for ticket search
    url = f"https://{DOMAIN}/api/v2/tickets"

    # Request parameters
    params = {
        'email': email
    }

    try:
        # Make the API request
        response = requests.get(url, headers=HEADERS, params=params, auth=AUTH)

        if response.status_code == 200:
            # Success - extract ticket IDs
            tickets = response.json()
            ticket_ids = [ticket['id'] for ticket in tickets]
            logging.info(f"Found {len(ticket_ids)} tickets for email {email}")
            return ticket_ids

        elif response.status_code == 429:
            # Rate limit exceeded - retry after delay
            retry_after = int(response.headers.get("Retry-After", 1))
            logging.info(f"Rate limit exceeded for email {email}. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return get_ticket_ids_by_email(email)  # Retry the same email

        else:
            # Other error
            logging.error(f"Failed to get tickets for {email}: {response.status_code} - {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for email {email}: {e}")
        return []

def process_emails_from_excel():
    """
    Process all emails from the input Excel file.

    Returns:
        list: List of tuples (email, ticket_ids_string) for output
    """
    print("Loading input Excel file...")

    try:
        # Load the Excel file
        df = pd.read_excel(input_file)
        print(f"✓ Loaded {len(df)} rows from {input_file}")
        logging.info(f"Loaded {len(df)} rows from {input_file}")

    except Exception as e:
        print(f"✗ Failed to load Excel file: {e}")
        logging.error(f"Failed to load Excel file: {e}")
        return []

    # Prepare output data
    output_data = []

    # Process each email in the spreadsheet
    for index, row in df.iterrows():
        email = row.iloc[0]  # Email is in the first column

        if pd.isna(email) or email == '':
            # Handle empty email cells
            logging.warning(f"No email provided in row {index + 1}")
            output_data.append([email, 'No email provided'])
            continue

        print(f"Processing row {index + 1}/{len(df)}: {email}")

        # Get ticket IDs for this email
        ticket_ids = get_ticket_ids_by_email(email)

        if ticket_ids:
            # Convert ticket IDs to comma-separated string
            ticket_ids_str = ', '.join(map(str, ticket_ids))
            logging.info(f"Found tickets for {email}: {ticket_ids_str}")
        else:
            ticket_ids_str = 'No tickets found'
            logging.info(f"No tickets found for {email}")

        output_data.append([email, ticket_ids_str])

        # Small delay between requests to be respectful
        time.sleep(0.1)

    return output_data

def export_results_to_excel(output_data):
    """
    Export the results to a new Excel file.

    Args:
        output_data (list): List of tuples (email, ticket_ids_string)
    """
    print("Creating output Excel file...")

    try:
        # Create DataFrame for output
        output_df = pd.DataFrame(output_data, columns=['Email', 'Ticket IDs'])

        # Save to Excel
        output_df.to_excel(output_file, index=False)

        print(f"✓ Successfully exported {len(output_data)} rows to {output_file}")
        logging.info(f"Output saved to {output_file}")

    except Exception as e:
        print(f"✗ Failed to save Excel file: {e}")
        logging.error(f"Failed to save Excel file: {e}")

def main():
    """
    Main function to orchestrate the entire process.
    """
    print("Freshdesk Email to Ticket ID Mapping Tool")
    print("=" * 60)

    # Setup logging
    setup_logging()

    # Validate file paths
    if not validate_file_paths():
        print("❌ File validation failed. Please check paths and permissions.")
        return

    # Process emails from Excel
    output_data = process_emails_from_excel()

    if not output_data:
        print("❌ No data to export. Check input file and logs.")
        return

    # Export results to Excel
    export_results_to_excel(output_data)

    print("\n" + "=" * 60)
    print("Processing completed!")
    print(f"Check log file: {log_file}")
    print(f"Output file: {output_file}")

# Run the script if executed directly
if __name__ == "__main__":
    main()

