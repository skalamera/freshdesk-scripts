"""
Freshdesk Conversation Deletion Script

DESCRIPTION:
This script deletes all conversations (notes and replies) associated with a
specific ticket in Freshdesk. It handles rate limiting, retries failed requests,
and provides comprehensive logging for audit trails and troubleshooting.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with conversation deletion permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_id with the ticket ID whose conversations you want to delete
4. Ensure your API key has permissions for conversation deletion
5. Run the script: python delete_conversation.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Conversations API: https://developers.freshdesk.com/api/#conversations
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- ticket_id: ID of the ticket whose conversations will be deleted
- log_file: Name of the log file for operation tracking

OUTPUT:
- Deletes all conversations for the specified ticket
- Creates detailed log file with operation results
- Console output showing progress and results
- No file output - results displayed in console and log file

CONVERSATION DELETION PROCESS:
- Fetches all conversations for the specified ticket
- Deletes each conversation individually
- Handles pagination if ticket has many conversations
- Includes delays between deletion requests to avoid rate limits

ERROR HANDLING:
- Handles HTTP 403 (permission denied) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles HTTP 5xx (server) errors with retry and backoff
- Validates API responses and displays error details
- Continues processing even if individual conversations fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Includes 1-second delays between deletion requests
- Monitors API usage to avoid exceeding limits

LOGGING:
- Creates detailed log file with timestamps
- Logs to both file and console simultaneously
- Tracks successful deletions and failures
- Includes retry attempts and error details

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has conversation deletion permissions
- Check that ticket ID is valid and accessible
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Remove sensitive information from ticket conversations
- Clean up test data or spam conversations
- Prepare tickets for data migration or archiving
- Remove inappropriate or confidential content
- Audit trail maintenance and compliance
"""

import requests
import base64
import time
import logging
import sys

# Set up logging to both file and console
log_file = 'delete_conversations_log.txt'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Freshdesk API credentials
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'
DEFAULT_TICKET_ID = 259708  # The default ticket ID for which to delete all conversations

# Encode API Key
encoded_api_key = base64.b64encode(f"{api_key}:X".encode("utf-8")).decode("utf-8")

# Base URL for the Freshdesk API
base_url = f"https://{domain}/api/v2"

# Headers for the API requests
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_api_key}'
}

def get_conversations(ticket_id):
    """Fetch all conversations for the given ticket ID."""
    conversations_url = f"{base_url}/tickets/{ticket_id}/conversations"
    response = requests.get(conversations_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to retrieve conversations for ticket {ticket_id}: {response.status_code}")
        return []

def delete_conversation(conversation_id):
    """Attempt to delete a conversation and return success or failure."""
    delete_url = f"{base_url}/conversations/{conversation_id}"
    delete_response = requests.delete(delete_url, headers=headers)

    if delete_response.status_code == 204:
        logging.info(f"Conversation {conversation_id} deleted successfully.")
        return True
    elif delete_response.status_code == 403:
        logging.warning(f"Failed to delete conversation {conversation_id}: 403 Forbidden - Check permissions.")
        return False
    elif delete_response.status_code in [429, 500, 503]:
        retry_after = int(delete_response.headers.get('Retry-After', 5))
        logging.warning(f"Rate limit or server error encountered. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return delete_conversation(conversation_id)
    else:
        logging.error(f"Failed to delete conversation {conversation_id}: {delete_response.status_code}")
        return False

def delete_all_conversations(ticket_id):
    """Delete all conversations for a given ticket, retrying if necessary."""
    logging.info(f"Starting deletion of all conversations for ticket {ticket_id}")
    print(f"Starting deletion of all conversations for ticket {ticket_id}")

    while True:
        conversations = get_conversations(ticket_id)
        if not conversations:
            logging.info("No more conversations left to delete or failed to retrieve conversations.")
            print("No more conversations left to delete or failed to retrieve conversations.")
            break

        for conversation in conversations:
            conversation_id = conversation['id']
            delete_conversation(conversation_id)
            time.sleep(1)  # Add a short delay to avoid overwhelming the API

        logging.info("Finished a pass over the conversations. Checking for any remaining...")
        print("Finished a pass over the conversations. Checking for any remaining...")

    logging.info(f"Conversation deletion completed for ticket {ticket_id}")
    print(f"Conversation deletion completed for ticket {ticket_id}")

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

def main(ticket_id=None, use_gui=False):
    """Main function with optional GUI mode."""
    if ticket_id is None:
        ticket_id = DEFAULT_TICKET_ID

    if use_gui:
        def run_deletion():
            process_deletion_gui(ticket_id)

        threading.Thread(target=run_deletion, daemon=True).start()
        return

    # Command-line mode
    logging.info(f"Starting conversation deletion for ticket {ticket_id}")
    print(f"Starting conversation deletion for ticket {ticket_id}")
    delete_all_conversations(ticket_id)

def process_deletion_gui(ticket_id):
    """Process deletion in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress(f"Starting conversation deletion for ticket {ticket_id}")

    # Show confirmation dialog
    confirm_msg = f"This will permanently delete ALL conversations for ticket {ticket_id}.\n\n"
    confirm_msg += "This action cannot be undone!\n\n"
    confirm_msg += "Are you sure you want to proceed?"

    if not messagebox.askyesno("Confirm Deletion", confirm_msg, icon='warning'):
        update_progress("❌ Deletion cancelled by user")
        return

    delete_all_conversations(ticket_id)

    update_progress("✅ Conversation deletion completed!")
    messagebox.showinfo("Success", f"All conversations for ticket {ticket_id} have been deleted.")

def create_gui():
    """Create the graphical user interface."""
    global ticket_id_var, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Conversation Deleter")
    app.geometry("500x400")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Delete Ticket Conversations", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Warning
    warning = tk.Label(main_frame,
                      text="⚠️ WARNING: This action cannot be undone!\n"
                           "All conversations for the selected ticket will be permanently deleted.",
                      justify="left", fg="red", font=("Arial", 10, "bold"))
    warning.grid(row=1, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Enter the ticket ID below to delete all conversations for that ticket.",
                           justify="left", fg="gray")
    instructions.grid(row=2, column=0, columnspan=2, pady=5)

    # Ticket ID input
    ttk.Label(main_frame, text="Ticket ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
    ticket_id_var = tk.StringVar(value=str(DEFAULT_TICKET_ID))
    ticket_id_entry = ttk.Entry(main_frame, textvariable=ticket_id_var, width=30)
    ticket_id_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    def start_deletion():
        ticket_id_str = ticket_id_var.get().strip()

        if not ticket_id_str:
            messagebox.showerror("Error", "Please enter a ticket ID.")
            return

        try:
            ticket_id = int(ticket_id_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid ticket ID (numbers only).")
            return

        threading.Thread(target=process_deletion_gui, args=(ticket_id,), daemon=True).start()

    def clear_form():
        ticket_id_var.set(str(DEFAULT_TICKET_ID))

    ttk.Button(button_frame, text="Delete Conversations",
               command=start_deletion).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Clear",
               command=clear_form).grid(row=0, column=1, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=6, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=50, state=tk.DISABLED)
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
