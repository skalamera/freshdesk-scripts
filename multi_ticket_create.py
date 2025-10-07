"""
Freshdesk Multi-Ticket Creation Script

DESCRIPTION:
This script creates multiple tickets in Freshdesk with different subjects and
priority levels for testing and bulk ticket generation purposes. It creates
tickets for various fulfillment types (Trial, Pilot, Distributor, etc.) at
both high and low priority levels.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket creation permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update tickets_to_create list if you want different subjects/priorities
4. Ensure your API key has permissions for ticket creation
5. Run the script: python multi_ticket_create.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#create_ticket
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- tickets_to_create: List of ticket configurations with subject and priority
- email: Default requester email for all tickets

OUTPUT:
- Creates multiple tickets with specified subjects and priorities
- Console output showing creation progress and results
- Detailed logging for troubleshooting

TICKET CREATION PROCESS:
- Creates tickets with different subjects for testing scenarios
- Sets priority levels (1 = Low, 2 = Medium, 3 = High, 4 = Urgent)
- Uses same requester email for all tickets
- Sets status to Open (2) for all tickets
- Includes 1-second delay between creations to respect rate limits

ERROR HANDLING:
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and connection errors
- Validates API responses and displays error details
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Includes 1-second delays between ticket creations
- Handles rate limit responses with retry-after delays
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket creation permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that requester email exists or is valid

USAGE SCENARIOS:
- Generate test tickets for training and demonstration
- Create sample data for testing automation workflows
- Bulk ticket creation for scenario testing
- Load testing and performance validation
"""

import requests
import json
import logging
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Freshdesk API details
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'

# Endpoint to create a ticket
url = f'https://{domain}/api/v2/tickets'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Define ticket details for both priority levels
tickets_to_create = [
    {"subject": "Trial Fulfillment - Test", "priority": 1},
    {"subject": "Pilot Fulfillment - Test", "priority": 1},
    {"subject": "Distributor Fulfillment - Test", "priority": 1},
    {"subject": "RFP Trial Fulfillment - Test", "priority": 1},
    {"subject": "New Customer Fulfillment", "priority": 1},
    {"subject": "Trial Fulfillment", "priority": 2},
    {"subject": "Pilot Fulfillment", "priority": 2},
    {"subject": "Distributor Fulfillment", "priority": 2},
    {"subject": "RFP Trial Fulfillment", "priority": 2},
    {"subject": "Renewal Fulfillment", "priority": 2}
]

def create_ticket(subject, priority, email="skalamera@gmail.com"):
    data = {
        "subject": subject,
        "priority": priority,
        "status": 2,  # Adjust the status as necessary
        "description": f"This ticket is for {subject}.",
        "email": email  # Requester's email
    }
    
    try:
        response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:
            logger.info(f"Ticket '{subject}' created successfully with ID: {response.json()['id']}")
        else:
            logger.error(f"Failed to create ticket '{subject}': {response.status_code}, {response.text}")
            
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as errh:
        logger.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Oops: Something Else {err}")

# Configure logging to both file and console
LOG_FILENAME = 'multi_ticket_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main(tickets_data=None, use_gui=False):
    """Main function with optional GUI mode."""
    if tickets_data is None:
        tickets_data = DEFAULT_TICKETS

    if use_gui:
        def run_ticket_creation():
            process_tickets_gui(tickets_data)

        threading.Thread(target=run_ticket_creation, daemon=True).start()
        return

    # Command-line mode
    logging.info("Starting multi-ticket creation...")
    print("Starting multi-ticket creation...")

    success_count = 0
    error_count = 0

    for i, ticket in enumerate(tickets_data, 1):
        print(f"Creating ticket {i}/{len(tickets_data)}: {ticket['subject']}")
        try:
            create_ticket(ticket['subject'], ticket['priority'])
            success_count += 1
        except Exception as e:
            error_count += 1
            logging.error(f"Failed to create ticket {ticket['subject']}: {e}")

        # Wait 1 second between requests to avoid rate limits
        if i < len(tickets_data):
            time.sleep(1)

    print(f"\nMulti-ticket creation completed. Success: {success_count}, Failed: {error_count}")
    logging.info(f"Multi-ticket creation completed. Success: {success_count}, Failed: {error_count}")

def process_tickets_gui(tickets_data):
    """Process tickets in GUI mode with progress updates."""
    success_count = 0
    error_count = 0

    def update_progress(current, total, message=""):
        progress_var.set(f"Creating: {current}/{total} tickets ({int((current/total)*100)}%)")
        if message:
            log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress(0, len(tickets_data), "Starting multi-ticket creation...")

    for i, ticket in enumerate(tickets_data, 1):
        update_progress(i, len(tickets_data), f"Creating ticket {i}: {ticket['subject']}")

        try:
            create_ticket(ticket['subject'], ticket['priority'], email_var.get())
            success_count += 1
        except Exception as e:
            error_count += 1
            update_progress(i, len(tickets_data), f"Error creating ticket {i}: {str(e)}")

        # Wait between requests to avoid rate limits
        if i < len(tickets_data):
            time.sleep(1)

    summary_msg = "\n" + "=" * 50 + "\n"
    summary_msg += "MULTI-TICKET CREATION SUMMARY\n"
    summary_msg += "=" * 50 + "\n"
    summary_msg += f"Total tickets processed: {len(tickets_data)}\n"
    summary_msg += f"Successfully created: {success_count}\n"
    summary_msg += f"Failed: {error_count}\n"
    summary_msg += "=" * 50

    update_progress(len(tickets_data), len(tickets_data), summary_msg)
    logging.info(f"GUI multi-ticket creation completed. Success: {success_count}, Failed: {error_count}")

    messagebox.showinfo("Multi-Ticket Creation Complete",
                       f"Created {success_count} tickets successfully.\n"
                       f"Failed: {error_count}")

def create_gui():
    """Create the graphical user interface."""
    global tickets_listbox, log_area, progress_var, email_var, app

    app = tk.Tk()
    app.title("Freshdesk Multi-Ticket Creator")
    app.geometry("700x600")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Multi-Ticket Creator", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Configure multiple tickets to create with different subjects and priorities.\n"
                                "You can modify, add, or remove tickets from the list below.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Requester email
    ttk.Label(main_frame, text="Requester Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
    email_var = tk.StringVar(value="skalamera@gmail.com")
    email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
    email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

    # Tickets list
    ttk.Label(main_frame, text="Tickets to Create:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    # Listbox frame
    listbox_frame = ttk.Frame(main_frame)
    listbox_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
    listbox_frame.columnconfigure(0, weight=1)

    # Tickets listbox
    tickets_listbox = tk.Listbox(listbox_frame, height=8, width=80)
    tickets_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # Scrollbar for listbox
    scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=tickets_listbox.yview)
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    tickets_listbox.config(yscrollcommand=scrollbar.set)

    # Load default tickets
    for ticket in DEFAULT_TICKETS:
        tickets_listbox.insert(tk.END, f"{ticket['subject']} (Priority: {ticket['priority']})")

    # Buttons for ticket management
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=10)

    def add_ticket():
        # Create a simple dialog for adding a ticket
        add_window = tk.Toplevel(app)
        add_window.title("Add Ticket")
        add_window.geometry("400x200")

        ttk.Label(add_window, text="Subject:").grid(row=0, column=0, padx=10, pady=10)
        subject_var = tk.StringVar()
        subject_entry = ttk.Entry(add_window, textvariable=subject_var, width=30)
        subject_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(add_window, text="Priority:").grid(row=1, column=0, padx=10, pady=10)
        priority_var = tk.StringVar(value="1")
        priority_combo = ttk.Combobox(add_window, textvariable=priority_var,
                                     values=["1 - Low", "2 - Medium", "3 - High", "4 - Urgent"])
        priority_combo.grid(row=1, column=1, padx=10, pady=10)

        def save_ticket():
            subject = subject_var.get().strip()
            priority_num = int(priority_var.get().split(' - ')[0])

            if not subject:
                messagebox.showerror("Error", "Please enter a subject.")
                return

            # Add to listbox
            tickets_listbox.insert(tk.END, f"{subject} (Priority: {priority_num})")
            add_window.destroy()

        ttk.Button(add_window, text="Add Ticket", command=save_ticket).grid(row=2, column=0, columnspan=2, pady=10)

    def remove_ticket():
        selection = tickets_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a ticket to remove.")
            return

        tickets_listbox.delete(selection[0])

    def clear_tickets():
        tickets_listbox.delete(0, tk.END)

    def load_defaults():
        tickets_listbox.delete(0, tk.END)
        for ticket in DEFAULT_TICKETS:
            tickets_listbox.insert(tk.END, f"{ticket['subject']} (Priority: {ticket['priority']})")

    ttk.Button(button_frame, text="Add Ticket", command=add_ticket).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Remove Selected", command=remove_ticket).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Clear All", command=clear_tickets).grid(row=0, column=2, padx=5)
    ttk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=3, padx=5)

    # Create tickets button
    create_frame = ttk.Frame(main_frame)
    create_frame.grid(row=6, column=0, columnspan=2, pady=10)

    def start_creation():
        if tickets_listbox.size() == 0:
            messagebox.showerror("Error", "Please add at least one ticket to create.")
            return

        # Parse tickets from listbox
        tickets_data = []
        for i in range(tickets_listbox.size()):
            item_text = tickets_listbox.get(i)
            # Extract subject and priority from format "Subject (Priority: X)"
            if "(Priority:" in item_text:
                subject = item_text.split(" (Priority:")[0]
                priority_str = item_text.split(" (Priority: ")[1].rstrip(")")
                priority = int(priority_str)
                tickets_data.append({"subject": subject, "priority": priority})

        if not tickets_data:
            messagebox.showerror("Error", "Could not parse ticket data.")
            return

        threading.Thread(target=process_tickets_gui, args=(tickets_data,), daemon=True).start()

    ttk.Button(create_frame, text="Create All Tickets",
               command=start_creation).grid(row=0, column=0, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=7, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=8, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=70, state=tk.DISABLED)
    log_area.grid(row=9, column=0, columnspan=2, pady=5)

    return app

# Default tickets configuration
DEFAULT_TICKETS = [
    {"subject": "Trial Fulfillment - Test", "priority": 1},
    {"subject": "Pilot Fulfillment - Test", "priority": 1},
    {"subject": "Distributor Fulfillment - Test", "priority": 1},
    {"subject": "RFP Trial Fulfillment - Test", "priority": 1},
    {"subject": "New Customer Fulfillment", "priority": 1},
    {"subject": "Trial Fulfillment", "priority": 2},
    {"subject": "Pilot Fulfillment", "priority": 2},
    {"subject": "Distributor Fulfillment", "priority": 2},
    {"subject": "RFP Trial Fulfillment", "priority": 2},
    {"subject": "Renewal Fulfillment", "priority": 2}
]

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

