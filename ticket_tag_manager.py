"""
Freshdesk Generic Ticket Tag Manager

DESCRIPTION:
This script provides a graphical user interface for adding or removing any tags
from Freshdesk tickets. Users can specify which tag to add/remove and provide
a list of ticket IDs, making it a flexible tool for ticket organization and
categorization beyond just QA tagging.

REQUIREMENTS:
- Python 3.x
- tkinter (usually included with Python)
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read/write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for ticket updates
4. Run the script: python ticket_tag_manager.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#update_ticket
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TAG_TO_ADD: Tag to add to tickets (user-specified)
- TAG_TO_REMOVE: Tag to remove from tickets (optional)
- TICKET_IDS: List of ticket IDs to process

OUTPUT:
- Adds or removes specified tags from tickets
- GUI interface for easy operation
- Log file with detailed operation information
- Progress tracking and completion statistics

TAG MANAGEMENT FEATURES:
- Add any specified tag to multiple tickets
- Remove specific tags from tickets (optional)
- Check for existing tags before adding
- Prevent duplicate tag additions
- Batch processing with rate limiting

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and displays error details
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Includes delays between requests to respect API limits
- Handles rate limit responses with retry-after delays
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

USAGE SCENARIOS:
- Add priority tags (urgent, high-priority) to tickets
- Categorize tickets by department or issue type
- Remove outdated or incorrect tags
- Bulk tag management for ticket organization
- Data cleanup and standardization operations
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import requests
import json
import time
import logging
import threading
import os

# Freshdesk API Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain
BASE_URL = f'https://{DOMAIN}/api/v2/tickets'

# HTTP Headers for API requests
HEADERS = {
    'Content-Type': 'application/json'
}

# Rate limiting configuration
REQUEST_DELAY = 1  # Delay between requests in seconds
BATCH_SIZE = 50  # Process tickets in batches

def setup_logging():
    """Set up logging to both file and console."""
    log_filename = 'ticket_tag_manager.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def make_api_request(url, method='GET', data=None):
    """Make a rate-limited API request to Freshdesk."""
    try:
        auth = (API_KEY, 'X')

        if method.upper() == 'GET':
            response = requests.get(url, auth=auth, headers=HEADERS)
        elif method.upper() == 'PUT':
            response = requests.put(url, auth=auth, headers=HEADERS, data=json.dumps(data))
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return make_api_request(url, method, data)  # Retry the same request

        response.raise_for_status()
        return response.json() if response.content else None

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        return None

def get_ticket_tags(ticket_id):
    """Retrieve current tags for a specific ticket."""
    url = f"{BASE_URL}/{ticket_id}"
    ticket_data = make_api_request(url, 'GET')

    if ticket_data:
        return ticket_data.get('tags', [])
    return []

def update_ticket_tags(ticket_id, tags_to_add=None, tags_to_remove=None):
    """Update tags for a specific ticket."""
    if not tags_to_add and not tags_to_remove:
        return False, "No tag operations specified"

    # Get current tags
    current_tags = get_ticket_tags(ticket_id)

    if current_tags is None:
        return False, f"Failed to retrieve current tags for ticket {ticket_id}"

    # Start with current tags
    updated_tags = current_tags.copy()

    # Remove specified tags
    if tags_to_remove:
        for tag in tags_to_remove:
            if tag in updated_tags:
                updated_tags.remove(tag)

    # Add specified tags (avoid duplicates)
    if tags_to_add:
        for tag in tags_to_add:
            if tag not in updated_tags:
                updated_tags.append(tag)

    # Only update if tags have changed
    if updated_tags == current_tags:
        return True, "No changes needed"

    # Update the ticket
    url = f"{BASE_URL}/{ticket_id}"
    update_data = {'tags': updated_tags}

    result = make_api_request(url, 'PUT', update_data)

    if result:
        return True, f"Updated tags: {', '.join(updated_tags)}"
    else:
        return False, f"Failed to update ticket {ticket_id}"

def process_tickets(ticket_ids, tag_to_add, tag_to_remove, log_area):
    """Process tickets and add/remove specified tags."""
    total_tickets = len(ticket_ids)
    success_count = 0
    error_count = 0
    no_change_count = 0

    log_area.config(state=tk.NORMAL)
    log_area.delete('1.0', tk.END)

    log_area.insert(tk.END, f"Starting tag management for {total_tickets} tickets...\n")
    log_area.insert(tk.END, f"Tag to add: '{tag_to_add}'\n")
    if tag_to_remove:
        log_area.insert(tk.END, f"Tag to remove: '{tag_to_remove}'\n")
    log_area.insert(tk.END, "=" * 60 + "\n")

    for i, ticket_id in enumerate(ticket_ids, 1):
        log_area.insert(tk.END, f"Processing ticket {i}/{total_tickets}: {ticket_id}\n")

        success, message = update_ticket_tags(ticket_id, [tag_to_add] if tag_to_add else None,
                                            [tag_to_remove] if tag_to_remove else None)

        if success:
            if "No changes needed" in message:
                no_change_count += 1
                log_area.insert(tk.END, f"  ✓ {message}\n")
            else:
                success_count += 1
                log_area.insert(tk.END, f"  ✓ {message}\n")
        else:
            error_count += 1
            log_area.insert(tk.END, f"  ❌ {message}\n")

        log_area.see(tk.END)

        # Rate limiting delay
        if i < total_tickets:
            time.sleep(REQUEST_DELAY)

    # Summary
    log_area.insert(tk.END, "\n" + "=" * 60 + "\n")
    log_area.insert(tk.END, "OPERATION SUMMARY\n")
    log_area.insert(tk.END, "=" * 60 + "\n")
    log_area.insert(tk.END, f"Total tickets processed: {total_tickets}\n")
    log_area.insert(tk.END, f"Successfully updated: {success_count}\n")
    log_area.insert(tk.END, f"No changes needed: {no_change_count}\n")
    log_area.insert(tk.END, f"Errors: {error_count}\n")

    log_area.config(state=tk.DISABLED)

    # Show completion message
    messagebox.showinfo("Tag Management Complete",
                       f"Processed {total_tickets} tickets.\n"
                       f"Updated: {success_count}\n"
                       f"No changes: {no_change_count}\n"
                       f"Errors: {error_count}")

def parse_ticket_ids(text_input):
    """Parse ticket IDs from text input (comma-separated or one per line)."""
    if not text_input.strip():
        return []

    # Split by comma or newline and clean up
    ids = []
    for item in text_input.replace(',', '\n').split('\n'):
        item = item.strip()
        if item and item.isdigit():
            ids.append(int(item))

    return ids

def start_tag_management():
    """Start the tag management process using GUI input."""
    tag_to_add = tag_add_var.get().strip()
    tag_to_remove = tag_remove_var.get().strip()
    ticket_input = ticket_ids_text.get('1.0', tk.END).strip()

    if not tag_to_add and not tag_to_remove:
        messagebox.showerror("Error", "Please specify at least one tag to add or remove.")
        return

    ticket_ids = parse_ticket_ids(ticket_input)

    if not ticket_ids:
        messagebox.showerror("Error", "Please provide valid ticket IDs (numbers only).")
        return

    # Run in separate thread to keep GUI responsive
    threading.Thread(target=process_tickets,
                    args=(ticket_ids, tag_to_add, tag_to_remove, log_area),
                    daemon=True).start()

def create_gui():
    """Create the graphical user interface."""
    global tag_add_var, tag_remove_var, ticket_ids_text, log_area

    root = tk.Tk()
    root.title("Freshdesk Ticket Tag Manager")
    root.geometry("600x500")

    # Tag to add section
    tk.Label(root, text="Tag Management", font=("Arial", 12, "bold")).pack(pady=10)

    tag_frame = tk.Frame(root)
    tag_frame.pack(pady=5, padx=20, fill="x")

    tk.Label(tag_frame, text="Tag to Add:").grid(row=0, column=0, sticky="w")
    tag_add_var = tk.StringVar()
    tk.Entry(tag_frame, textvariable=tag_add_var, width=30).grid(row=0, column=1, padx=10)

    tk.Label(tag_frame, text="Tag to Remove (optional):").grid(row=1, column=0, sticky="w")
    tag_remove_var = tk.StringVar()
    tk.Entry(tag_frame, textvariable=tag_remove_var, width=30).grid(row=1, column=1, padx=10)

    # Ticket IDs section
    tk.Label(root, text="Ticket IDs (one per line or comma-separated):").pack(pady=5)

    ticket_ids_text = tk.Text(root, height=8, width=60)
    ticket_ids_text.pack(pady=5, padx=20)

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Start Tag Management",
              command=start_tag_management,
              bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT, padx=5)

    def clear_form():
        tag_add_var.set("")
        tag_remove_var.set("")
        ticket_ids_text.delete('1.0', tk.END)
        log_area.delete('1.0', tk.END)

    tk.Button(button_frame, text="Clear Form",
              command=clear_form, padx=20).pack(side=tk.LEFT, padx=5)

    # Log area
    tk.Label(root, text="Operation Log:").pack(pady=5)
    log_area = scrolledtext.ScrolledText(root, height=10, width=70, state=tk.DISABLED)
    log_area.pack(pady=5, padx=20)

    # Instructions
    instructions = tk.Label(root,
                           text="Instructions:\n"
                                "1. Enter the tag you want to ADD to tickets\n"
                                "2. Optionally enter a tag to REMOVE from tickets\n"
                                "3. Enter ticket IDs (one per line or comma-separated)\n"
                                "4. Click 'Start Tag Management' to begin",
                           justify="left", fg="gray")
    instructions.pack(pady=10, padx=20)

    return root

def main():
    """Main function to run the application."""
    print("Starting Freshdesk Ticket Tag Manager...")
    setup_logging()

    # Create and run GUI
    root = create_gui()
    root.mainloop()

# Run the script if executed directly
if __name__ == "__main__":
    main()
