"""
Freshdesk Test Ticket Creation GUI

DESCRIPTION:
This script provides a graphical user interface (GUI) for creating test tickets
in Freshdesk with company and contact management. It allows users to select
specific test cases and automatically creates the necessary companies and
contacts before creating the tickets.

Freshdesk is a cloud-based customer support platform that helps businesses
manage customer inquiries, support requests, and service tickets through a
unified interface.

REQUIREMENTS:
- Python 3.x
- tkinter (usually included with Python)
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket, contact, and company creation permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for:
   - Ticket creation and management
   - Contact creation and management
   - Company creation and management
4. Run the script: python create_test_ticket.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

FEATURES:
- Creates or updates companies and contacts as needed
- Provides GUI for selecting which test cases to run
- Automatically assigns tickets to specified group and agent
- Shows results in a popup message box
- Handles API errors gracefully

INPUT PARAMETERS:
Company Creation/Update:
- company_name: Name of the company to create or update
- state: State field for the company (custom field)

Contact Creation/Update:
- full_name: Full name of the contact
- email: Email address of the contact
- company_id: ID of associated company (optional)

Ticket Creation:
- subject: Ticket title/subject line
- description: Detailed description of the issue
- status: Ticket status (2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed)
- priority: Priority level (1 = Low, 2 = Medium, 3 = High, 4 = Urgent)
- requester_id: ID of the contact creating the ticket

OUTPUT:
- Creates companies, contacts, and tickets as needed
- Displays results in GUI message box
- Shows success/failure status for each operation

ERROR HANDLING:
- Validates contact_id is an integer
- Handles API errors with descriptive messages
- Shows popup dialogs for results and errors

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has all necessary permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that custom fields exist in your Freshdesk instance
"""

import tkinter as tk
from tkinter import messagebox
import requests
import json
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# Authentication tuple for API requests
auth = (API_KEY, 'X')  # Use the correct authentication format

# HTTP Headers for API requests
headers = {'Content-Type': 'application/json'}  # Header specifying content type

def create_or_update_company(company_name, state):
    """
    Create or update a company in Freshdesk.

    This function first checks if a company with the given name already exists
    using the autocomplete API. If found, it updates the existing company.
    If not found, it creates a new company.

    Args:
        company_name (str): Name of the company to create or update
        state (str): State value to set in the company's custom fields

    Returns:
        int: The company ID from the API response

    Raises:
        Exception: If the API request fails or no company ID is returned

    Note:
        - Uses the autocomplete API to search for existing companies
        - Sets the 'state' custom field during creation/update
        - Assumes 'state' is a valid custom field in your Freshdesk instance
    """
    # Search for existing company by name using autocomplete API
    url = f'https://{DOMAIN}/api/v2/companies/autocomplete?name={company_name}'
    response = requests.get(url, auth=auth)

    # Parse response and get list of matching companies
    companies = response.json().get('companies', [])

    # Prepare company data with custom fields
    company_data = {
        "name": company_name,
        "custom_fields": {
            "state": state  # Set state in custom fields
        }
    }
    company_data_json = json.dumps(company_data)

    # Check if company already exists
    if companies:
        # Update existing company
        company_id = companies[0]['id']
        update_url = f'https://{DOMAIN}/api/v2/companies/{company_id}'
        response = requests.put(update_url, auth=auth, headers=headers, data=company_data_json)

        if response.status_code != 200:
            raise Exception(f"Failed to update company: {response.text}")
        print(f"✓ Updated existing company: {company_name} (ID: {company_id})")
    else:
        # Create new company
        create_url = f'https://{DOMAIN}/api/v2/companies'
        response = requests.post(create_url, auth=auth, headers=headers, data=company_data_json)

        if response.status_code != 201:
            raise Exception(f"Failed to create company: {response.text}")
        print(f"✓ Created new company: {company_name}")

    # Extract and return company ID from response
    response_data = response.json()
    if 'id' in response_data:
        return response_data['id']
    else:
        raise Exception("No company ID found in API response.")


def create_or_update_contact(full_name, email, company_id=None):
    """
    Create or update a contact in Freshdesk.

    This function first checks if a contact with the given email already exists.
    If found, it updates the existing contact. If not found, it creates a new contact.

    Args:
        full_name (str): Full name of the contact
        email (str): Email address of the contact
        company_id (int, optional): ID of the company to associate with the contact

    Returns:
        tuple: (contact_id, status) where status is "Created" or "Updated"
               Returns (None, None) if operation fails

    Note:
        - Uses email lookup to find existing contacts
        - Associates contact with company if company_id is provided
        - Handles both creation and update scenarios
    """
    # Search for existing contact by email
    url = f'https://{DOMAIN}/api/v2/contacts?email={email}'
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        # Parse response to get contact data
        contacts_response = response.json()

        if contacts_response:
            # Contact exists, update it
            contact = contacts_response[0]
            contact_id = contact.get('id')

            if contact_id:
                # Prepare update data
                update_url = f'https://{DOMAIN}/api/v2/contacts/{contact_id}'
                contact_data = {
                    "name": full_name,
                    "email": email
                }

                # Add company association if provided
                if company_id:
                    contact_data["company_id"] = company_id

                # Update the contact
                response = requests.put(update_url, auth=auth, headers=headers, data=json.dumps(contact_data))

                if response.status_code == 200:
                    print(f"✓ Updated existing contact: {full_name} ({email})")
                    return contact_id, "Updated"
                else:
                    print(f"✗ Failed to update contact: {response.text}")
                    return None, None
            else:
                print("✗ No ID found in the contact data.")
                return None, None
        else:
            print("✗ No contacts found for the given email.")
            return None, None

    elif response.status_code == 404:
        # Contact doesn't exist, create new one
        create_url = f'https://{DOMAIN}/api/v2/contacts'
        contact_data = {
            "name": full_name,
            "email": email
        }

        # Add company association if provided
        if company_id:
            contact_data["company_id"] = company_id

        # Create the contact
        response = requests.post(create_url, auth=auth, headers=headers, data=json.dumps(contact_data))

        if response.status_code == 201:
            new_contact_id = response.json()['id']
            print(f"✓ Created new contact: {full_name} ({email})")
            return new_contact_id, "Created"
        else:
            print(f"✗ Failed to create contact: {response.text}")
            return None, None

    else:
        # Unexpected error
        print(f"✗ Error checking contact existence: {response.status_code} - {response.text}")
        return None, None

def create_ticket(contact_id, subject, description, status=2, priority=1):
    """
    Create a ticket in Freshdesk for a specific contact.

    This function creates a new support ticket in Freshdesk with the specified
    subject, description, and assigns it to a contact as the requester.

    Args:
        contact_id (int): ID of the contact who is creating the ticket
        subject (str): Subject/title of the ticket
        description (str): Detailed description of the issue
        status (int, optional): Ticket status (default: 2 = Open)
        priority (int, optional): Ticket priority (default: 1 = Low)

    Returns:
        dict: Ticket data returned from the API

    Raises:
        TypeError: If contact_id is not an integer
        Exception: If ticket creation fails

    Note:
        - Automatically assigns to group ID 67000578451 ('Old Subs' group)
        - Assigns to specific agent (responder_id: 67051499418)
        - Uses the contact as the requester
    """
    # Validate contact_id is an integer
    if not isinstance(contact_id, int):
        raise TypeError(f"Expected integer for contact_id, got {type(contact_id).__name__} instead.")

    # Prepare ticket data payload
    ticket_data = {
        "subject": subject,
        "description": description,
        "status": status,
        "priority": priority,
        "requester_id": contact_id,
        "group_id": 67000578451,  # Assign to 'Old Subs' group
        "responder_id": 67051499418  # Assign to specific agent
    }

    # Convert to JSON for API request
    ticket_data_json = json.dumps(ticket_data)
    print(f"Sending ticket data: {ticket_data}")  # Debug output

    # Create the ticket via API
    url = f'https://{DOMAIN}/api/v2/tickets'
    response = requests.post(url, auth=auth, headers=headers, data=ticket_data_json)

    if response.status_code != 201:
        raise Exception(f"Failed to create ticket: {response.text}")

    # Return the created ticket data
    return response.json()

def run_test_cases(selected_cases):
    """
    Execute the selected test cases by creating tickets for each case.

    This function creates or updates a default test contact, then creates
    tickets for each selected test case using that contact as the requester.

    Args:
        selected_cases (list): List of test case dictionaries with 'subject' key

    Note:
        - Uses a default test contact: "Test User" with email "test.user@example.com"
        - Creates tickets with automated descriptions
        - Shows results in a GUI message box
    """
    results = []

    print(f"Starting test case execution for {len(selected_cases)} cases...")

    # Create or update the default test contact
    contact_result = create_or_update_contact("Test User", "test.user@example.com")

    if contact_result and contact_result[0]:
        contact_id, status = contact_result
        print(f"✓ Using contact: Test User (ID: {contact_id}) - {status}")

        # Create tickets for each selected case
        for case in selected_cases:
            try:
                # Create ticket with automated description
                ticket = create_ticket(
                    contact_id,
                    case['subject'],
                    f"This is an automated test ticket for {case['subject']}."
                )
                result_msg = f"✓ Ticket created: {case['subject']} (ID: {ticket['id']})"
                print(f"  {result_msg}")
                results.append(result_msg)

            except Exception as e:
                error_msg = f"✗ Error for {case['subject']}: {str(e)}"
                print(f"  {error_msg}")
                results.append(error_msg)

    else:
        error_msg = "Failed to create or update contact. No tickets created."
        print(f"✗ {error_msg}")
        results.append(error_msg)

    # Show results in GUI message box
    messagebox.showinfo("Test Results", "\n".join(results))
    print("Test execution completed.")

"""
GUI Application Setup

This section creates a graphical user interface that allows users to:
- Select which test cases to run using checkboxes
- See all available test case options
- Execute selected test cases with one button click
- View results in a popup message box

The GUI uses tkinter, Python's standard GUI library, to create a simple
and intuitive interface for running the test cases.
"""

# Create the main GUI window
root = tk.Tk()
root.title("Freshdesk Test Ticket Creator")
root.geometry("400x500")  # Set window size

# Define available test cases
# Each test case has a subject (ticket title) and a checkbox variable
test_cases = [
    {"subject": "Assembly 1", "var": tk.BooleanVar()},
    {"subject": "Assembly 2", "var": tk.BooleanVar()},
    {"subject": "Assembly Rollover 1", "var": tk.BooleanVar()},
    {"subject": "Assembly Rollover 2", "var": tk.BooleanVar()},
    {"subject": "SEDCUST 1", "var": tk.BooleanVar()},
    {"subject": "SEDCUST 2", "var": tk.BooleanVar()},
    {"subject": "SIM - ASSIGNMENT 1", "var": tk.BooleanVar()},
    {"subject": "SIM - ASSIGNMENT 2", "var": tk.BooleanVar()},
]

# Create GUI layout instructions
instructions = tk.Label(
    root,
    text="Select test cases to create tickets for:",
    font=("Arial", 10, "bold")
)
instructions.grid(row=0, column=0, pady=10, sticky='w')

# Create checkboxes for each test case
for idx, case in enumerate(test_cases):
    checkbox = tk.Checkbutton(
        root,
        text=case["subject"],
        variable=case["var"],
        anchor='w'
    )
    checkbox.grid(row=idx + 1, column=0, sticky='w', padx=20)

# Select All / Deselect All functionality
select_all_var = tk.BooleanVar()

def toggle_all():
    """Toggle all checkboxes on or off based on Select All state."""
    for case in test_cases:
        case["var"].set(select_all_var.get())

# Select All checkbox
select_all_checkbox = tk.Checkbutton(
    root,
    text="Select All / Deselect All",
    variable=select_all_var,
    command=toggle_all,
    font=("Arial", 9, "italic")
)
select_all_checkbox.grid(row=len(test_cases) + 1, column=0, sticky='w', padx=20, pady=5)

# Button to execute selected test cases
run_button = tk.Button(
    root,
    text="Create Selected Tickets",
    command=lambda: run_test_cases([case for case in test_cases if case["var"].get()]),
    bg="#4CAF50",  # Green background
    fg="white",    # White text
    font=("Arial", 10, "bold"),
    padx=20,
    pady=10
)
run_button.grid(row=len(test_cases) + 2, column=0, pady=15)

# Status information label
status_label = tk.Label(
    root,
    text="Note: All tickets will be assigned to the 'Old Subs' group\nand associated with the test contact.",
    font=("Arial", 8),
    fg="gray"
)
status_label.grid(row=len(test_cases) + 3, column=0, pady=5)

# Footer with version info
footer_label = tk.Label(
    root,
    text="Freshdesk Test Ticket Creator v1.0",
    font=("Arial", 7),
    fg="gray"
)
footer_label.grid(row=len(test_cases) + 4, column=0, pady=10)

# Start the GUI event loop
# This keeps the window open and responsive to user interactions
root.mainloop()
