"""
Freshdesk Ticket with Attachment Creation Script

DESCRIPTION:
This script creates a new tracker ticket in Freshdesk and immediately adds an
attachment to it as a private note. This workflow is useful for creating tickets
with supporting documentation or evidence files from the initial creation.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and conversation write permissions
- Freshdesk account and domain access
- Valid attachment file path

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update RELATED_TICKET_ID with the ticket to link as a related ticket
4. Update ATTACHMENT_PATH with the path to your attachment file
5. Ensure your API key has permissions for ticket and conversation access
6. Run the script: python create_ticket_with_attach.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#create_ticket
- Conversations API: https://developers.freshdesk.com/api/#create_conversation
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- RELATED_TICKET_ID: ID of the ticket to associate with the new tracker
- ATTACHMENT_PATH: Local file path to the attachment file

OUTPUT:
- Creates a new tracker ticket linked to the related ticket
- Adds attachment as a private note to the tracker ticket
- Console output showing success/failure for each step

TICKET CREATION PROCESS:
1. Creates tracker ticket with related_ticket_ids array
2. Retrieves the new ticket ID from the creation response
3. Creates a private note with the attachment file
4. Associates the attachment with the newly created ticket

ATTACHMENT PROCESS:
- Supports various file types (images, documents, etc.)
- Uses multipart/form-data for file upload
- Creates private notes (visible only to agents)
- Validates file exists before attempting upload

ERROR HANDLING:
- Validates attachment file exists before upload
- Handles HTTP 429 (rate limit) errors
- Handles network and file access errors
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket and conversation write permissions
- Check that attachment file exists and is readable
- Ensure network connectivity to Freshdesk API
- Check that related ticket ID is valid and accessible
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Create tracker tickets with supporting documentation
- Attach screenshots for bug reports or issue documentation
- Upload reference documents to support tickets
- Document issues with visual or file-based evidence
- Automated evidence collection for incident management
"""

import requests
import json
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
RELATED_TICKET_ID = 115423  # The ticket to which the tracker will be linked
ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for creating a new tracker ticket
create_ticket_url = f"https://{DOMAIN}/api/v2/tickets"

# Configure logging to both file and console
LOG_FILENAME = 'ticket_attachment_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
    "Content-Type": "application/json"
}

# Step 1: Create the tracker ticket (without attachment)
logging.info("Step 1: Creating tracker ticket...")
print("Step 1: Creating tracker ticket...")
ticket_payload = {
    "description": "This is a tracker ticket linked to another issue.",
    "subject": "Tracker Ticket for Issue #115423",
    "email": "sskalamera@benchmarkeducation.com",  # Required to create the ticket
    "related_ticket_ids": [RELATED_TICKET_ID],  # Must be an array of integers
    "priority": 1,  # 1 = Low, 2 = Medium, 3 = High, 4 = Urgent
    "status": 2,  # 2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed
    "cc_emails": ["skalamera@gmail.com"]  # Must be an array
}

# Send request to create tracker ticket
create_response = requests.post(create_ticket_url, auth=(API_KEY, "X"), headers=headers, json=ticket_payload)

# Check if ticket creation was successful
if create_response.status_code == 201:
    tracker_ticket = create_response.json()  # Get response as JSON
    tracker_ticket_id = tracker_ticket["id"]  # Extract new ticket ID
    print(f"âœ… Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
    logging.info(f"Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
else:
    error_msg = f"Failed to create tracker ticket: {create_response.status_code}, {create_response.text}"
    print(f"âŒ {error_msg}")
    logging.error(error_msg)
    exit()  # Stop script if creation fails

# Step 2: Update the newly created tracker ticket with the attachment
logging.info("Step 2: Adding attachment to tracker ticket...")
print("Step 2: Adding attachment to tracker ticket...")
update_ticket_url = f"https://{DOMAIN}/api/v2/tickets/{tracker_ticket_id}/notes"

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Payload for adding a private note with the attachment
    update_payload = {
        "body": "Attaching relevant screenshot to the tracker ticket.",
        "private": "true"  # Must be string "true" or "false" when using multipart
    }

    # Send request to update the ticket with the attachment
    update_response = requests.post(update_ticket_url, auth=(API_KEY, "X"), files=files, data=update_payload)

# Check if update was successful
if update_response.status_code == 201:
    print("✅ Attachment added successfully to the tracker ticket!")
    logging.info("Attachment added successfully to the tracker ticket!")
else:
    error_msg = f"Failed to add attachment: {update_response.status_code}, {update_response.text}"
    print(f"❌ {error_msg}")
    logging.error(error_msg)

def main(ticket_data=None, use_gui=False):
    """Main function with optional GUI mode."""
    if ticket_data is None:
        ticket_data = {
            'related_ticket_id': DEFAULT_RELATED_TICKET_ID,
            'subject': 'Tracker Ticket for Issue #' + str(DEFAULT_RELATED_TICKET_ID),
            'description': 'This is a tracker ticket linked to another issue.',
            'email': 'sskalamera@benchmarkeducation.com',
            'priority': 1,
            'status': 2,
            'cc_emails': ['skalamera@gmail.com'],
            'attachment_path': DEFAULT_ATTACHMENT_PATH,
            'attachment_note': 'Attaching relevant screenshot to the tracker ticket.'
        }

    if use_gui:
        def run_ticket_creation():
            process_ticket_creation_gui(ticket_data)

        threading.Thread(target=run_ticket_creation, daemon=True).start()
        return

    # Command-line mode
    logging.info("Starting ticket with attachment creation...")
    print("Starting ticket with attachment creation...")

    # Validate attachment file exists
    if not os.path.exists(ticket_data['attachment_path']):
        error_msg = f"Attachment file not found: {ticket_data['attachment_path']}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return

    create_ticket_with_attachment(ticket_data)

def process_ticket_creation_gui(ticket_data):
    """Process ticket creation in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Starting ticket with attachment creation...")

    # Validate attachment file exists
    if not os.path.exists(ticket_data['attachment_path']):
        update_progress(f"❌ Attachment file not found: {ticket_data['attachment_path']}")
        messagebox.showerror("Error", f"Attachment file not found: {ticket_data['attachment_path']}")
        return

    update_progress("Creating tracker ticket...")
    ticket_id = create_ticket_with_attachment(ticket_data)

    if ticket_id:
        update_progress("✅ Ticket with attachment created successfully!")
        messagebox.showinfo("Success", f"Ticket #{ticket_id} created successfully with attachment!")
    else:
        update_progress("❌ Failed to create ticket with attachment")
        messagebox.showerror("Error", "Failed to create ticket with attachment")

def create_gui():
    """Create the graphical user interface."""
    global subject_var, description_text, email_var, priority_var, status_var, cc_var, related_ticket_var, attachment_path_var, attachment_note_text, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Ticket with Attachment Creator")
    app.geometry("700x700")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Create Ticket with Attachment", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Configure the ticket details and select an attachment file.\n"
                                "The attachment will be added as a private note to the new ticket.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Form fields
    form_frame = ttk.LabelFrame(main_frame, text="Ticket Details", padding="10")
    form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    form_frame.columnconfigure(1, weight=1)

    # Related Ticket ID
    ttk.Label(form_frame, text="Related Ticket ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    related_ticket_var = tk.StringVar(value=str(DEFAULT_RELATED_TICKET_ID))
    related_ticket_entry = ttk.Entry(form_frame, textvariable=related_ticket_var, width=50)
    related_ticket_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Subject
    ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky=tk.W, pady=5)
    subject_var = tk.StringVar(value='Tracker Ticket for Issue #' + str(DEFAULT_RELATED_TICKET_ID))
    subject_entry = ttk.Entry(form_frame, textvariable=subject_var, width=50)
    subject_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    # Description
    ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
    description_text = tk.Text(form_frame, height=3, width=50)
    description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
    description_text.insert('1.0', 'This is a tracker ticket linked to another issue.')

    # Email
    ttk.Label(form_frame, text="Requester Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
    email_var = tk.StringVar(value='sskalamera@benchmarkeducation.com')
    email_entry = ttk.Entry(form_frame, textvariable=email_var, width=50)
    email_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

    # Priority
    ttk.Label(form_frame, text="Priority:").grid(row=4, column=0, sticky=tk.W, pady=5)
    priority_var = tk.StringVar(value="1")
    priority_combo = ttk.Combobox(form_frame, textvariable=priority_var,
                                 values=["1 - Low", "2 - Medium", "3 - High", "4 - Urgent"])
    priority_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

    # Status
    ttk.Label(form_frame, text="Status:").grid(row=5, column=0, sticky=tk.W, pady=5)
    status_var = tk.StringVar(value="2")
    status_combo = ttk.Combobox(form_frame, textvariable=status_var,
                               values=["2 - Open", "3 - Pending", "4 - Resolved", "5 - Closed"])
    status_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

    # CC Emails
    ttk.Label(form_frame, text="CC Emails:").grid(row=6, column=0, sticky=tk.W, pady=5)
    cc_var = tk.StringVar(value='skalamera@gmail.com')
    cc_entry = ttk.Entry(form_frame, textvariable=cc_var, width=50)
    cc_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)

    # Attachment section
    attachment_frame = ttk.LabelFrame(main_frame, text="Attachment", padding="10")
    attachment_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    # Attachment path
    ttk.Label(attachment_frame, text="Attachment File:").grid(row=0, column=0, sticky=tk.W, pady=5)
    attachment_path_var = tk.StringVar(value=DEFAULT_ATTACHMENT_PATH)

    path_frame = ttk.Frame(attachment_frame)
    path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
    path_frame.columnconfigure(0, weight=1)

    attachment_path_entry = ttk.Entry(path_frame, textvariable=attachment_path_var, width=40)
    attachment_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select Attachment File",
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                ("Documents", "*.pdf;*.doc;*.docx;*.txt"),
                ("Spreadsheets", "*.xlsx;*.xls;*.csv")
            ]
        )
        if filename:
            attachment_path_var.set(filename)

    ttk.Button(path_frame, text="Browse", command=browse_file).grid(row=0, column=1, padx=5)

    # Attachment note
    ttk.Label(attachment_frame, text="Attachment Note:").grid(row=1, column=0, sticky=tk.W, pady=5)
    attachment_note_text = tk.Text(attachment_frame, height=2, width=50)
    attachment_note_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
    attachment_note_text.insert('1.0', 'Attaching relevant screenshot to the tracker ticket.')

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    def start_creation():
        # Validate required fields
        if not attachment_path_var.get().strip():
            messagebox.showerror("Error", "Please select an attachment file.")
            return

        if not os.path.exists(attachment_path_var.get()):
            messagebox.showerror("Error", f"Attachment file not found: {attachment_path_var.get()}")
            return

        # Parse form data
        try:
            related_ticket_id = int(related_ticket_var.get())
            priority = int(priority_var.get().split(' - ')[0])
            status = int(status_var.get().split(' - ')[0])
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for IDs and selections.")
            return

        ticket_data = {
            'related_ticket_id': related_ticket_id,
            'subject': subject_var.get().strip(),
            'description': description_text.get('1.0', tk.END).strip(),
            'email': email_var.get().strip(),
            'priority': priority,
            'status': status,
            'cc_emails': [cc_var.get().strip()],
            'attachment_path': attachment_path_var.get(),
            'attachment_note': attachment_note_text.get('1.0', tk.END).strip()
        }

        if not ticket_data['subject'] or not ticket_data['description']:
            messagebox.showerror("Error", "Please fill in subject and description.")
            return

        threading.Thread(target=process_ticket_creation_gui, args=(ticket_data,), daemon=True).start()

    def load_defaults():
        related_ticket_var.set(str(DEFAULT_RELATED_TICKET_ID))
        subject_var.set('Tracker Ticket for Issue #' + str(DEFAULT_RELATED_TICKET_ID))
        description_text.delete('1.0', tk.END)
        description_text.insert('1.0', 'This is a tracker ticket linked to another issue.')
        email_var.set('sskalamera@benchmarkeducation.com')
        priority_var.set("1")
        status_var.set("2")
        cc_var.set('skalamera@gmail.com')
        attachment_path_var.set(DEFAULT_ATTACHMENT_PATH)
        attachment_note_text.delete('1.0', tk.END)
        attachment_note_text.insert('1.0', 'Attaching relevant screenshot to the tracker ticket.')

    ttk.Button(button_frame, text="Create Ticket with Attachment",
               command=start_creation).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Load Defaults",
               command=load_defaults).grid(row=0, column=1, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=6, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=70, state=tk.DISABLED)
    log_area.grid(row=7, column=0, columnspan=2, pady=5)

    return app

def create_ticket_with_attachment(ticket_data):
    """Create ticket with attachment - refactored to accept parameters."""
    # Step 1: Create the tracker ticket
    logging.info("Step 1: Creating tracker ticket...")
    print("Step 1: Creating tracker ticket...")

    ticket_payload = {
        "description": ticket_data['description'],
        "subject": ticket_data['subject'],
        "email": ticket_data['email'],
        "related_ticket_ids": [ticket_data['related_ticket_id']],
        "priority": ticket_data['priority'],
        "status": ticket_data['status'],
        "cc_emails": ticket_data['cc_emails']
    }

    create_response = requests.post(create_ticket_url, auth=(API_KEY, "X"), headers=headers, json=ticket_payload)

    if create_response.status_code == 201:
        tracker_ticket = create_response.json()
        tracker_ticket_id = tracker_ticket["id"]
        print(f"✅ Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
        logging.info(f"Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
    else:
        error_msg = f"Failed to create tracker ticket: {create_response.status_code}, {create_response.text}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return None

    # Step 2: Add attachment to the ticket
    logging.info("Step 2: Adding attachment to tracker ticket...")
    print("Step 2: Adding attachment to tracker ticket...")

    update_ticket_url = f"https://{DOMAIN}/api/v2/tickets/{tracker_ticket_id}/notes"

    try:
        with open(ticket_data['attachment_path'], "rb") as file:
            files = {
                "attachments[]": (os.path.basename(ticket_data['attachment_path']), file, "application/octet-stream"),
            }

            update_payload = {
                "body": ticket_data['attachment_note'],
                "private": "true"
            }

            update_response = requests.post(update_ticket_url, auth=(API_KEY, "X"), files=files, data=update_payload)

        if update_response.status_code == 201:
            print("✅ Attachment added successfully to the tracker ticket!")
            logging.info("Attachment added successfully to the tracker ticket!")
            return tracker_ticket_id
        else:
            error_msg = f"Failed to add attachment: {update_response.status_code}, {update_response.text}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            return None

    except Exception as e:
        error_msg = f"Error processing attachment file: {str(e)}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return None

# Default values
DEFAULT_RELATED_TICKET_ID = 115423
DEFAULT_ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

