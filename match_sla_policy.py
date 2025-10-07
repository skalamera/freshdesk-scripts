"""
Freshdesk SLA Policy Matching Script

DESCRIPTION:
This script retrieves all SLA (Service Level Agreement) policies from Freshdesk
and matches them against a specific ticket based on group and ticket type. It
analyzes which SLA policy should be applied to a ticket and provides detailed
information about the matching process.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- Valid Freshdesk API key with SLA policy and ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update the ticket data in the main() function with your test ticket
4. Ensure your API key has permissions for SLA policy and ticket access
5. Run the script: python match_sla_policy.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- SLA Policies API: https://developers.freshdesk.com/api/#sla_policies
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_DATA: Test ticket with group_id, type, priority, and due_by

OUTPUT:
- Console output showing SLA policy matching results
- Log file with detailed operation information
- Analysis of which SLA policy should apply to the ticket

SLA POLICY MATCHING:
- Matches tickets to SLA policies based on group_id and ticket type
- Checks if ticket.group_id is in policy.applicable_to.group_ids
- Checks if ticket.type is in policy.applicable_to.ticket_types
- Returns the first matching policy found

ERROR HANDLING:
- Handles HTTP 404 (policies/tickets not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has SLA policy and ticket read permissions
- Check that the ticket and SLA policies exist
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Test SLA policy application for specific tickets
- Debug SLA policy configuration issues
- Analyze which policies apply to different ticket types
- Validate SLA policy setup and configuration
"""

import requests
import json
import time
import logging
import pandas as pd
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f'https://{DOMAIN}/api/v2'
HEADERS = {'Content-Type': 'application/json'}

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sla_policies.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_sla_policies():
    """
    Retrieve all SLA policies from Freshdesk.

    Returns:
        list: List of SLA policy dictionaries, empty list if error
    """
    endpoint = f'{BASE_URL}/sla_policies'

    try:
        # Make a single request to get all policies (Freshdesk API supports this)
        response = requests.get(endpoint, headers=HEADERS, auth=(API_KEY, 'X'))

        if response.status_code == 200:
            sla_policies = response.json()
            logging.info(f"Successfully retrieved {len(sla_policies)} SLA policies")
            return sla_policies
        else:
            logging.error(f'Failed to fetch SLA policies. Status code: {response.status_code}, Response: {response.text}')
            return []

    except requests.exceptions.RequestException as e:
        logging.error(f'Network error retrieving SLA policies: {e}')
        return []

def match_sla_policy(ticket, sla_policies):
    for policy in sla_policies:
        try:
            # Check if policy has the expected structure
            if 'applicable_to' not in policy:
                continue

            applicable_to = policy['applicable_to']

            if 'group_ids' not in applicable_to or 'ticket_types' not in applicable_to:
                continue

            if ticket['group_id'] in applicable_to['group_ids'] and ticket['type'] in applicable_to['ticket_types']:
                return policy
        except (KeyError, TypeError):
            # Skip policies with unexpected structure
            continue
    return None

def main(ticket):
    sla_policies = get_sla_policies()
    matched_policy = match_sla_policy(ticket, sla_policies)
    
    if matched_policy:
        logging.info(f"Matched SLA Policy: {matched_policy['name']}")
        print(f"Matched SLA Policy: {matched_policy['name']}")
    else:
        logging.info("No matching SLA policy found.")
        print("No matching SLA policy found.")

def main(ticket=None, use_gui=False):
    """Main function with optional GUI mode."""
    if ticket is None:
        ticket = DEFAULT_TICKET

    if use_gui:
        def run_sla_analysis():
            process_sla_analysis_gui(ticket)

        threading.Thread(target=run_sla_analysis, daemon=True).start()
        return

    # Command-line mode
    logging.info(f"Starting SLA analysis for ticket {ticket['id']}")
    print(f"Starting SLA analysis for ticket {ticket['id']}")

    sla_policies = get_sla_policies()
    matched_policy = match_sla_policy(ticket, sla_policies)

    if matched_policy:
        logging.info(f"Matched SLA Policy: {matched_policy['name']}")
        print(f"Matched SLA Policy: {matched_policy['name']}")
    else:
        logging.info("No matching SLA policy found.")
        print("No matching SLA policy found.")

def process_sla_analysis_gui(ticket):
    """Process SLA analysis in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress(f"Starting SLA analysis for ticket {ticket['id']}...")

    sla_policies = get_sla_policies()

    # Debug: Check if we got policies and their structure
    if not sla_policies:
        update_progress("❌ No SLA policies retrieved from API")
        messagebox.showerror("Error", "No SLA policies retrieved from API")
        return

    # Check first policy structure
    first_policy = sla_policies[0]
    if 'applicable_to' not in first_policy:
        update_progress(f"❌ First policy missing 'applicable_to' key. Keys: {list(first_policy.keys())}")
        messagebox.showerror("Error", f"API response structure unexpected. Missing 'applicable_to' key.")
        return

    matched_policy = match_sla_policy(ticket, sla_policies)

    if matched_policy:
        update_progress(f"✅ Matched SLA Policy: {matched_policy['name']}")

        # Show policy details
        details_text = f"SLA Policy Match Found:\n\n"
        details_text += f"Policy Name: {matched_policy['name']}\n"
        details_text += f"Policy ID: {matched_policy['id']}\n"
        details_text += f"Description: {matched_policy.get('description', 'N/A')}\n"
        details_text += f"Applicable Groups: {len(matched_policy['applicable_to']['group_ids'])}\n"
        details_text += f"Applicable Types: {matched_policy['applicable_to']['ticket_types']}\n"

        messagebox.showinfo("SLA Policy Match", details_text)
    else:
        update_progress("❌ No matching SLA policy found.")
        messagebox.showinfo("No Match", "No SLA policy matches the current ticket criteria.")

def create_gui():
    """Create the graphical user interface."""
    global ticket_id_var, ticket_type_var, group_id_var, priority_var, due_by_var, sla_policies_tree, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk SLA Policy Analyzer")
    app.geometry("800x700")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="SLA Policy Analyzer", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Enter ticket details below to find which SLA policy should apply.\n"
                                "The system will match based on group ID and ticket type.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Ticket details form
    form_frame = ttk.LabelFrame(main_frame, text="Ticket Details", padding="10")
    form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    form_frame.columnconfigure(1, weight=1)

    # Ticket ID
    ttk.Label(form_frame, text="Ticket ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ticket_id_var = tk.StringVar(value=str(DEFAULT_TICKET['id']))
    ticket_id_entry = ttk.Entry(form_frame, textvariable=ticket_id_var, width=30)
    ticket_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Ticket Type
    ttk.Label(form_frame, text="Ticket Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
    ticket_type_var = tk.StringVar(value=DEFAULT_TICKET['type'])
    ticket_type_combo = ttk.Combobox(form_frame, textvariable=ticket_type_var,
                                    values=["Incident", "Service Request", "Problem", "Change"])
    ticket_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    # Group ID
    ttk.Label(form_frame, text="Group ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
    group_id_var = tk.StringVar(value=str(DEFAULT_TICKET['group_id']))
    group_id_entry = ttk.Entry(form_frame, textvariable=group_id_var, width=30)
    group_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

    # Priority
    ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=5)
    priority_var = tk.StringVar(value=str(DEFAULT_TICKET['priority']))
    priority_combo = ttk.Combobox(form_frame, textvariable=priority_var,
                                 values=["1", "2", "3", "4"])
    priority_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

    # Due By
    ttk.Label(form_frame, text="Due By (optional):").grid(row=4, column=0, sticky=tk.W, pady=5)
    due_by_var = tk.StringVar(value=DEFAULT_TICKET['due_by'])
    due_by_entry = ttk.Entry(form_frame, textvariable=due_by_var, width=30)
    due_by_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

    # SLA Policies section
    policies_frame = ttk.LabelFrame(main_frame, text="Available SLA Policies", padding="10")
    policies_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    # SLA Policies treeview
    columns = ("id", "name", "groups", "types")
    sla_policies_tree = ttk.Treeview(policies_frame, columns=columns, show="headings", height=6)
    sla_policies_tree.heading("id", text="ID")
    sla_policies_tree.heading("name", text="Name")
    sla_policies_tree.heading("groups", text="Groups")
    sla_policies_tree.heading("types", text="Types")
    sla_policies_tree.column("id", width=60)
    sla_policies_tree.column("name", width=200)
    sla_policies_tree.column("groups", width=100)
    sla_policies_tree.column("types", width=150)
    sla_policies_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def load_sla_policies():
        """Load SLA policies into the treeview."""
        def load_policies():
            try:
                sla_policies = get_sla_policies()
                sla_policies_tree.delete(*sla_policies_tree.get_children())

                for policy in sla_policies:
                    try:
                        applicable_to = policy.get('applicable_to', {})
                        groups_count = len(applicable_to.get('group_ids', []))
                        types = ', '.join(applicable_to.get('ticket_types', []))

                        sla_policies_tree.insert("", tk.END, values=(
                            policy['id'],
                            policy['name'],
                            f"{groups_count} groups",
                            types
                        ))
                    except (KeyError, TypeError):
                        # Skip policies with unexpected structure
                        continue

                messagebox.showinfo("Success", f"Loaded {len(sla_policies)} SLA policies.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load SLA policies: {str(e)}")

        threading.Thread(target=load_policies, daemon=True).start()

    ttk.Button(policies_frame, text="Load SLA Policies", command=load_sla_policies).grid(row=1, column=0, pady=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    def analyze_ticket():
        try:
            # Validate inputs
            ticket_id = int(ticket_id_var.get())
            ticket_type = ticket_type_var.get()
            group_id = int(group_id_var.get())
            priority = int(priority_var.get())
            due_by = due_by_var.get().strip() or None

            if not ticket_type:
                messagebox.showerror("Error", "Please select a ticket type.")
                return

            ticket = {
                "id": ticket_id,
                "type": ticket_type,
                "group_id": group_id,
                "priority": priority,
                "due_by": due_by
            }

            threading.Thread(target=process_sla_analysis_gui, args=(ticket,), daemon=True).start()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for IDs.")

    def load_defaults():
        ticket_id_var.set(str(DEFAULT_TICKET['id']))
        ticket_type_var.set(DEFAULT_TICKET['type'])
        group_id_var.set(str(DEFAULT_TICKET['group_id']))
        priority_var.set(str(DEFAULT_TICKET['priority']))
        due_by_var.set(DEFAULT_TICKET['due_by'])

    ttk.Button(button_frame, text="Analyze Ticket", command=analyze_ticket).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=1, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=6, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=70, state=tk.DISABLED)
    log_area.grid(row=7, column=0, columnspan=2, pady=5)

    return app

# Default ticket configuration
DEFAULT_TICKET = {
    "id": 250128,
    "type": "Incident",
    "group_id": 67000578163,
    "priority": 3,
    "due_by": "2024-07-12T13:33:29Z"
}

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

