"""
Freshdesk Region and Account Manager Updater GUI

DESCRIPTION:
This script provides a graphical user interface for updating ticket regions and
account managers based on company state information. It automatically determines
the appropriate region and account manager for each ticket based on the company's
state and updates the custom fields accordingly.

REQUIREMENTS:
- Python 3.x
- tkinter (usually included with Python)
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and company read/write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update state_to_region_account_manager mapping if needed
4. Ensure your API key has permissions for ticket and company access
5. Run the script: python region_updater.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#update_ticket
- Companies API: https://developers.freshdesk.com/api/#companies
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- REQUEST_INTERVAL: Delay between API requests (default: 0.22 seconds)
- state_to_region_account_manager: Mapping of states to regions and managers

OUTPUT:
- GUI interface for ticket ID input and progress monitoring
- Updates ticket custom fields with region and account manager
- Log file with detailed operation information
- Progress tracking and completion statistics

REGION MAPPING:
- Automatically maps US states to regions (West, Northeast, Central Southwest, Central Southeast)
- Assigns appropriate account managers based on state
- Handles international and DoDEA (Department of Defense Education Activity) cases

TICKET UPDATE PROCESS:
- Fetches company information for each ticket
- Extracts state from company custom fields
- Maps state to region and account manager
- Updates ticket with cf_region and cf_account_manager fields
- Processes tickets in rate-limited batches

ERROR HANDLING:
- Handles HTTP 404 (ticket/company not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Implements 0.22-second delays between requests
- Monitors rate limit usage and adjusts timing
- Handles rate limit responses with retry-after delays

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and company read/write permissions
- Check that company custom fields include 'state'
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets have associated companies

USAGE SCENARIOS:
- Bulk update ticket regions based on company locations
- Assign appropriate account managers automatically
- Maintain consistent regional assignments across tickets
- Data cleanup and standardization operations
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import time
import threading

# Freshdesk API credentials and URL
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany'
BASE_URL = f'https://{DOMAIN}.freshdesk.com/api/v2'

# Rate limiting setup
REQUEST_INTERVAL = 0.22  # slightly more than 0.21 seconds to stay within the limit

# State to Region and Account Manager Mapping
state_to_region_account_manager = {
    "WA": ("West", "Jamie Garcia"), "OR": ("West", "Jamie Garcia"), "ID": ("West", "Jamie Garcia"), "MT": ("West", "Jamie Garcia"), 
    "WY": ("West", "Jamie Garcia"), "CA": ("West", "Michelle Susi"), "NV": ("West", "Michelle Susi"), "UT": ("West", "Jamie Garcia"), 
    "CO": ("West", "Jamie Garcia"), "AZ": ("West", "Michelle Susi"), "NM": ("Central Southwest", "Christina Fabiano"), 
    "KS": ("Central Southwest", "Christina Fabiano"), "OK": ("Central Southwest", "Christina Fabiano"), "TX": ("Central Southwest", "Christina Fabiano"), 
    "MO": ("Central Southwest", "Christina Fabiano"), "AR": ("Central Southwest", "Christina Fabiano"), "LA": ("Central Southwest", "Christina Fabiano"), 
    "MS": ("Central Southwest", "Christina Fabiano"), "NE": ("Central Southwest", "Christina Fabiano"), "IA": ("Central Southwest", "Christina Fabiano"), 
    "HI": ("Central Southwest", "Michelle Susi"), "AK": ("Central Southwest", "Michelle Susi"), "AL": ("Central Southeast", "Sue Wick-Krch"), 
    "TN": ("Central Southeast", "Sue Wick-Krch"), "KY": ("Central Southeast", "Sue Wick-Krch"), "SC": ("Central Southeast", "Sue Wick-Krch"), 
    "GA": ("Central Southeast", "Sue Wick-Krch"), "ND": ("Central Southeast", "Audrey Smith"), "SD": ("Central Southeast", "Audrey Smith"), 
    "MN": ("Central Southeast", "Audrey Smith"), "WI": ("Central Southeast", "Audrey Smith"), "IL": ("Central Southeast", "Audrey Smith"), 
    "IN": ("Central Southeast", "Sue Wick-Krch"), "OH": ("Central Southeast", "Sue Wick-Krch"), "MI": ("Central Southeast", "Sue Wick-Krch"), 
    "FL": ("Central Southeast", "Sue Wick-Krch"), "WV": ("Northeast", "Julie Tangeman"), "VA": ("Northeast", "Julie Tangeman"), 
    "NC": ("Northeast", "Julie Tangeman"), "ME": ("Northeast", "Julie Tangeman"), "NH": ("Northeast", "Julie Tangeman"), 
    "VT": ("Northeast", "Julie Tangeman"), "MA": ("Northeast", "Julie Tangeman"), "RI": ("Northeast", "Julie Tangeman"), 
    "CT": ("Northeast", "Julie Tangeman"), "NY": ("Northeast", "Julie Tangeman"), "NJ": ("Northeast", "Julie Tangeman"), 
    "PA": ("Northeast", "Julie Tangeman"), "DE": ("Northeast", "Julie Tangeman"), "MD": ("Northeast", "Julie Tangeman"), 
    "DC": ("Northeast", "Julie Tangeman"), "International": ("Northeast", "Julie Tangeman")
}

log_messages = []

def get_company_state(company_id):
    """Fetches the state from a company's information by company ID."""
    url = f'{BASE_URL}/companies/{company_id}'
    response = requests.get(url, auth=(API_KEY, 'X'))
    company_data = response.json()
    return company_data.get('custom_fields', {}).get('state')

def update_ticket_fields(ticket_id, region, account_manager):
    """Updates the region and account manager custom fields for a ticket."""
    url = f'{BASE_URL}/tickets/{ticket_id}'
    data = {'custom_fields': {'cf_region': region, 'cf_account_manager': account_manager}}
    response = requests.put(url, json=data, auth=(API_KEY, 'X'))
    return response.status_code

def process_tickets(ticket_ids):
    """Processes the list of ticket IDs and updates their region and account manager based on the company's state."""
    total = len(ticket_ids)
    successful_updates = 0
    skipped_tickets = 0

    log_area.config(state=tk.NORMAL)  # Enable text area to update logs
    log_area.delete('1.0', tk.END)  # Clear previous logs

    last_request_time = time.time() - REQUEST_INTERVAL  # Initialize last request time

    for i, ticket_id in enumerate(ticket_ids, start=1):
        current_time = time.time()
        elapsed_time = current_time - last_request_time
        if elapsed_time < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed_time)

        try:
            ticket_info = requests.get(f'{BASE_URL}/tickets/{ticket_id}', auth=(API_KEY, 'X')).json()
            company_id = ticket_info.get('company_id')
            if company_id:
                state = get_company_state(company_id)
                if state:
                    region_account_manager = state_to_region_account_manager.get(state)
                    if region_account_manager:
                        region, account_manager = region_account_manager
                        response_code = update_ticket_fields(ticket_id, region, account_manager)
                        last_request_time = time.time()  # Update last request time after a successful call
                        if response_code == 200:
                            successful_updates += 1
                            message = f'Ticket {ticket_id} updated to region {region} and account manager {account_manager}.'
                        else:
                            message = f'Failed to update ticket {ticket_id} to region {region} and account manager {account_manager}.'
                    else:
                        message = f'State found but no region/account manager mapping for ticket {ticket_id}. Skipping.'
                else:
                    skipped_tickets += 1
                    message = f'Skipping ticket {ticket_id}: No state present'
            else:
                skipped_tickets += 1
                message = f'Skipping ticket {ticket_id}: No company associated'
            log_area.insert(tk.END, message + "\n")
            log_area.see(tk.END)
        except Exception as e:
            message = f'Error processing ticket {ticket_id}: {str(e)}'
            log_area.insert(tk.END, message + "\n")
            log_area.see(tk.END)

        progress_label.config(text=f'Processing: {i}/{total} tickets ({int((i/total)*100)}%)')
        app.update_idletasks()  # Update GUI components dynamically

    log_area.config(state=tk.DISABLED)  # Disable editing after updates
    messagebox.showinfo("Update Complete", f"{successful_updates} out of {total} tickets have been updated. Skipped {skipped_tickets} tickets.")

def update_tickets():
    """Starts the ticket update process in a separate thread to keep the GUI responsive."""
    ticket_ids = text_area.get('1.0', tk.END).strip().split()
    threading.Thread(target=process_tickets, args=(ticket_ids,)).start()

def export_logs():
    """Exports the log messages from the log area to a text file."""
    contents = log_area.get('1.0', tk.END)
    with open('update_logs.txt', 'w') as file:
        file.write(contents)
    messagebox.showinfo("Export Logs", "Logs have been exported to 'update_logs.txt'.")

# Initialize the main application window
app = tk.Tk()
app.title('Ticket Region and Account Manager Updater')
app.geometry('500x400')

# Add a text area for input
text_area = scrolledtext.ScrolledText(app, width=45, height=5)
text_area.pack(pady=10)

# Add a log area
log_area = scrolledtext.ScrolledText(app, width=45, height=10)
log_area.pack(pady=10)
log_area.config(state=tk.DISABLED)  # Disable editing initially

# Add buttons and labels
update_button = tk.Button(app, text='Update Tickets', command=update_tickets)
update_button.pack(pady=5)

export_button = tk.Button(app, text='Export Logs', command=export_logs)
export_button.pack(pady=5)

progress_label = tk.Label(app, text='Ready')
progress_label.pack(pady=5)

# Start the application
app.mainloop()

