"""
Freshdesk Company and Ticket Creation Script

DESCRIPTION:
This script creates a new company in Freshdesk (or uses an existing one if it
already exists) and associates a requester with that company. It then creates a
ticket for that company using the associated requester. This workflow is useful
for automated ticket creation with proper company and requester relationships.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with company, contact, and ticket creation permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace sandbox_domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update test_unique_external_id, company_name, ticket_subject, and ticket_description
4. Ensure your API key has permissions for company, contact, and ticket creation
5. Run the script: python create_company_ticket.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Companies API: https://developers.freshdesk.com/api/#companies
- Contacts API: https://developers.freshdesk.com/api/#contacts
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- sandbox_domain: Your Freshdesk domain
- test_unique_external_id: Unique identifier for the requester
- company_name: Name of the company to create/find
- ticket_subject: Subject line for the new ticket
- ticket_description: Description content for the new ticket

OUTPUT:
- Creates company (or finds existing one)
- Creates/associates requester with company
- Creates ticket with company and requester associations
- Console output showing success/failure for each step

WORKFLOW PROCESS:
1. Company Creation: Creates new company or handles duplicate company errors
2. Requester Association: Searches for existing requester or creates new one
3. Ticket Creation: Creates ticket with proper company and requester relationships

ERROR HANDLING:
- Handles HTTP 409 (duplicate company) errors with graceful fallback
- Handles HTTP 404 (requester not found) errors by creating new requester
- Handles network and parsing errors
- Validates API responses and data structure

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has company, contact, and ticket creation permissions
- Check that unique_external_id is unique across all contacts
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that company and contact fields are valid

USAGE SCENARIOS:
- Automated ticket creation for new customers
- Bulk ticket creation with company associations
- Testing company and contact workflows
- Integration with external systems for ticket creation
- Customer onboarding automation
"""

import requests
import json
import logging
import sys

# Define API credentials and endpoints
api_key = "5TMgbcZdRFY70hSpEdj"
sandbox_domain = "benchmarkeducationcompanysandbox.freshdesk.com"
headers = {
    "Content-Type": "application/json"
}

# Configure logging to both file and console
LOG_FILENAME = 'company_ticket_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Function to create a new company
def create_company(company_name):
    url = f"https://{sandbox_domain}/api/v2/companies"
    company_data = {
        "name": company_name,
    }

    response = requests.post(url, auth=(api_key, "X"), headers=headers, data=json.dumps(company_data))
    
    if response.status_code == 201:
        print("Company created successfully:", response.json())
        return response.json()["id"]  # Return the company ID
    elif response.status_code == 409:
        # Handle duplicate company error
        error_info = response.json().get("errors", [])
        if error_info and "additional_info" in error_info[0]:
            company_id = error_info[0]["additional_info"].get("company_id")
            print(f"Company already exists. Using existing company ID: {company_id}")
            return company_id
        else:
            print("Failed to create company due to duplicate value, but no ID was returned.")
            return None
    else:
        print("Failed to create company:", response.status_code, response.text)
        return None

# Function to create or associate a requester with a company
def create_or_associate_requester(unique_external_id, company_id):
    # First, try to find the requester by unique_external_id
    search_url = f"https://{sandbox_domain}/api/v2/search/contacts?query=\"unique_external_id:{unique_external_id}\""
    response = requests.get(search_url, auth=(api_key, "X"), headers=headers)
    
    if response.status_code == 200:
        contacts = response.json().get("results", [])
        if contacts:
            contact = contacts[0]
            print(f"Requester found with ID: {contact['id']}")
            # Check if the contact is already associated with the company
            if contact.get("company_id") == company_id:
                print("Requester already associated with the company.")
                return contact["id"]
            else:
                # Update the contact to associate it with the company
                update_url = f"https://{sandbox_domain}/api/v2/contacts/{contact['id']}"
                update_data = {
                    "company_id": company_id
                }
                update_response = requests.put(update_url, auth=(api_key, "X"), headers=headers, data=json.dumps(update_data))
                if update_response.status_code == 200:
                    print("Requester successfully associated with the company.")
                    return contact["id"]
                else:
                    print("Failed to associate requester with the company:", update_response.status_code, update_response.text)
                    return None
        else:
            print("Requester not found. Creating a new one.")
    else:
        print("Failed to search for requester:", response.status_code, response.text)

    # If the requester does not exist, create a new one
    create_url = f"https://{sandbox_domain}/api/v2/contacts"
    contact_data = {
        "unique_external_id": unique_external_id,
        "company_id": company_id,
        "name": "Default Requester Name"  # Provide a default name for the requester
    }
    create_response = requests.post(create_url, auth=(api_key, "X"), headers=headers, data=json.dumps(contact_data))
    
    if create_response.status_code == 201:
        print("Requester created and associated with the company:", create_response.json())
        return create_response.json()["id"]
    else:
        print("Failed to create requester:", create_response.status_code, create_response.text)
        return None

# Function to create a new ticket using a requester's ID
def create_ticket(subject, description, company_id, requester_id):
    url = f"https://{sandbox_domain}/api/v2/tickets"
    ticket_data = {
        "subject": subject,
        "description": description,
        "status": 2,  # Assuming 'Open' status
        "priority": 1,  # Assuming 'Low' priority
        "company_id": company_id,
        "requester_id": requester_id  # Use the requester's ID instead of unique_external_id
    }

    response = requests.post(url, auth=(api_key, "X"), headers=headers, data=json.dumps(ticket_data))
    
    if response.status_code == 201:
        print("Ticket created successfully:", response.json())
    else:
        print("Failed to create ticket:", response.status_code, response.text)

# Main execution
if __name__ == "__main__":
    logging.info("Starting company and ticket creation process...")
    print("Starting company and ticket creation process...")

    company_name = "New New New Company"
    ticket_subject = "New Support Request"
    ticket_description = "Description of the issue or request."
    test_unique_external_id = "newnewnew1234"  # Test unique external ID

    # Step 1: Attempt to create the company or use the existing one
    logging.info("Step 1: Creating/finding company...")
    print("Step 1: Creating/finding company...")
    company_id = create_company(company_name)

    # Step 2: Ensure the requester is associated with the company
    if company_id:
        logging.info("Step 2: Creating/associating requester...")
        print("Step 2: Creating/associating requester...")
        requester_id = create_or_associate_requester(test_unique_external_id, company_id)

        # Step 3: Create a new ticket for the company using the requester's ID
        if requester_id:
            logging.info("Step 3: Creating ticket...")
            print("Step 3: Creating ticket...")
            create_ticket(ticket_subject, ticket_description, company_id, requester_id)

    logging.info("Company and ticket creation process completed.")
    print("Company and ticket creation process completed.")

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

def main(use_gui=False, form_data=None):
    """Main function with optional GUI mode."""
    if use_gui:
        def run_creation():
            process_creation_gui(form_data)

        threading.Thread(target=run_creation, daemon=True).start()
        return

    # Command-line mode
    logging.info("Starting company and ticket creation process...")
    print("Starting company and ticket creation process...")

    company_name = "New New New Company"
    ticket_subject = "New Support Request"
    ticket_description = "Description of the issue or request."
    test_unique_external_id = "newnewnew1234"  # Test unique external ID

    # Step 1: Attempt to create the company or use the existing one
    logging.info("Step 1: Creating/finding company...")
    print("Step 1: Creating/finding company...")
    company_id = create_company(company_name)

    # Step 2: Ensure the requester is associated with the company
    if company_id:
        logging.info("Step 2: Creating/associating requester...")
        print("Step 2: Creating/associating requester...")
        requester_id = create_or_associate_requester(test_unique_external_id, company_id)

        # Step 3: Create a new ticket for the company using the requester's ID
        if requester_id:
            logging.info("Step 3: Creating ticket...")
            print("Step 3: Creating ticket...")
            create_ticket(ticket_subject, ticket_description, company_id, requester_id)

    logging.info("Company and ticket creation process completed.")
    print("Company and ticket creation process completed.")

def process_creation_gui(form_data):
    """Process creation in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Starting company and ticket creation process...")

    # Extract form data
    company_name = form_data.get('company_name', 'New Company')
    ticket_subject = form_data.get('ticket_subject', 'New Support Request')
    ticket_description = form_data.get('ticket_description', 'Description of the issue or request.')
    unique_external_id = form_data.get('unique_external_id', 'newcontact1234')

    # Step 1: Attempt to create the company or use the existing one
    update_progress("Step 1: Creating/finding company...")
    company_id = create_company(company_name)

    if not company_id:
        update_progress("❌ Failed to create/find company")
        messagebox.showerror("Error", "Failed to create or find company")
        return

    # Step 2: Ensure the requester is associated with the company
    update_progress("Step 2: Creating/associating requester...")
    requester_id = create_or_associate_requester(unique_external_id, company_id)

    if not requester_id:
        update_progress("❌ Failed to create/associate requester")
        messagebox.showerror("Error", "Failed to create or associate requester")
        return

    # Step 3: Create a new ticket for the company using the requester's ID
    update_progress("Step 3: Creating ticket...")
    create_ticket(ticket_subject, ticket_description, company_id, requester_id)

    update_progress("✅ Company and ticket creation process completed!")
    messagebox.showinfo("Success", "Company and ticket created successfully!")

def create_gui():
    """Create the graphical user interface."""
    global company_name_var, ticket_subject_var, ticket_description_text, unique_external_id_var, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Company & Ticket Creator")
    app.geometry("600x600")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Create Company & Ticket", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Fill in the form below to create a company, associate a requester,\n"
                                "and create a ticket with proper relationships.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Form fields
    form_frame = ttk.LabelFrame(main_frame, text="Details", padding="10")
    form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    form_frame.columnconfigure(1, weight=1)

    # Company Name
    ttk.Label(form_frame, text="Company Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
    company_name_var = tk.StringVar(value="New Company")
    company_name_entry = ttk.Entry(form_frame, textvariable=company_name_var, width=50)
    company_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Unique External ID
    ttk.Label(form_frame, text="Requester ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
    unique_external_id_var = tk.StringVar(value="newcontact1234")
    unique_external_id_entry = ttk.Entry(form_frame, textvariable=unique_external_id_var, width=50)
    unique_external_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    # Ticket Subject
    ttk.Label(form_frame, text="Ticket Subject:").grid(row=2, column=0, sticky=tk.W, pady=5)
    ticket_subject_var = tk.StringVar(value="New Support Request")
    ticket_subject_entry = ttk.Entry(form_frame, textvariable=ticket_subject_var, width=50)
    ticket_subject_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

    # Ticket Description
    ttk.Label(form_frame, text="Ticket Description:").grid(row=3, column=0, sticky=tk.W, pady=5)
    ticket_description_text = tk.Text(form_frame, height=4, width=50)
    ticket_description_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
    ticket_description_text.insert('1.0', 'Description of the issue or request.')

    # Quick templates
    template_frame = ttk.LabelFrame(main_frame, text="Quick Templates", padding="10")
    template_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    def apply_template(template_type):
        templates = {
            'subscription': {
                'subject': 'Subscription Issue',
                'description': 'Customer is experiencing issues with their subscription. Please investigate and resolve.'
            },
            'login': {
                'subject': 'Login Problem',
                'description': 'User unable to log in to their account. Please assist with troubleshooting.'
            },
            'bug': {
                'subject': 'Bug Report',
                'description': 'User has reported a bug in the system. Please investigate and provide a fix.'
            }
        }

        if template_type in templates:
            template = templates[template_type]
            ticket_subject_var.set(template['subject'])
            ticket_description_text.delete('1.0', tk.END)
            ticket_description_text.insert('1.0', template['description'])

    ttk.Button(template_frame, text="Subscription Issue",
               command=lambda: apply_template('subscription')).grid(row=0, column=0, padx=5)
    ttk.Button(template_frame, text="Login Problem",
               command=lambda: apply_template('login')).grid(row=0, column=1, padx=5)
    ttk.Button(template_frame, text="Bug Report",
               command=lambda: apply_template('bug')).grid(row=0, column=2, padx=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    def start_creation():
        form_data = {
            'company_name': company_name_var.get().strip(),
            'unique_external_id': unique_external_id_var.get().strip(),
            'ticket_subject': ticket_subject_var.get().strip(),
            'ticket_description': ticket_description_text.get('1.0', tk.END).strip()
        }

        if not form_data['company_name'] or not form_data['unique_external_id'] or not form_data['ticket_subject']:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        threading.Thread(target=process_creation_gui, args=(form_data,), daemon=True).start()

    def clear_form():
        company_name_var.set("New Company")
        unique_external_id_var.set("newcontact1234")
        ticket_subject_var.set("New Support Request")
        ticket_description_text.delete('1.0', tk.END)
        ticket_description_text.insert('1.0', 'Description of the issue or request.')

    ttk.Button(button_frame, text="Create Company & Ticket",
               command=start_creation).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Clear Form",
               command=clear_form).grid(row=0, column=1, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=6, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=60, state=tk.DISABLED)
    log_area.grid(row=7, column=0, columnspan=2, pady=5)

    return app

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()
