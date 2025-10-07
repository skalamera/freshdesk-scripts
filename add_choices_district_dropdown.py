"""
Freshdesk Custom Field Dropdown Choices Addition Script

DESCRIPTION:
This script adds multiple choices to a Freshdesk custom field dropdown in
batches with proper rate limiting and error handling. It's designed for bulk
operations when you need to add many options to dropdown-type custom fields
like district selections, categories, or other choice-based fields.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with admin/ticket field write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update FIELD_ID with the ID of the custom field you want to modify
4. Update NEW_CHOICES list with the choices you want to add
5. Ensure your API key has admin permissions for ticket field management
6. Run the script: python add_choices_district_dropdown.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Admin Ticket Fields API: https://developers.freshdesk.com/api/#admin-ticket-fields
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- FIELD_ID: ID of the custom field to modify
- NEW_CHOICES: List of new choices to add
- BATCH_SIZE: Number of choices to add per API call
- DELAY_BETWEEN_BATCHES: Delay between batch operations

OUTPUT:
- Console output showing batch processing progress
- Detailed logging for troubleshooting
- Summary of successful/failed operations

BATCH PROCESSING FEATURES:
- Processes choices in configurable batch sizes
- Maintains existing choices while adding new ones
- Handles rate limiting automatically
- Provides retry logic for failed batches
- Tracks progress across multiple batches

SUPPORTED FIELD TYPES:
- Dropdown/select field types
- Multi-select field types
- Checkbox field types (for adding new options)

ERROR HANDLING:
- Handles HTTP 404 (field not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates field exists before processing
- Continues processing even if individual batches fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Implements delays between batches to respect limits
- Configurable batch sizes to manage API load

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security
- Use admin API key with appropriate permissions

TROUBLESHOOTING:
- Verify API key has admin/ticket field write permissions
- Check that FIELD_ID is correct (find in Freshdesk admin panel)
- Ensure the custom field type supports choice addition
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes choices in small batches to avoid timeouts
- Configurable delays between operations
- Large numbers of choices may take significant time to process
- Consider breaking very large lists into multiple runs

USAGE SCENARIOS:
- Add multiple districts to a district dropdown field
- Populate category options for categorization fields
- Add product codes or service types to selection fields
- Bulk update field options during data migration
- Maintain field choices across multiple environments

IMPORTANT NOTES:
- This adds values to existing choices, doesn't replace them
- Some field types may not support dynamic choice addition
- Changes may take time to reflect in ticket forms
- Test in a development environment first
- Monitor API rate limits during large operations
"""

import requests
import time
import base64
import logging
import sys
import os
from pathlib import Path

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompanysandbox'  # Replace with your domain
FIELD_ID = '1067000960667'  # Replace with your custom field ID

# Processing Configuration
BATCH_SIZE = 2  # Number of choices to add per API call
DELAY_BETWEEN_BATCHES = 5  # Seconds to wait between batches
MAX_RETRIES_PER_BATCH = 3  # Maximum retries for failed batches
REQUEST_TIMEOUT = 30  # Timeout for API requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('field_choices_update.log', encoding='utf-8'),
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

    if not DOMAIN or DOMAIN == 'benchmarkeducationcompanysandbox':
        errors.append("DOMAIN not configured. Please set your actual Freshdesk domain.")

    if not FIELD_ID:
        errors.append("FIELD_ID not configured. Please set your custom field ID.")

    if errors:
        for error in errors:
            logging.error(error)
            print(f"❌ {error}")
        return False

    return True

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

def make_api_request(url, method='GET', data=None, headers=None):
    """
    Make a rate-limited API request to Freshdesk.

    Args:
        url (str): Full URL for the API request
        method (str): HTTP method (GET, PUT, etc.)
        data (dict, optional): JSON data for POST/PUT requests
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

        # Add data for POST/PUT requests
        if method.upper() in ['POST', 'PUT'] and data:
            request_kwargs['json'] = data

        # Make the request
        response = requests.request(method.upper(), **request_kwargs)

        if response.status_code == 200:
            logging.debug(f"Request successful: {response.status_code}")
            return response.json()
        elif response.status_code == 404:
            logging.warning(f"Resource not found: {url}")
            return None
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return make_api_request(url, method, data, headers)  # Retry the same request
        else:
            logging.error(f"API request failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for URL {url}: {e}")
        return None

def get_field_details(field_id):
    """
    Retrieve details about the custom field to understand its current configuration.

    Args:
        field_id (str): The field ID to fetch details for

    Returns:
        dict or None: Field details if successful, None if failed
    """
    url = f"https://{DOMAIN}/api/v2/admin/ticket_fields/{field_id}"

    try:
        logging.info(f"Fetching field details for field ID: {field_id}")
        response_data = make_api_request(url, 'GET')

        if response_data:
            field_name = response_data.get('name', 'Unknown Field')
            field_type = response_data.get('type', 'Unknown')
            current_choices = response_data.get('choices', [])

            logging.info(f"Successfully retrieved field details: {field_name} ({field_type})")
            print(f"✓ Field found: {field_name} ({field_type})")
            print(f"  Current choices: {len(current_choices)}")

            return response_data
        else:
            logging.error(f"Field ID {field_id} not found or inaccessible")
            print(f"❌ Field ID {field_id} not found or inaccessible")
            return None

    except Exception as e:
        logging.error(f"Error fetching field details: {e}")
        print(f"❌ Error fetching field details: {e}")
        return None

def fetch_existing_choices(field_id):
    """
    Fetch the current choices for a custom field.

    Args:
        field_id (str): The field ID to fetch choices for

    Returns:
        list: List of existing choices, or empty list if failed
    """
    field_details = get_field_details(field_id)

    if field_details:
        choices = field_details.get('choices', [])
        logging.info(f"Fetched {len(choices)} existing choices")
        return choices
    else:
        logging.error("Could not fetch existing choices due to field access error")
        return []

def validate_choices_to_add(choices_list):
    """
    Validate the list of choices to add.

    Args:
        choices_list (list): List of choices to validate

    Returns:
        tuple: (is_valid, cleaned_choices, errors)
    """
    if not choices_list:
        return False, [], ["No choices provided"]

    errors = []
    cleaned_choices = []
    seen_choices = set()

    for i, choice in enumerate(choices_list):
        # Validate choice is not empty
        if not choice or not str(choice).strip():
            errors.append(f"Choice {i+1}: Empty or invalid choice")
            continue

        # Clean the choice (strip whitespace)
        cleaned_choice = str(choice).strip()

        # Check for duplicates within the new choices
        if cleaned_choice in seen_choices:
            errors.append(f"Choice '{cleaned_choice}': Duplicate choice in input list")
            continue

        seen_choices.add(cleaned_choice)
        cleaned_choices.append(cleaned_choice)

    if errors:
        logging.warning(f"Validation found {len(errors)} issues with choices")
        for error in errors[:5]:  # Show first 5 errors
            print(f"⚠ {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more validation issues")

    return len(cleaned_choices) > 0, cleaned_choices, errors

def update_custom_field_choices(field_id, existing_choices, new_choices_to_add):
    """
    Update a custom field by adding new choices in batches.

    Args:
        field_id (str): The field ID to update
        existing_choices (list): Current choices in the field
        new_choices_to_add (list): New choices to add

    Returns:
        bool: True if update successful, False otherwise
    """
    if not new_choices_to_add:
        logging.warning("No new choices to add")
        print("⚠ No new choices to add")
        return True

    # Check for duplicates between existing and new choices
    duplicate_count = 0
    unique_new_choices = []

    for choice in new_choices_to_add:
        if choice not in existing_choices:
            unique_new_choices.append(choice)
        else:
            duplicate_count += 1

    if duplicate_count > 0:
        logging.warning(f"Found {duplicate_count} duplicate choices (skipping)")
        print(f"⚠ Found {duplicate_count} duplicate choices (skipping)")

    if not unique_new_choices:
        logging.info("All provided choices already exist in the field")
        print("✓ All provided choices already exist in the field")
        return True

    print(f"Adding {len(unique_new_choices)} new unique choices in batches...")

    # Combine existing and new choices
    updated_choices = existing_choices + unique_new_choices

    # Process in batches
    total_batches = (len(unique_new_choices) + BATCH_SIZE - 1) // BATCH_SIZE
    success_count = 0
    error_count = 0

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(unique_new_choices))
        batch = unique_new_choices[start_idx:end_idx]

        # Create current state of choices (existing + all previous batches)
        current_choices = existing_choices + unique_new_choices[:start_idx + len(batch)]

        print(f"  Processing batch {batch_num + 1}/{total_batches} ({len(batch)} choices)")

        success = update_field_batch(field_id, current_choices, batch_num + 1)

        if success:
            success_count += 1
        else:
            error_count += 1

        # Delay between batches to respect rate limits
        if batch_num < total_batches - 1:  # Don't delay after the last batch
            print(f"  Waiting {DELAY_BETWEEN_BATCHES} seconds before next batch...")
            time.sleep(DELAY_BETWEEN_BATCHES)

    print(f"\n✓ Batch processing complete: {success_count} successful, {error_count} failed")

    if error_count == 0:
        logging.info(f"Successfully added all {len(unique_new_choices)} new choices")
        print(f"✓ Successfully added all {len(unique_new_choices)} new choices")
        return True
    else:
        logging.warning(f"Added {len(unique_new_choices) - (error_count * BATCH_SIZE)} choices, {error_count * BATCH_SIZE} failed")
        print(f"⚠ Added {len(unique_new_choices) - (error_count * BATCH_SIZE)} choices, {error_count * BATCH_SIZE} failed")
        return False

def update_field_batch(field_id, current_choices, batch_number):
    """
    Update a single batch of field choices.

    Args:
        field_id (str): The field ID to update
        current_choices (list): Current complete list of choices
        batch_number (int): Batch number for logging

    Returns:
        bool: True if update successful, False otherwise
    """
    url = f"https://{DOMAIN}/api/v2/admin/ticket_fields/{field_id}"

    # Prepare the update payload
    update_payload = {
        'choices': current_choices
    }

    retry_count = 0

    while retry_count < MAX_RETRIES_PER_BATCH:
        try:
            logging.info(f"Updating field {field_id} with batch {batch_number} ({len(current_choices)} total choices)")
            response = requests.put(url, json=update_payload, auth=(API_KEY, 'X'), timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                logging.info(f"Batch {batch_number} updated successfully")
                return True
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logging.warning(f"Rate limit hit for batch {batch_number}. Retrying after {retry_after} seconds...")
                print(f"⏳ Rate limit reached for batch {batch_number}. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                retry_count += 1
                continue
            else:
                logging.error(f"Failed to update batch {batch_number}: {response.status_code} - {response.text}")
                print(f"❌ Failed to update batch {batch_number}: {response.status_code}")
                retry_count += 1

                if retry_count < MAX_RETRIES_PER_BATCH:
                    wait_time = 2 * retry_count  # Exponential backoff
                    print(f"  Retrying batch {batch_number} in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"  Max retries reached for batch {batch_number}")
                    return False

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error for batch {batch_number}: {e}")
            print(f"❌ Network error for batch {batch_number}: {e}")
            retry_count += 1

            if retry_count < MAX_RETRIES_PER_BATCH:
                wait_time = 2 * retry_count
                print(f"  Retrying batch {batch_number} in {wait_time} seconds...")
                time.sleep(wait_time)

    return False

def load_choices_from_file(filename):
    """
    Load choices from a text file (one choice per line).

    Args:
        filename (str): Path to the file containing choices

    Returns:
        list: List of choices, or empty list if failed
    """
    try:
        if not os.path.exists(filename):
            logging.error(f"Choices file not found: {filename}")
            print(f"❌ Choices file not found: {filename}")
            return []

        choices = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                choice = line.strip()
                if choice and not choice.startswith('#'):  # Skip empty lines and comments
                    choices.append(choice)

        logging.info(f"Loaded {len(choices)} choices from {filename}")
        print(f"✓ Loaded {len(choices)} choices from {filename}")
        return choices

    except Exception as e:
        logging.error(f"Error loading choices from file: {e}")
        print(f"❌ Error loading choices from file: {e}")
        return []

def main():
    """
    Main function to orchestrate the custom field choices addition process.
    """
    print("Freshdesk Custom Field Choices Addition Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Custom Field Choices Addition")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    try:
        # Step 1: Get field details and validate access
        print("Step 1: Validating field access...")
        field_details = get_field_details(FIELD_ID)

        if not field_details:
            print("❌ Cannot access the specified field. Please check:")
            print("  - Field ID is correct")
            print("  - API key has admin permissions")
            print("  - Field exists in your Freshdesk account")
            return 1

        field_name = field_details.get('name', 'Unknown Field')
        field_type = field_details.get('type', 'Unknown')

        print(f"✓ Field validated: {field_name} ({field_type})")

        # Step 2: Fetch existing choices
        print("Step 2: Fetching existing choices...")
        existing_choices = fetch_existing_choices(FIELD_ID)

        if existing_choices is None:
            print("❌ Failed to fetch existing choices.")
            return 1

        print(f"✓ Found {len(existing_choices)} existing choices")

        # Step 3: Prepare new choices to add
        print("Step 3: Preparing new choices...")

        # Example new choices - replace this with your actual data
        new_choices = [f'New District {i}' for i in range(1, 2001)]

        # Alternative: Load from file if you have a choices file
        # new_choices = load_choices_from_file('district_choices.txt')

        print(f"✓ Prepared {len(new_choices)} new choices to add")

        # Validate choices
        is_valid, cleaned_choices, validation_errors = validate_choices_to_add(new_choices)

        if not is_valid:
            print("❌ No valid choices to add after validation.")
            return 1

        if validation_errors:
            print(f"⚠ Found {len(validation_errors)} validation issues (continuing with valid choices)")

        print(f"✓ {len(cleaned_choices)} valid choices ready for addition")

        # Step 4: Update field with new choices
        print("Step 4: Adding choices to field...")
        success = update_custom_field_choices(FIELD_ID, existing_choices, cleaned_choices)

        if success:
            # Final verification
            print("Step 5: Verifying final state...")
            final_choices = fetch_existing_choices(FIELD_ID)

            if final_choices and len(final_choices) >= len(existing_choices) + len(cleaned_choices):
                print("
" + "=" * 60)
                print("OPERATION SUMMARY")
                print("=" * 60)
                print(f"✓ Operation completed successfully!")
                print(f"  Field: {field_name}")
                print(f"  Field Type: {field_type}")
                print(f"  Original choices: {len(existing_choices)}")
                print(f"  New choices added: {len(cleaned_choices)}")
                print(f"  Final choices: {len(final_choices)}")
                print(f"  Log file: field_choices_update.log")

                logging.info("=" * 60)
                logging.info("FIELD CHOICES ADDITION COMPLETED SUCCESSFULLY")
                logging.info("=" * 60)
                logging.info(f"Field: {field_name}")
                logging.info(f"Original choices: {len(existing_choices)}")
                logging.info(f"New choices added: {len(cleaned_choices)}")
                logging.info(f"Final choices: {len(final_choices)}")
                logging.info("=" * 60)

                return 0
            else:
                print("❌ Verification failed. Final choice count doesn't match expected.")
                return 1
        else:
            print("❌ Failed to add choices. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Operation interrupted by user")
        logging.info("Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during operation: {e}")
        logging.error(f"Unexpected error during operation: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

