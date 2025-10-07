"""
Freshdesk Ticket Attachment Upload Script

DESCRIPTION:
This script adds an attachment to a Freshdesk ticket by creating a private note
with the attached file. It uploads image files (or other file types) to existing
tickets for documentation and reference purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket and conversation write permissions
- Freshdesk account and domain access
- Valid attachment file path

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TICKET_ID with the ticket you want to attach files to
4. Update ATTACHMENT_PATH with the path to your attachment file
5. Ensure your API key has permissions for ticket and conversation access
6. Run the script: python update_ticket_with_attach.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Conversations API: https://developers.freshdesk.com/api/#create_conversation
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TICKET_ID: ID of the ticket to attach files to
- ATTACHMENT_PATH: Local path to the file to attach

OUTPUT:
- Adds attachment as a private note to the specified ticket
- Console output showing success/failure status
- Error messages if upload fails

ATTACHMENT PROCESS:
- Creates a private note with the attachment
- Supports various file types (images, documents, etc.)
- Uses multipart/form-data for file upload
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
- Check that ticket ID is valid and accessible
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Attach screenshots for bug reports or issue documentation
- Upload reference documents to support tickets
- Add evidence or supporting files to cases
- Document issues with visual or file-based evidence
"""

import requests
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
DEFAULT_TICKET_ID = 298629
DEFAULT_ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for adding a note with an attachment
url = f"https://{DOMAIN}/api/v2/tickets/{TICKET_ID}/notes"

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
}

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Data payload (private note with attachment)
    data = {
        "body": "Here is the attached screenshot for the ticket.",
        "private": "true"  # Freshdesk API expects a string "true"/"false" instead of a boolean
    }

    # Send POST request using multipart/form-data
    response = requests.post(url, auth=(API_KEY, "X"), files=files, data=data)

# Handle response
if response.status_code == 201:
    print("âœ… Attachment added successfully as a note!")
elif response.status_code == 429:
    print("âš ï¸ Rate limit exceeded. Try again later.")
else:
    print(f"❌ Failed to add attachment: {response.status_code}, {response.text}")

def main(attachment_config=None, use_gui=False):
    """Main function with optional GUI mode."""
    if attachment_config is None:
        attachment_config = {
            'ticket_id': DEFAULT_TICKET_ID,
            'attachment_path': DEFAULT_ATTACHMENT_PATH,
            'note_body': 'Here is the attached screenshot for the ticket.',
            'private': True
        }

    if use_gui:
        def run_attachment_upload():
            process_attachment_upload_gui(attachment_config)

        threading.Thread(target=run_attachment_upload, daemon=True).start()
        return

    # Command-line mode
    print("Starting attachment upload...")

    # Validate attachment file exists
    if not os.path.exists(attachment_config['attachment_path']):
        print(f"❌ Attachment file not found: {attachment_config['attachment_path']}")
        return

    upload_attachment_to_ticket(attachment_config)

def process_attachment_upload_gui(attachment_config):
    """Process attachment upload in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Starting attachment upload...")

    # Validate attachment file exists
    if not os.path.exists(attachment_config['attachment_path']):
        update_progress(f"❌ Attachment file not found: {attachment_config['attachment_path']}")
        messagebox.showerror("Error", f"Attachment file not found: {attachment_config['attachment_path']}")
        return

    update_progress("Uploading attachment to ticket...")
    success = upload_attachment_to_ticket(attachment_config)

    if success:
        update_progress("✅ Attachment uploaded successfully!")
        messagebox.showinfo("Success", "Attachment uploaded successfully to the ticket!")
    else:
        update_progress("❌ Failed to upload attachment")
        messagebox.showerror("Error", "Failed to upload attachment")

def create_gui():
    """Create the graphical user interface."""
    global ticket_id_var, attachment_path_var, note_body_text, private_var, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Attachment Uploader")
    app.geometry("600x600")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Ticket Attachment Uploader", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Upload an attachment to an existing Freshdesk ticket.\n"
                                "The attachment will be added as a private note to the ticket.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Form fields
    form_frame = ttk.LabelFrame(main_frame, text="Upload Details", padding="10")
    form_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    form_frame.columnconfigure(1, weight=1)

    # Ticket ID
    ttk.Label(form_frame, text="Ticket ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ticket_id_var = tk.StringVar(value=str(DEFAULT_TICKET_ID))
    ticket_id_entry = ttk.Entry(form_frame, textvariable=ticket_id_var, width=30)
    ticket_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Attachment path
    ttk.Label(form_frame, text="Attachment File:").grid(row=1, column=0, sticky=tk.W, pady=5)
    attachment_path_var = tk.StringVar(value=DEFAULT_ATTACHMENT_PATH)

    path_frame = ttk.Frame(form_frame)
    path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
    path_frame.columnconfigure(0, weight=1)

    attachment_path_entry = ttk.Entry(path_frame, textvariable=attachment_path_var, width=25)
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

    # Note body
    ttk.Label(form_frame, text="Note Body:").grid(row=2, column=0, sticky=tk.W, pady=5)
    note_body_text = tk.Text(form_frame, height=3, width=30)
    note_body_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
    note_body_text.insert('1.0', 'Here is the attached screenshot for the ticket.')

    # Private note checkbox
    private_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(form_frame, text="Private Note (visible only to agents)",
                   variable=private_var).grid(row=3, column=0, columnspan=2, pady=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    def preview_upload():
        try:
            ticket_id = int(ticket_id_var.get())
            attachment_path = attachment_path_var.get()
            note_body = note_body_text.get('1.0', tk.END).strip()
            private = private_var.get()

            if not attachment_path:
                messagebox.showerror("Error", "Please select an attachment file.")
                return

            if not os.path.exists(attachment_path):
                messagebox.showerror("Error", f"Attachment file not found: {attachment_path}")
                return

            preview_text = "Upload Preview:\n\n"
            preview_text += f"Ticket ID: #{ticket_id}\n"
            preview_text += f"Attachment: {os.path.basename(attachment_path)}\n"
            preview_text += f"File Size: {os.path.getsize(attachment_path)} bytes\n"
            preview_text += f"Note Type: {'Private' if private else 'Public'}\n"
            preview_text += f"Note Body: {note_body[:50]}{'...' if len(note_body) > 50 else ''}"

            messagebox.showinfo("Upload Preview", preview_text)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid ticket ID.")

    def start_upload():
        try:
            # Validate inputs
            ticket_id = int(ticket_id_var.get())
            attachment_path = attachment_path_var.get()
            note_body = note_body_text.get('1.0', tk.END).strip()
            private = private_var.get()

            if not attachment_path:
                messagebox.showerror("Error", "Please select an attachment file.")
                return

            if not os.path.exists(attachment_path):
                messagebox.showerror("Error", f"Attachment file not found: {attachment_path}")
                return

            if not note_body:
                messagebox.showerror("Error", "Please enter a note body.")
                return

            attachment_config = {
                'ticket_id': ticket_id,
                'attachment_path': attachment_path,
                'note_body': note_body,
                'private': private
            }

            threading.Thread(target=process_attachment_upload_gui, args=(attachment_config,), daemon=True).start()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid ticket ID.")

    def load_defaults():
        ticket_id_var.set(str(DEFAULT_TICKET_ID))
        attachment_path_var.set(DEFAULT_ATTACHMENT_PATH)
        note_body_text.delete('1.0', tk.END)
        note_body_text.insert('1.0', 'Here is the attached screenshot for the ticket.')
        private_var.set(True)

    ttk.Button(button_frame, text="Preview Upload", command=preview_upload).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Upload Attachment", command=start_upload).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=2, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=4, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=5, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=60, state=tk.DISABLED)
    log_area.grid(row=6, column=0, columnspan=2, pady=5)

    return app

def upload_attachment_to_ticket(attachment_config):
    """Upload attachment to ticket - refactored to accept configuration."""
    # API URL for adding a note with an attachment
    url = f"https://{DOMAIN}/api/v2/tickets/{attachment_config['ticket_id']}/notes"

    # Headers for authentication
    headers = {
        "Authorization": f"{API_KEY}:X",
    }

    try:
        # Open the attachment file
        with open(attachment_config['attachment_path'], "rb") as file:
            files = {
                "attachments[]": (os.path.basename(attachment_config['attachment_path']), file, "application/octet-stream"),
            }

            # Data payload (private note with attachment)
            data = {
                "body": attachment_config['note_body'],
                "private": "true" if attachment_config['private'] else "false"
            }

            # Send POST request using multipart/form-data
            response = requests.post(url, auth=(API_KEY, "X"), files=files, data=data)

        # Handle response
        if response.status_code == 201:
            print("✅ Attachment added successfully as a note!")
            return True
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded. Try again later.")
            return False
        else:
            print(f"❌ Failed to add attachment: {response.status_code}, {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error uploading attachment: {str(e)}")
        return False

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

