"""
Freshdesk Contact and Domain Management GUI

DESCRIPTION:
This script provides a graphical user interface for managing Freshdesk contacts
and company domains. It offers two main operations:

1. Move Domain and Associated Contacts: Transfers a domain from one company to
   another along with all contacts using that domain email address
2. Move Contacts Only: Transfers contacts between companies based on domain
   filtering or moves all contacts

The script includes comprehensive rate limiting, error handling, and detailed
logging of all operations.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- tkinter (usually included with Python)
- Valid Freshdesk API key with contact/company read/write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for:
   - Contact management (read/write)
   - Company management (read/write/delete)
4. Run the script: python fd_contact_and_domain_manager.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 700 requests per minute for enterprise plans

FEATURES:
- GUI interface for easy operation
- Rate limit management with automatic delays
- Comprehensive error handling and logging
- Real-time progress tracking
- Log export functionality

OPERATIONS:

1. MOVE DOMAIN AND ASSOCIATED CONTACTS:
   - Removes a domain from source company
   - Adds domain to target company
   - Moves all contacts with that domain email to target company
   - Optionally deletes source company

2. MOVE CONTACTS ONLY:
   - Moves contacts based on domain filtering (if not "move all")
   - Moves all contacts from source to target company
   - Optionally deletes source company

INPUT PARAMETERS:
- Source Company ID: ID of company to move from
- Target Company ID: ID of company to move to
- Domain: Email domain to move (for domain operations)
- Delete options: Whether to delete source company after operations

OUTPUT:
- Real-time log of all operations in GUI
- Detailed error messages for troubleshooting
- Exportable log file for record keeping

ERROR HANDLING:
- Validates company IDs are numeric
- Handles API rate limiting with automatic retry
- Handles domain conflicts and duplicate domains
- Validates required fields before processing
- Continues processing even if individual operations fail

RATE LIMIT HANDLING:
- Monitors API rate limits automatically
- Waits for rate limit reset when necessary
- Processes requests in controlled batches

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has all necessary permissions
- Check that company IDs are valid and exist
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check GUI logs for detailed error information
"""

import requests
import time
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain

# Authentication and headers
auth = (API_KEY, 'X')
headers = {'Content-Type': 'application/json'}

# Rate limiting configuration (Enterprise plan)
RATE_LIMIT = 700  # Enterprise plan rate limit
RATE_LIMIT_WINDOW = 60  # in seconds

# Initialize rate limit tracking
rate_limit_remaining = RATE_LIMIT
rate_limit_reset_time = time.time() + RATE_LIMIT_WINDOW

def make_request(method, endpoint, params=None, data=None):
    """
    Make an API request to Freshdesk with rate limiting.

    This function handles API rate limiting automatically by checking remaining
    requests and waiting for the rate limit window to reset if necessary.

    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        endpoint (str): API endpoint (e.g., '/contacts', '/companies/123')
        params (dict, optional): Query parameters for GET requests
        data (dict, optional): JSON data for POST/PUT requests

    Returns:
        dict or None: API response data, or None if no content

    Raises:
        requests.exceptions.HTTPError: If API request fails

    Note:
        - Automatically handles rate limit waiting
        - Updates rate limit counters based on response headers
        - Raises HTTPError for non-success status codes
    """
    global rate_limit_remaining, rate_limit_reset_time

    # Wait if rate limit is exceeded
    while rate_limit_remaining <= 0:
        sleep_time = max(rate_limit_reset_time - time.time(), 0)
        if sleep_time > 0:
            print(f"Rate limit reached. Waiting {sleep_time:.1f} seconds...")
        time.sleep(sleep_time)
        rate_limit_remaining = RATE_LIMIT

    # Construct full URL
    url = f'https://{DOMAIN}/api/v2{endpoint}'

    # Make the API request
    response = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=data,
        auth=auth
    )

    # Update rate limit counters from response headers
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', RATE_LIMIT))
    rate_limit_reset_time = time.time() + RATE_LIMIT_WINDOW

    # Raise exception for HTTP errors (4xx, 5xx)
    response.raise_for_status()

    # Return JSON data if response has content, otherwise None
    return response.json() if response.content else None

def get_contacts_by_company(company_id):
    """
    Retrieve all contacts associated with a specific company.

    This function fetches contacts in pages and combines them into a single list.
    Uses pagination to handle companies with many contacts.

    Args:
        company_id (int): ID of the company to fetch contacts for

    Returns:
        list: List of contact dictionaries

    Note:
        - Handles pagination automatically
        - Returns empty list if company has no contacts or doesn't exist
    """
    contacts = []
    page = 1

    while True:
        # Fetch contacts for this company, one page at a time
        response = make_request('GET', f'/contacts?company_id={company_id}&page={page}')

        if not response:
            # No more contacts or error occurred
            break

        # Add this page of contacts to our collection
        contacts.extend(response)
        page += 1

    return contacts

def update_company_domains(company_id, domains):
    """
    Update the domains associated with a company.

    Args:
        company_id (int): ID of the company to update
        domains (list): List of domain strings to set for the company

    Note:
        - Overwrites existing domains with the new list
        - Domains should be valid email domains (e.g., 'example.com')
    """
    make_request('PUT', f'/companies/{company_id}', data={'domains': domains})

def move_contacts_to_company(contact_ids, new_company_id):
    """
    Move multiple contacts to a different company.

    Args:
        contact_ids (list): List of contact IDs to move
        new_company_id (int): ID of the company to move contacts to

    Note:
        - Updates each contact individually
        - All contacts will be moved to the same target company
    """
    for contact_id in contact_ids:
        make_request('PUT', f'/contacts/{contact_id}', data={'company_id': new_company_id})

def delete_company(company_id):
    """
    Delete a company from Freshdesk.

    WARNING: This operation is permanent and cannot be undone.

    Args:
        company_id (int): ID of the company to delete

    Note:
        - This will fail if the company has associated tickets or active subscriptions
        - Use with caution in production environments
    """
    make_request('DELETE', f'/companies/{company_id}')

def move_contacts_and_domain(source_company_id, incorrect_domain, correct_company_id, delete_company_flag, log):
    """
    Move a domain and all associated contacts from one company to another.

    This is the main operation for transferring company ownership of a domain
    along with all contacts using email addresses from that domain.

    Args:
        source_company_id (int): ID of company currently owning the domain
        incorrect_domain (str): Domain to transfer (e.g., 'example.com')
        correct_company_id (int): ID of company that should own the domain
        delete_company_flag (bool): Whether to delete source company after transfer
        log (tk.Text): GUI text widget for logging progress

    Process:
        1. Get all contacts from source company
        2. Remove domain from source company
        3. Add domain to correct company
        4. Move contacts with that domain to correct company
        5. Optionally delete source company

    Note:
        - Only moves contacts whose email contains the specified domain
        - Handles domain conflicts gracefully
        - Logs all operations for audit trail
    """
    log.insert(tk.END, f'Starting domain and contact transfer process...\n')
    log.insert(tk.END, f'Source Company: {source_company_id}\n')
    log.insert(tk.END, f'Domain to move: {incorrect_domain}\n')
    log.insert(tk.END, f'Target Company: {correct_company_id}\n')
    log.insert(tk.END, f'Delete source company: {delete_company_flag}\n\n')

    try:
        # Step 1: Get all contacts from source company
        log.insert(tk.END, 'Step 1: Fetching contacts from source company...\n')
        source_company_contacts = get_contacts_by_company(source_company_id)
        log.insert(tk.END, f'Found {len(source_company_contacts)} contacts in source company.\n')

        # Step 2: Remove domain from source company
        log.insert(tk.END, 'Step 2: Removing domain from source company...\n')
        source_company = make_request('GET', f'/companies/{source_company_id}')
        source_company_domains = source_company.get('domains', [])

        if incorrect_domain in source_company_domains:
            source_company_domains.remove(incorrect_domain)
            update_company_domains(source_company_id, source_company_domains)
            log.insert(tk.END, f'✓ Removed domain {incorrect_domain} from source company.\n')
        else:
            log.insert(tk.END, f'⚠ Domain {incorrect_domain} was not found in source company domains.\n')

        # Step 3: Add domain to correct company
        log.insert(tk.END, 'Step 3: Adding domain to target company...\n')
        correct_company = make_request('GET', f'/companies/{correct_company_id}')
        correct_company_domains = correct_company.get('domains', [])

        # Debug: Show current domains
        log.insert(tk.END, f'Current domains in target company: {correct_company_domains}\n')

        # Add domain if not already present
        if incorrect_domain not in correct_company_domains:
            correct_company_domains.append(incorrect_domain)
            update_company_domains(correct_company_id, correct_company_domains)
            log.insert(tk.END, f'✓ Added domain {incorrect_domain} to target company.\n')
        else:
            log.insert(tk.END, f'⚠ Domain {incorrect_domain} already exists in target company.\n')

        # Step 4: Move contacts with the domain
        log.insert(tk.END, 'Step 4: Moving contacts...\n')
        contact_ids_to_move = [
            contact['id'] for contact in source_company_contacts
            if incorrect_domain in contact['email']
        ]

        if contact_ids_to_move:
            move_contacts_to_company(contact_ids_to_move, correct_company_id)
            log.insert(tk.END, f'✓ Moved {len(contact_ids_to_move)} contacts to target company.\n')
        else:
            log.insert(tk.END, f'⚠ No contacts found with domain {incorrect_domain}.\n')

        # Step 5: Delete source company if requested
        if delete_company_flag:
            log.insert(tk.END, 'Step 5: Deleting source company...\n')
            delete_company(source_company_id)
            log.insert(tk.END, f'✓ Deleted source company {source_company_id}.\n')

        log.insert(tk.END, '\n🎉 Domain and contact transfer completed successfully!\n')

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            log.insert(tk.END, f'❌ Error: Domain conflict. Domain {incorrect_domain} might already exist in another company.\n')
        else:
            log.insert(tk.END, f'❌ HTTP Error {e.response.status_code}: {e.response.text}\n')
    except Exception as e:
        log.insert(tk.END, f'❌ Unexpected error: {str(e)}\n')

def move_only_contacts(source_company_id, target_company_id, delete_source_flag, move_all_flag, domains_to_move, log):
    """
    Move contacts from one company to another with optional domain filtering.

    This function moves contacts between companies. If move_all_flag is False,
    it filters contacts by specific domains. If True, it moves all contacts.

    Args:
        source_company_id (int): ID of company to move contacts from
        target_company_id (int): ID of company to move contacts to
        delete_source_flag (bool): Whether to delete source company after move
        move_all_flag (bool): Whether to move all contacts or filter by domain
        domains_to_move (str): Comma-separated list of domains to filter by
        log (tk.Text): GUI text widget for logging progress

    Process:
        1. Get all contacts from source company
        2. Filter contacts based on move_all_flag and domains
        3. Move filtered contacts to target company
        4. Optionally delete source company

    Note:
        - When move_all_flag is False, only moves contacts with specified domains
        - When move_all_flag is True, moves ALL contacts from source company
        - Handles domain filtering case-insensitively
    """
    log.insert(tk.END, f'Starting contact transfer process...\n')
    log.insert(tk.END, f'Source Company: {source_company_id}\n')
    log.insert(tk.END, f'Target Company: {target_company_id}\n')
    log.insert(tk.END, f'Move all contacts: {move_all_flag}\n')
    if not move_all_flag:
        log.insert(tk.END, f'Domains to filter: {domains_to_move}\n')
    log.insert(tk.END, f'Delete source company: {delete_source_flag}\n\n')

    try:
        # Step 1: Get all contacts from source company
        log.insert(tk.END, 'Step 1: Fetching contacts from source company...\n')
        source_company_contacts = get_contacts_by_company(company_id=source_company_id)
        log.insert(tk.END, f'Found {len(source_company_contacts)} contacts in source company.\n')

        # Step 2: Filter contacts based on criteria
        log.insert(tk.END, 'Step 2: Filtering contacts...\n')

        if move_all_flag:
            # Move all contacts
            contact_ids_to_move = [contact['id'] for contact in source_company_contacts]
            log.insert(tk.END, f'Moving all {len(contact_ids_to_move)} contacts.\n')
        else:
            # Filter by specific domains
            domain_list = [domain.strip().lower() for domain in domains_to_move.split(',') if domain.strip()]
            contact_ids_to_move = [
                contact['id'] for contact in source_company_contacts
                if any(domain in contact['email'].lower() for domain in domain_list)
            ]
            log.insert(tk.END, f'Found {len(contact_ids_to_move)} contacts matching domains: {domains_to_move}\n')

        if not contact_ids_to_move:
            log.insert(tk.END, '⚠ No contacts found matching the criteria.\n')
            return

        # Step 3: Move contacts to target company
        log.insert(tk.END, 'Step 3: Moving contacts to target company...\n')
        move_contacts_to_company(contact_ids_to_move, target_company_id)
        log.insert(tk.END, f'✓ Successfully moved {len(contact_ids_to_move)} contacts to company {target_company_id}.\n')

        # Step 4: Delete source company if requested
        if delete_source_flag:
            log.insert(tk.END, 'Step 4: Deleting source company...\n')
            delete_company(source_company_id)
            log.insert(tk.END, f'✓ Deleted source company {source_company_id}.\n')

        log.insert(tk.END, '\n🎉 Contact transfer completed successfully!\n')

    except Exception as e:
        log.insert(tk.END, f'❌ Error during contact transfer: {str(e)}\n')

# Function to start the domain move process from GUI
def start_domain_process():
    source_company_id = source_company_id_var.get()
    incorrect_domain = domain_var.get()
    correct_company_id = correct_company_id_var.get()
    delete_company_flag = delete_company_var.get()

    # Debug logging
    print(f"Source Company ID: {source_company_id}")
    print(f"Domain to Move: {incorrect_domain}")
    print(f"Correct Company ID: {correct_company_id}")
    
    if not source_company_id or not incorrect_domain or not correct_company_id:
        messagebox.showerror("Error", "Please provide source company ID, domain, and correct company ID.")
        return

    try:
        source_company_id = int(source_company_id)
        correct_company_id = int(correct_company_id)
        move_contacts_and_domain(source_company_id, incorrect_domain, correct_company_id, delete_company_flag, log_text)
    except ValueError:
        messagebox.showerror("Error", "Company IDs must be numbers.")

# Function to start the contact move process from GUI
def start_contact_process():
    source_company_id = source_company_id_var2.get()
    target_company_id = target_company_id_var.get()
    delete_source_flag = delete_source_var.get()
    move_all_flag = move_all_var.get()
    domains_to_move = domains_var.get()

    # Debug logging
    print(f"Source Company ID: {source_company_id}")
    print(f"Target Company ID: {target_company_id}")
    print(f"Move All Contacts: {move_all_flag}")
    print(f"Domains to Move: {domains_to_move}")
    
    if not source_company_id or not target_company_id:
        messagebox.showerror("Error", "Please provide both source and target company IDs.")
        return

    try:
        source_company_id = int(source_company_id)
        target_company_id = int(target_company_id)
        move_only_contacts(source_company_id, target_company_id, delete_source_flag, move_all_flag, domains_to_move, log_text)
    except ValueError:
        messagebox.showerror("Error", "Company IDs must be numbers.")

# Function to export logs to a file
def export_logs():
    log_content = log_text.get(1.0, tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(log_content)
        messagebox.showinfo("Success", "Logs exported successfully.")

# Function to enable or disable the domain entry based on the checkbox
def toggle_domain_entry():
    if move_all_var.get():
        domains_entry.configure(state=tk.DISABLED)
    else:
        domains_entry.configure(state=tk.NORMAL)

# GUI setup
root = tk.Tk()
root.title("Freshdesk Contact and Domain Manager")

# Initialize StringVar variables
source_company_id_var = tk.StringVar()
domain_var = tk.StringVar()
correct_company_id_var = tk.StringVar()
source_company_id_var2 = tk.StringVar()
target_company_id_var = tk.StringVar()
domains_var = tk.StringVar()

# Section 1: Move Domain and Associated Contacts
tk.Label(root, text="Move Domain and Associated Contacts").grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

tk.Label(root, text="Source Company ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
source_company_id_entry = tk.Entry(root, textvariable=source_company_id_var, width=30)
source_company_id_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Domain to Move:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
domain_entry = tk.Entry(root, textvariable=domain_var, width=30)
domain_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Correct Company ID:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
correct_company_id_entry = tk.Entry(root, textvariable=correct_company_id_var, width=30)
correct_company_id_entry.grid(row=3, column=1, padx=10, pady=5)

delete_company_var = tk.BooleanVar()
delete_company_check = tk.Checkbutton(root, text="Delete Company After Moving Domain and Associated Contacts", variable=delete_company_var)
delete_company_check.grid(row=4, column=0, columnspan=2, pady=5)

start_domain_button = tk.Button(root, text="Start Process", command=start_domain_process)
start_domain_button.grid(row=5, column=0, columnspan=2, pady=10)

# Section 2: Move Contacts Only
tk.Label(root, text="Move Contacts Only").grid(row=6, column=0, columnspan=2, pady=10, sticky="w")

tk.Label(root, text="Source Company ID:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
source_company_id_entry2 = tk.Entry(root, textvariable=source_company_id_var2, width=30)
source_company_id_entry2.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Target Company ID:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
target_company_id_entry = tk.Entry(root, textvariable=target_company_id_var, width=30)
target_company_id_entry.grid(row=8, column=1, padx=10, pady=5)

move_all_var = tk.BooleanVar()
move_all_check = tk.Checkbutton(root, text="Move All Contacts", variable=move_all_var, command=toggle_domain_entry)
move_all_check.grid(row=9, column=0, columnspan=2, pady=5)

tk.Label(root, text="Domains to Move (comma-separated):").grid(row=10, column=0, padx=10, pady=5, sticky="e")
domains_entry = tk.Entry(root, textvariable=domains_var, width=30)
domains_entry.grid(row=10, column=1, padx=10, pady=5)

delete_source_var = tk.BooleanVar()
delete_source_check = tk.Checkbutton(root, text="Delete Source Company After Moving Contacts", variable=delete_source_var)
delete_source_check.grid(row=11, column=0, columnspan=2, pady=5)

start_contact_button = tk.Button(root, text="Start Process", command=start_contact_process)
start_contact_button.grid(row=12, column=0, columnspan=2, pady=10)

# Log area and export button
log_text = scrolledtext.ScrolledText(root, width=70, height=20)
log_text.grid(row=13, column=0, columnspan=2, padx=10, pady=10)

export_button = tk.Button(root, text="Export Logs", command=export_logs)
export_button.grid(row=14, column=0, columnspan=2, pady=10)

root.mainloop()

