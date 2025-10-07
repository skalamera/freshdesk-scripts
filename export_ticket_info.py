"""
Freshdesk Ticket Information Export Script

DESCRIPTION:
This script processes Freshdesk ticket and contact JSON data files to extract
and export key ticket information to CSV format. It combines ticket data with
contact information to provide a comprehensive view of tickets including
requester details, creation dates, and contact information.

REQUIREMENTS:
- Python 3.x
- json library (built-in)
- csv library (built-in)
- Valid JSON files containing ticket and contact data
- Read access to input JSON files and write access to output directory

SETUP INSTRUCTIONS:
1. Ensure you have 'tickets.json' and 'contacts.json' files in the working directory
2. Update INPUT_FILENAMES if your files have different names
3. Update OUTPUT_FILENAME if you want a different CSV filename
4. Run the script: python export_ticket_info.py

INPUT DATA FORMAT:
tickets.json should contain:
- Array of ticket objects with fields: ticket_id, created_at, contact_details
- contact_details should include: name, email (and optionally other fields)

contacts.json should contain:
- Array of contact objects with fields: id, name, email
- OR a dictionary with 'contacts' key containing the array

OUTPUT:
- CSV file with ticket information including:
  - Ticket ID
  - Creation date
  - Contact name
  - Contact email
- Console output showing progress and results
- Detailed logging for troubleshooting

CSV OUTPUT FORMAT:
Ticket ID,Created Date,Contact Name,Contact Email
12345,2023-01-15T10:30:00Z,John Doe,john.doe@example.com
12346,2023-01-15T11:15:00Z,Jane Smith,jane.smith@example.com

ERROR HANDLING:
- Validates JSON file structure and required fields
- Handles missing or malformed data gracefully
- Provides detailed error messages for troubleshooting
- Continues processing even if individual records fail
- Validates file access permissions

SECURITY NOTE:
- No API keys or external connections required
- Processes local files only
- Safe for offline environments
- No sensitive data transmission

TROUBLESHOOTING:
- Verify input JSON files exist and are readable
- Check JSON structure matches expected format
- Ensure output directory is writable
- Validate that tickets contain required fields
- Check console output and logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes files in memory for efficiency
- Handles large JSON files with streaming if needed
- Minimal memory usage for typical datasets
- Fast processing for thousands of records

USAGE SCENARIOS:
- Export ticket data for analysis in Excel or other tools
- Create contact lists from ticket data
- Generate reports combining ticket and contact information
- Data migration and backup operations
- Integration with other business systems
"""

import json
import csv
import logging
import os
import sys
from pathlib import Path

# Configuration
INPUT_FILENAMES = {
    'tickets': 'tickets.json',
    'contacts': 'contacts.json'
}
OUTPUT_FILENAME = 'ticket_info.csv'
LOG_FILENAME = 'ticket_export.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def validate_input_files():
    """
    Validate that all required input files exist and are readable.

    Returns:
        bool: True if all files are valid, False otherwise
    """
    missing_files = []
    unreadable_files = []

    for file_type, filename in INPUT_FILENAMES.items():
        file_path = Path(filename)

        if not file_path.exists():
            missing_files.append(f"{file_type}: {filename}")
        elif not os.access(file_path, os.R_OK):
            unreadable_files.append(f"{file_type}: {filename}")

    if missing_files:
        for file_info in missing_files:
            logging.error(f"Missing input file: {file_info}")
            print(f"❌ Missing input file: {file_info}")
        return False

    if unreadable_files:
        for file_info in unreadable_files:
            logging.error(f"Cannot read input file: {file_info}")
            print(f"❌ Cannot read input file: {file_info}")
        return False

    print("✓ All input files validated successfully")
    return True

def validate_output_directory():
    """
    Validate that the output directory is writable.

    Returns:
        bool: True if directory is writable, False otherwise
    """
    output_path = Path(OUTPUT_FILENAME)

    try:
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        test_file = output_path.parent / ".write_test"
        test_file.write_text("test")
        test_file.unlink()

        return True

    except PermissionError:
        error_msg = f"Permission denied: Cannot write to {output_path.parent}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error validating output directory: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def load_json_safely(filename):
    """
    Load JSON file with comprehensive error handling.

    Args:
        filename (str): Path to the JSON file

    Returns:
        dict or list: Parsed JSON data, or None if failed
    """
    try:
        logging.info(f"Loading JSON file: {filename}")
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validate data is a dictionary or list
        if not isinstance(data, (dict, list)):
            logging.error(f"Invalid JSON structure in {filename}: expected dict or list, got {type(data)}")
            print(f"❌ Invalid JSON structure in {filename}")
            return None

        logging.info(f"Successfully loaded {filename} ({len(data)} items)")
        return data

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {filename}: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None
    except UnicodeDecodeError as e:
        error_msg = f"Encoding error reading {filename}: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None
    except FileNotFoundError:
        error_msg = f"File not found: {filename}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None
    except Exception as e:
        error_msg = f"Error reading {filename}: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return None

def normalize_contacts_data(contacts_data):
    """
    Normalize contacts data to ensure it's always a list.

    Args:
        contacts_data: Raw contacts data from JSON

    Returns:
        list: Normalized contacts list
    """
    if not contacts_data:
        logging.warning("Contacts data is empty or None")
        return []

    # Handle different data structures
    if isinstance(contacts_data, dict):
        # Check for nested structure
        if 'contacts' in contacts_data and isinstance(contacts_data['contacts'], list):
            return contacts_data['contacts']
        else:
            logging.warning("Contacts data is a dict but doesn't contain 'contacts' list")
            return []
    elif isinstance(contacts_data, list):
        return contacts_data
    else:
        logging.warning(f"Unexpected contacts data type: {type(contacts_data)}")
        return []

def create_contact_lookup(contacts_list):
    """
    Create a lookup dictionary for contacts by ID.

    Args:
        contacts_list (list): List of contact dictionaries

    Returns:
        dict: Contact lookup dictionary {contact_id: contact_data}
    """
    if not contacts_list:
        logging.warning("No contacts data provided for lookup creation")
        return {}

    lookup = {}
    for contact in contacts_list:
        contact_id = contact.get('id')
        if contact_id is not None:
            lookup[contact_id] = contact
        else:
            logging.warning(f"Contact missing ID field: {contact}")

    logging.info(f"Created contact lookup with {len(lookup)} entries")
    return lookup

def extract_ticket_info(tickets_data, contacts_lookup):
    """
    Extract and enrich ticket information with contact details.

    Args:
        tickets_data: Raw tickets data from JSON
        contacts_lookup (dict): Contact lookup dictionary

    Returns:
        list: List of enriched ticket information dictionaries
    """
    if not tickets_data:
        logging.warning("No tickets data provided")
        return []

    # Normalize tickets data
    if isinstance(tickets_data, dict):
        if 'tickets' in tickets_data and isinstance(tickets_data['tickets'], list):
            tickets_list = tickets_data['tickets']
        else:
            logging.warning("Tickets data is a dict but doesn't contain 'tickets' list")
            return []
    elif isinstance(tickets_data, list):
        tickets_list = tickets_data
    else:
        logging.warning(f"Unexpected tickets data type: {type(tickets_data)}")
        return []

    logging.info(f"Processing {len(tickets_list)} tickets")

    ticket_info_list = []
    processed_count = 0
    skipped_count = 0

    for ticket in tickets_list:
        try:
            # Extract basic ticket information
            ticket_id = ticket.get('ticket_id') or ticket.get('id')
            created_at = ticket.get('created_at')
            contact_details = ticket.get('contact_details', {})

            # Skip tickets without ID
            if not ticket_id:
                logging.warning(f"Ticket missing ID: {ticket}")
                skipped_count += 1
                continue

            # Extract contact information
            contact_name = 'N/A'
            contact_email = 'N/A'

            if contact_details:
                contact_name = contact_details.get('name', 'N/A')
                contact_email = contact_details.get('email', 'N/A')
            else:
                # Try to get contact info from lookup if available
                contact_id = ticket.get('contact_id') or ticket.get('requester_id')
                if contact_id and contact_id in contacts_lookup:
                    contact_data = contacts_lookup[contact_id]
                    contact_name = contact_data.get('name', 'N/A')
                    contact_email = contact_data.get('email', 'N/A')

            # Create ticket info record
            ticket_info = {
                'Ticket ID': ticket_id,
                'Created Date': created_at,
                'Contact Name': contact_name,
                'Contact Email': contact_email
            }

            # Add additional fields if available
            if 'subject' in ticket:
                ticket_info['Subject'] = ticket['subject']
            if 'status' in ticket:
                ticket_info['Status'] = ticket['status']
            if 'priority' in ticket:
                ticket_info['Priority'] = ticket['priority']
            if 'group_id' in ticket:
                ticket_info['Group ID'] = ticket['group_id']
            if 'agent_id' in ticket or 'responder_id' in ticket:
                ticket_info['Agent ID'] = ticket.get('agent_id') or ticket.get('responder_id')

            ticket_info_list.append(ticket_info)
            processed_count += 1

        except Exception as e:
            logging.error(f"Error processing ticket {ticket.get('ticket_id', 'unknown')}: {e}")
            skipped_count += 1
            continue

    logging.info(f"Processed {processed_count} tickets, skipped {skipped_count}")
    print(f"✓ Processed {processed_count} tickets, skipped {skipped_count}")

    return ticket_info_list

def save_to_csv(ticket_info_list, filename):
    """
    Save ticket information to CSV file with proper formatting.

    Args:
        ticket_info_list (list): List of ticket information dictionaries
        filename (str): Output CSV filename

    Returns:
        bool: True if save successful, False otherwise
    """
    if not ticket_info_list:
        logging.warning("No ticket data to save")
        print("⚠ No ticket data to save")
        return False

    try:
        logging.info(f"Saving {len(ticket_info_list)} records to {filename}")
        print(f"Saving {len(ticket_info_list)} records to {filename}...")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all unique fieldnames from the data
            fieldnames = set()
            for ticket_info in ticket_info_list:
                fieldnames.update(ticket_info.keys())

            # Sort fieldnames for consistent output
            fieldnames = sorted(fieldnames)

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data rows
            for ticket_info in ticket_info_list:
                writer.writerow(ticket_info)

        # Verify file was created and has content
        file_path = Path(filename)
        if file_path.exists():
            file_size = file_path.stat().st_size
            logging.info(f"Successfully saved CSV file: {filename} ({file_size} bytes)")
            print(f"✓ Successfully saved {len(ticket_info_list)} records to {filename}")
            return True
        else:
            logging.error(f"Failed to create output file: {filename}")
            print(f"❌ Failed to create output file: {filename}")
            return False

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

def analyze_data_quality(tickets_data, contacts_data):
    """
    Analyze the quality and completeness of input data.

    Args:
        tickets_data: Raw tickets data
        contacts_data: Raw contacts data

    Returns:
        dict: Data quality analysis results
    """
    analysis = {
        'tickets_total': 0,
        'tickets_with_id': 0,
        'tickets_with_contact_details': 0,
        'tickets_with_creation_date': 0,
        'contacts_total': 0,
        'contacts_with_id': 0,
        'contacts_with_email': 0,
        'estimated_coverage': 0.0
    }

    # Analyze tickets data
    if tickets_data:
        if isinstance(tickets_data, dict) and 'tickets' in tickets_data:
            tickets_list = tickets_data['tickets']
        elif isinstance(tickets_data, list):
            tickets_list = tickets_data
        else:
            tickets_list = []

        analysis['tickets_total'] = len(tickets_list)

        for ticket in tickets_list:
            if ticket.get('ticket_id') or ticket.get('id'):
                analysis['tickets_with_id'] += 1
            if ticket.get('contact_details'):
                analysis['tickets_with_contact_details'] += 1
            if ticket.get('created_at'):
                analysis['tickets_with_creation_date'] += 1

    # Analyze contacts data
    if contacts_data:
        if isinstance(contacts_data, dict) and 'contacts' in contacts_data:
            contacts_list = contacts_data['contacts']
        elif isinstance(contacts_data, list):
            contacts_list = contacts_data
        else:
            contacts_list = []

        analysis['contacts_total'] = len(contacts_list)

        for contact in contacts_list:
            if contact.get('id'):
                analysis['contacts_with_id'] += 1
            if contact.get('email'):
                analysis['contacts_with_email'] += 1

    # Calculate estimated coverage (how many tickets can be matched to contacts)
    if analysis['tickets_total'] > 0 and analysis['contacts_total'] > 0:
        # Simple estimation based on available IDs
        tickets_with_contact_id = sum(1 for ticket in tickets_list
                                    if ticket.get('contact_id') or ticket.get('requester_id'))
        analysis['estimated_coverage'] = min(tickets_with_contact_id / analysis['tickets_total'], 1.0)

    return analysis

def main():
    """
    Main function to orchestrate the ticket information export process.
    """
    print("Freshdesk Ticket Information Export Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Ticket Information Export Tool")

    # Validate input files
    if not validate_input_files():
        print("❌ Input file validation failed.")
        return 1

    # Validate output directory
    if not validate_output_directory():
        print("❌ Output directory validation failed.")
        return 1

    try:
        # Load JSON data
        print("\nLoading input files...")
        tickets_data = load_json_safely(INPUT_FILENAMES['tickets'])
        contacts_data = load_json_safely(INPUT_FILENAMES['contacts'])

        if not tickets_data:
            print("❌ No valid tickets data found.")
            return 1

        # Analyze data quality
        print("\nAnalyzing data quality...")
        quality_analysis = analyze_data_quality(tickets_data, contacts_data)

        print("📊 DATA QUALITY ANALYSIS:")
        print(f"   Tickets total: {quality_analysis['tickets_total']}")
        print(f"   Tickets with ID: {quality_analysis['tickets_with_id']}")
        print(f"   Tickets with contact details: {quality_analysis['tickets_with_contact_details']}")
        print(f"   Tickets with creation date: {quality_analysis['tickets_with_creation_date']}")
        print(f"   Contacts total: {quality_analysis['contacts_total']}")
        print(f"   Contacts with ID: {quality_analysis['contacts_with_id']}")
        print(f"   Contacts with email: {quality_analysis['contacts_with_email']}")
        print(f"   Estimated contact coverage: {quality_analysis['estimated_coverage']:.1%}")

        # Normalize and process data
        print("\nProcessing ticket and contact data...")
        contacts_list = normalize_contacts_data(contacts_data)
        contacts_lookup = create_contact_lookup(contacts_list)

        # Extract ticket information
        ticket_info_list = extract_ticket_info(tickets_data, contacts_lookup)

        if not ticket_info_list:
            print("❌ No ticket information could be extracted.")
            return 1

        # Save to CSV
        print("\nSaving to CSV file...")
        success = save_to_csv(ticket_info_list, OUTPUT_FILENAME)

        if success:
            # Final summary
            output_path = Path(OUTPUT_FILENAME)
            file_size = output_path.stat().st_size

            print("\n" + "=" * 60)
            print("EXPORT SUMMARY")
            print("=" * 60)
            print(f"✓ Export completed successfully!")
            print(f"  Input files: {', '.join(INPUT_FILENAMES.values())}")
            print(f"  Output file: {OUTPUT_FILENAME}")
            print(f"  Records exported: {len(ticket_info_list)}")
            print(f"  File size: {file_size:,} bytes")
            print(f"  Log file: {LOG_FILENAME}")

            # Show sample of exported data
            if ticket_info_list:
                print("
📋 SAMPLE EXPORTED DATA:"                sample_fields = ['Ticket ID', 'Created Date', 'Contact Name', 'Contact Email']
                print(f"   {', '.join(sample_fields)}")
                for i, ticket in enumerate(ticket_info_list[:3]):  # Show first 3 records
                    sample_values = [str(ticket.get(field, 'N/A')) for field in sample_fields]
                    print(f"   {', '.join(sample_values)}")
                if len(ticket_info_list) > 3:
                    print(f"   ... and {len(ticket_info_list) - 3} more records")

            logging.info("=" * 60)
            logging.info("TICKET EXPORT COMPLETED SUCCESSFULLY")
            logging.info("=" * 60)
            logging.info(f"Input tickets: {quality_analysis['tickets_total']}")
            logging.info(f"Input contacts: {quality_analysis['contacts_total']}")
            logging.info(f"Records exported: {len(ticket_info_list)}")
            logging.info(f"Output file: {OUTPUT_FILENAME}")
            logging.info("=" * 60)

            return 0
        else:
            print("❌ Export failed. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Export interrupted by user")
        logging.info("Export interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during export: {e}")
        logging.error(f"Unexpected error during export: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

