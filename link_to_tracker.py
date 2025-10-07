"""
Freshdesk Ticket to Tracker Association Script

DESCRIPTION:
This script creates an association between a regular ticket and a tracker ticket
in Freshdesk using the ticket association API. It links tickets for better
organization and tracking of related issues.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket update permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TRACKER_ID and TICKET_ID with the appropriate ticket numbers
4. Ensure your API key has permissions for ticket updates
5. Run the script: python link_to_tracker.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Ticket Associations API: https://developers.freshdesk.com/api/#ticket_associations
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TRACKER_ID: ID of the tracker ticket
- TICKET_ID: ID of the ticket to associate with the tracker
- ASSOCIATION_TYPE: Type of association (3 = tracker relationship)

OUTPUT:
- Associates the specified ticket with the tracker ticket
- Console output showing success/failure status
- Detailed response information if successful

ASSOCIATION PROCESS:
- Uses PUT request to update the tracker ticket
- Sets association_type to 3 (tracker relationship)
- Includes both ticket IDs in related_ticket_ids array
- Creates bidirectional association between tickets

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that both ticket IDs are valid
- Ensure network connectivity to Freshdesk API
- Verify that tickets exist and are accessible

USAGE SCENARIOS:
- Link support tickets to their corresponding tracker tickets
- Organize related tickets for better issue tracking
- Create associations for reporting and analysis
- Maintain ticket relationships for workflow management
"""

import requests
import json
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"

# Ticket and tracker IDs
TRACKER_ID = 299766
TICKET_ID = 299585

# API endpoint to update the tracker ticket
url = f"https://{DOMAIN}/api/v2/tickets/{TRACKER_ID}"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Configure logging to both file and console
LOG_FILENAME = 'ticket_tracker_linking.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Data payload to associate both tickets
data = {
    "association_type": 3,  # Ensure the tracker is explicitly defined
    "related_ticket_ids": [TRACKER_ID, TICKET_ID]  # Include both tracker and ticket
}

# Make the request
logging.info("Making API request to link ticket to tracker...")
print("Making API request to link ticket to tracker...")
response = requests.put(
    url,
    auth=(API_KEY, "X"),
    headers=headers,
    data=json.dumps(data)
)

# Output the response
if response.status_code == 200:
    message = "Ticket successfully linked to tracker!"
    print(message)
    print(response.json())
    logging.info(message)
else:
    error_msg = f"Failed to link ticket. Status Code: {response.status_code}"
    print(error_msg)
    print(response.text)
    logging.error(error_msg)

def main(link_config=None, use_gui=False):
    """Main function with optional GUI mode."""
    if link_config is None:
        link_config = {
            'tracker_id': DEFAULT_TRACKER_ID,
            'ticket_id': DEFAULT_TICKET_ID,
            'association_type': 3
        }

    if use_gui:
        def run_link_creation():
            process_link_creation_gui(link_config)

        threading.Thread(target=run_link_creation, daemon=True).start()
        return

    # Command-line mode
    logging.info("Making API request to link ticket to tracker...")
    print("Making API request to link ticket to tracker...")

    link_tickets_to_tracker(link_config)

def process_link_creation_gui(link_config):
    """Process link creation in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Creating ticket association...")

    success = link_tickets_to_tracker(link_config)

    if success:
        update_progress("✅ Tickets successfully linked!")
        messagebox.showinfo("Success", f"Ticket {link_config['ticket_id']} successfully linked to tracker {link_config['tracker_id']}!")
    else:
        update_progress("❌ Failed to link tickets")
        messagebox.showerror("Error", "Failed to link tickets")

def create_gui():
    """Create the graphical user interface."""
    global tracker_id_var, ticket_id_var, association_type_var, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Ticket Association Manager")
    app.geometry("500x500")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Ticket Association Manager", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Link a regular ticket to a tracker ticket for better organization.\n"
                                "This creates a bidirectional association between the tickets.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Form fields
    form_frame = ttk.LabelFrame(main_frame, text="Association Details", padding="10")
    form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    form_frame.columnconfigure(1, weight=1)

    # Tracker ID
    ttk.Label(form_frame, text="Tracker Ticket ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    tracker_id_var = tk.StringVar(value=str(DEFAULT_TRACKER_ID))
    tracker_id_entry = ttk.Entry(form_frame, textvariable=tracker_id_var, width=30)
    tracker_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Ticket ID
    ttk.Label(form_frame, text="Ticket ID to Link:").grid(row=1, column=0, sticky=tk.W, pady=5)
    ticket_id_var = tk.StringVar(value=str(DEFAULT_TICKET_ID))
    ticket_id_entry = ttk.Entry(form_frame, textvariable=ticket_id_var, width=30)
    ticket_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    # Association Type
    ttk.Label(form_frame, text="Association Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
    association_type_var = tk.StringVar(value="3")
    association_type_combo = ttk.Combobox(form_frame, textvariable=association_type_var,
                                         values=["3 - Tracker"], state="readonly")
    association_type_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    def preview_association():
        try:
            tracker_id = int(tracker_id_var.get())
            ticket_id = int(ticket_id_var.get())
            association_type = int(association_type_var.get())

            preview_text = "Association Preview:\n\n"
            preview_text += f"Tracker Ticket: #{tracker_id}\n"
            preview_text += f"Regular Ticket: #{ticket_id}\n"
            preview_text += f"Association Type: {association_type} (Tracker)\n"
            preview_text += "\nThis will create a bidirectional link between these tickets."

            messagebox.showinfo("Association Preview", preview_text)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric ticket IDs.")

    def start_linking():
        try:
            # Validate inputs
            tracker_id = int(tracker_id_var.get())
            ticket_id = int(ticket_id_var.get())
            association_type = int(association_type_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric ticket IDs.")
            return

        link_config = {
            'tracker_id': tracker_id,
            'ticket_id': ticket_id,
            'association_type': association_type
        }

        threading.Thread(target=process_link_creation_gui, args=(link_config,), daemon=True).start()

    def load_defaults():
        tracker_id_var.set(str(DEFAULT_TRACKER_ID))
        ticket_id_var.set(str(DEFAULT_TICKET_ID))
        association_type_var.set("3")

    ttk.Button(button_frame, text="Preview Association", command=preview_association).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Link Tickets", command=start_linking).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=2, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=4, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=5, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=50, state=tk.DISABLED)
    log_area.grid(row=6, column=0, columnspan=2, pady=5)

    return app

def link_tickets_to_tracker(link_config):
    """Link tickets to tracker - refactored to accept configuration."""
    logging.info("Making API request to link ticket to tracker...")
    print("Making API request to link ticket to tracker...")

    # API endpoint to update the tracker ticket
    url = f"https://{DOMAIN}/api/v2/tickets/{link_config['tracker_id']}"

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Data payload to associate both tickets
    data = {
        "association_type": link_config['association_type'],
        "related_ticket_ids": [link_config['tracker_id'], link_config['ticket_id']]
    }

    response = requests.put(
        url,
        auth=(API_KEY, "X"),
        headers=headers,
        data=json.dumps(data)
    )

    # Output the response
    if response.status_code == 200:
        message = "Ticket successfully linked to tracker!"
        print(message)
        print(response.json())
        logging.info(message)
        return True
    else:
        error_msg = f"Failed to link ticket. Status Code: {response.status_code}"
        print(error_msg)
        print(response.text)
        logging.error(error_msg)
        return False

# Default values
DEFAULT_TRACKER_ID = 299766
DEFAULT_TICKET_ID = 299585

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

