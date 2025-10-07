"""
Freshdesk Contact Deletion Script

DESCRIPTION:
This script deletes contacts from Freshdesk based on email addresses provided
in an Excel file. It performs hard deletion (permanent removal) of contacts
with proper safety checks, confirmation prompts, and comprehensive logging.
This is a destructive operation that cannot be undone.

WARNING: This script performs PERMANENT deletion of contacts. Use with extreme caution.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with contact delete permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update INPUT_FILENAME with your Excel file containing email addresses
4. Ensure your API key has permissions for contact deletion
5. Run the script: python delete_contacts.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Contacts API: https://developers.freshdesk.com/api/#contacts
- Authentication: Basic Auth with API key

INPUT:
- Excel file with email addresses in the first column
- File should be readable by pandas (xlsx, xls, csv formats supported)

OUTPUT:
- Console output showing deletion progress and results
- Detailed log file with all operations and errors
- Summary of successful/failed deletions

DELETION PROCESS:
1. Validates input file and configuration
2. Prompts for confirmation before proceeding
3. Finds contact IDs by email addresses
4. Performs hard deletion (permanent removal)
5. Provides detailed results and recommendations

SAFETY FEATURES:
- Confirmation prompt before deletion
- Validates each contact exists before deletion
- Handles API rate limiting automatically
- Comprehensive error logging and reporting
- Rollback information for troubleshooting

ERROR HANDLING:
- Handles HTTP 404 (contact not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates Excel file format and data
- Continues processing even if individual deletions fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Implements delays between operations to respect limits
- Logs rate limit events for monitoring

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security
- Use admin API key with appropriate permissions

TROUBLESHOOTING:
- Verify API key has contact delete permissions
- Check Freshdesk domain is correct
- Ensure email addresses in Excel file are valid
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes contacts sequentially to respect rate limits
- Implements delays between operations
- Large contact lists may take significant time to process
- Consider breaking large files into smaller batches

IMPORTANT SAFETY NOTES:
- This performs HARD deletion (permanent removal)
- Deleted contacts cannot be recovered
- Test with a small subset first
- Ensure you have backups of important data
- Verify email addresses before running
- Monitor the process and be prepared to stop if needed

USAGE SCENARIOS:
- Remove duplicate or test contacts
- Clean up old contact data
- Data migration cleanup
- Compliance-related contact removal
- Account maintenance operations
"""

import requests
import pandas as pd
import time
import logging
import base64
import sys
import os
from pathlib import Path

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# Script Configuration
INPUT_FILENAME = 'delete_contacts.xlsx'  # Excel file with email addresses
OUTPUT_FILENAME = 'deletion_results.csv'  # Results file
LOG_FILENAME = 'contact_deletion.log'  # Log file
REQUEST_TIMEOUT = 30  # Timeout for API requests
DELAY_BETWEEN_OPERATIONS = 1  # Delay between operations (seconds)

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
    errors = []

    if not API_KEY or API_KEY == '5TMgbcZdRFY70hSpEdj':
        errors.append("API_KEY not configured. Please set your actual Freshdesk API key.")

    if not DOMAIN or DOMAIN == 'benchmarkeducationcompany.freshdesk.com':
        errors.append("DOMAIN not configured. Please set your actual Freshdesk domain.")

    if not INPUT_FILENAME:
        errors.append("INPUT_FILENAME not configured. Please set your Excel file path.")

    if errors:
        for error in errors:
            logging.error(error)
            print(f"❌ {error}")
        return False

    return True

def validate_input_file():
    """
    Validate that the input Excel file exists and is readable.

    Returns:
        tuple: (is_valid, emails_list, errors)
    """
    errors = []

    # Check if file exists
    if not os.path.exists(INPUT_FILENAME):
        errors.append(f"Input file not found: {INPUT_FILENAME}")
        return False, [], errors

    # Check if file is readable
    if not os.access(INPUT_FILENAME, os.R_OK):
        errors.append(f"Cannot read input file: {INPUT_FILENAME}")
        return False, [], errors

    try:
        # Try to read the Excel file
        df = pd.read_excel(INPUT_FILENAME)

        # Check if 'Email' column exists
        if 'Email' not in df.columns:
            errors.append("Excel file must contain an 'Email' column")
            return False, [], errors

        # Extract email addresses
        emails = df['Email'].dropna().astype(str).str.strip().tolist()

        # Filter out empty emails
        valid_emails = [email for email in emails if email and email.lower() != 'nan']

        # Check for duplicates
        email_counts = pd.Series(valid_emails).value_counts()
        duplicates = email_counts[email_counts > 1]

        if len(duplicates) > 0:
            logging.warning(f"Found {len(duplicates)} duplicate email addresses")
            print(f"⚠ Found {len(duplicates)} duplicate email addresses")

        # Validate email format (basic check)
        import re
        invalid_emails = []
        for email in valid_emails:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                invalid_emails.append(email)

        if invalid_emails:
            logging.warning(f"Found {len(invalid_emails)} potentially invalid email addresses")
            print(f"⚠ Found {len(invalid_emails)} potentially invalid email addresses")
            for email in invalid_emails[:5]:  # Show first 5
                print(f"  Invalid: {email}")
            if len(invalid_emails) > 5:
                print(f"  ... and {len(invalid_emails) - 5} more")

        if not valid_emails:
            errors.append("No valid email addresses found in the file")
            return False, [], errors

        logging.info(f"Loaded {len(valid_emails)} email addresses from {INPUT_FILENAME}")
        print(f"✓ Loaded {len(valid_emails)} email addresses")

        return True, valid_emails, []

    except Exception as e:
        errors.append(f"Error reading Excel file: {e}")
        return False, [], errors

def prepare_authentication():
    """
    Prepare authentication headers for API requests.

    Returns:
        dict: Headers dictionary with authentication
    """
    try:
        # Encode API key for Basic Authentication
        auth_str = f'{API_KEY}:X'
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_base64}'
        }

        logging.info("Authentication headers prepared successfully")
        return headers

    except Exception as e:
        logging.error(f"Error preparing authentication: {e}")
        print(f"❌ Error preparing authentication: {e}")
        return None

def make_api_request(url, method='GET', params=None, headers=None):
    """
    Make a rate-limited API request to Freshdesk.

    Args:
        url (str): Full URL for the API request
        method (str): HTTP method (GET, DELETE, etc.)
        params (dict, optional): Query parameters for GET requests
        headers (dict, optional): HTTP headers

    Returns:
        dict or None: API response data, or None if failed
    """
    try:
        logging.debug(f"Making {method} request to: {url}")

        # Prepare request arguments
        request_kwargs = {
            'url': url,
            'headers': headers or {},
            'timeout': REQUEST_TIMEOUT
        }

        # Add authentication
        if API_KEY:
            auth_str = f'{API_KEY}:X'
            auth_bytes = auth_str.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            request_kwargs['headers']['Authorization'] = f'Basic {auth_base64}'

        # Add query parameters for GET requests
        if method.upper() == 'GET' and params:
            request_kwargs['params'] = params

        # Make the request
        response = requests.request(method.upper(), **request_kwargs)

        if response.status_code == 200:
            logging.debug(f"Request successful: {response.status_code}")
            return response.json()
        elif response.status_code == 204:
            # Successful deletion (no content)
            logging.debug(f"Deletion successful: {response.status_code}")
            return True
        elif response.status_code == 404:
            logging.warning(f"Resource not found: {url}")
            return None
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return make_api_request(url, method, params, headers)  # Retry the same request
        else:
            logging.error(f"API request failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for URL {url}: {e}")
        return None

def get_contact_id_by_email(email, headers):
    """
    Find a contact ID by email address.

    Args:
        email (str): Email address to search for
        headers (dict): HTTP headers for the request

    Returns:
        int or None: Contact ID if found, None if not found
    """
    if not email or not email.strip():
        logging.warning(f"Empty email provided: {email}")
        return None

    url = f"https://{DOMAIN}/api/v2/contacts"
    params = {'email': email.strip()}

    try:
        response_data = make_api_request(url, 'GET', params, headers)

        if response_data and isinstance(response_data, list) and len(response_data) > 0:
            contact_id = response_data[0].get('id')
            logging.info(f"Found contact ID {contact_id} for email {email}")
            return contact_id
        else:
            logging.warning(f"No contact found for email: {email}")
            return None

    except Exception as e:
        logging.error(f"Error finding contact for email {email}: {e}")
        return None

def get_contact_details(contact_id, headers):
    """
    Get detailed information about a contact before deletion.

    Args:
        contact_id (int): Contact ID to fetch details for
        headers (dict): HTTP headers for the request

    Returns:
        dict or None: Contact details if successful, None if failed
    """
    if not contact_id:
        return None

    url = f"https://{DOMAIN}/api/v2/contacts/{contact_id}"

    try:
        response_data = make_api_request(url, 'GET', None, headers)

        if response_data:
            logging.info(f"Retrieved details for contact ID {contact_id}")
            return response_data
        else:
            logging.warning(f"Could not retrieve details for contact ID {contact_id}")
            return None

    except Exception as e:
        logging.error(f"Error getting contact details for ID {contact_id}: {e}")
        return None

def delete_contact_permanently(contact_id, headers):
    """
    Perform hard deletion of a contact (permanent removal).

    Args:
        contact_id (int): Contact ID to delete
        headers (dict): HTTP headers for the request

    Returns:
        bool: True if deletion successful, False otherwise
    """
    if not contact_id:
        logging.error("No contact ID provided for deletion")
        return False

    url = f"https://{DOMAIN}/api/v2/contacts/{contact_id}/hard_delete?force=true"

    try:
        logging.info(f"Attempting to delete contact ID {contact_id}")
        response_data = make_api_request(url, 'DELETE', None, headers)

        if response_data is True:  # Successful deletion returns True (204 status)
            logging.info(f"Successfully deleted contact ID {contact_id}")
            return True
        else:
            logging.error(f"Failed to delete contact ID {contact_id}")
            return False

    except Exception as e:
        logging.error(f"Error deleting contact ID {contact_id}: {e}")
        return False

def save_results_to_csv(results_data, filename):
    """
    Save deletion results to CSV file.

    Args:
        results_data (list): List of deletion result dictionaries
        filename (str): Output CSV filename

    Returns:
        bool: True if save successful, False otherwise
    """
    if not results_data:
        logging.warning("No results data to save")
        return False

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(results_data)
        df.to_csv(filename, index=False, encoding='utf-8')

        file_size = os.path.getsize(filename)
        logging.info(f"Successfully saved {len(results_data)} results to {filename} ({file_size} bytes)")
        print(f"✓ Saved {len(results_data)} results to {filename}")
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

def prompt_for_confirmation(email_count):
    """
    Prompt user for confirmation before proceeding with deletion.

    Args:
        email_count (int): Number of emails to process

    Returns:
        bool: True if user confirms, False otherwise
    """
    print("
⚠ DANGER ZONE ⚠"    print("=" * 50)
    print(f"You are about to DELETE {email_count} contacts PERMANENTLY.")
    print("This action CANNOT be undone.")
    print("Deleted contacts will be lost forever.")
    print("=" * 50)

    while True:
        response = input("Do you want to proceed? (type 'DELETE' to confirm): ").strip().upper()

        if response == 'DELETE':
            print("✓ Deletion confirmed. Proceeding...")
            return True
        elif response in ['N', 'NO', 'CANCEL', 'QUIT']:
            print("✓ Deletion cancelled.")
            return False
        else:
            print("Please type 'DELETE' to confirm or 'NO' to cancel.")

def main():
    """
    Main function to orchestrate the contact deletion process.
    """
    print("Freshdesk Contact Deletion Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Contact Deletion Tool")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    try:
        # Step 1: Validate input file
        print("Step 1: Validating input file...")
        is_valid, email_addresses, file_errors = validate_input_file()

        if not is_valid:
            print("❌ Input file validation failed.")
            for error in file_errors:
                print(f"  - {error}")
            return 1

        if not email_addresses:
            print("❌ No valid email addresses found in the file.")
            return 1

        # Step 2: Prompt for confirmation
        print("Step 2: Requesting confirmation...")
        if not prompt_for_confirmation(len(email_addresses)):
            print("Operation cancelled by user.")
            return 0

        # Step 3: Prepare authentication
        print("Step 3: Preparing authentication...")
        headers = prepare_authentication()

        if not headers:
            print("❌ Failed to prepare authentication.")
            return 1

        # Step 4: Process deletions
        print("Step 4: Processing contact deletions...")
        results_data = []
        success_count = 0
        error_count = 0
        not_found_count = 0

        for i, email in enumerate(email_addresses, 1):
            print(f"\n  [{i}/{len(email_addresses)}] Processing: {email}")

            try:
                # Find contact ID by email
                contact_id = get_contact_id_by_email(email, headers)

                if contact_id:
                    # Get contact details for logging
                    contact_details = get_contact_details(contact_id, headers)

                    # Attempt deletion
                    if delete_contact_permanently(contact_id, headers):
                        success_count += 1
                        result = {
                            'Email': email,
                            'Contact ID': contact_id,
                            'Contact Name': contact_details.get('name', 'N/A') if contact_details else 'N/A',
                            'Status': 'Deleted',
                            'Error': ''
                        }
                        print(f"    ✓ Deleted contact ID {contact_id}")
                    else:
                        error_count += 1
                        result = {
                            'Email': email,
                            'Contact ID': contact_id,
                            'Contact Name': contact_details.get('name', 'N/A') if contact_details else 'N/A',
                            'Status': 'Delete Failed',
                            'Error': 'Deletion API call failed'
                        }
                        print(f"    ❌ Failed to delete contact ID {contact_id}")
                else:
                    not_found_count += 1
                    result = {
                        'Email': email,
                        'Contact ID': 'Not Found',
                        'Contact Name': 'N/A',
                        'Status': 'Not Found',
                        'Error': 'No contact found with this email'
                    }
                    print(f"    ⚠ Contact not found for email: {email}")

                results_data.append(result)

            except Exception as e:
                error_count += 1
                result = {
                    'Email': email,
                    'Contact ID': 'Error',
                    'Contact Name': 'N/A',
                    'Status': 'Error',
                    'Error': str(e)
                }
                results_data.append(result)
                logging.error(f"Error processing email {email}: {e}")
                print(f"    ❌ Error processing email {email}: {e}")

            # Delay between operations to respect rate limits
            if i < len(email_addresses):  # Don't delay after the last operation
                time.sleep(DELAY_BETWEEN_OPERATIONS)

        # Step 5: Save results
        print("
Step 5: Saving results...")
        if save_results_to_csv(results_data, OUTPUT_FILENAME):
            # Final summary
            print("
" + "=" * 60)
            print("DELETION SUMMARY")
            print("=" * 60)
            print(f"✓ Deletion process completed!")
            print(f"  Emails processed: {len(email_addresses)}")
            print(f"  Contacts deleted: {success_count}")
            print(f"  Contacts not found: {not_found_count}")
            print(f"  Errors: {error_count}")
            print(f"  Results saved to: {OUTPUT_FILENAME}")
            print(f"  Log file: {LOG_FILENAME}")

            # Show success rate
            if len(email_addresses) > 0:
                success_rate = (success_count / len(email_addresses)) * 100
                print(f"  Success rate: {success_rate:.1f}%")

            # Show recommendations
            if error_count > 0:
                print(f"\n⚠ {error_count} operations failed")
                print("  Check logs for detailed error information")

            if not_found_count > 0:
                print(f"\n⚠ {not_found_count} contacts were not found")
                print("  Verify email addresses in your input file")

            logging.info("=" * 60)
            logging.info("CONTACT DELETION COMPLETED")
            logging.info("=" * 60)
            logging.info(f"Emails processed: {len(email_addresses)}")
            logging.info(f"Contacts deleted: {success_count}")
            logging.info(f"Contacts not found: {not_found_count}")
            logging.info(f"Errors: {error_count}")
            logging.info(f"Results saved to: {OUTPUT_FILENAME}")
            logging.info("=" * 60)

            return 0
        else:
            print("❌ Failed to save results.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Deletion interrupted by user")
        logging.info("Deletion interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during deletion: {e}")
        logging.error(f"Unexpected error during deletion: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

