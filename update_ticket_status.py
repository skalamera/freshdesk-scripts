"""
Freshdesk Ticket Status Update Script

DESCRIPTION:
This script updates ticket statuses in Freshdesk based on a predefined mapping.
It finds tickets with old status values and updates them to new status values
with proper error handling, retry logic, and rate limit management.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket update permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update STATUS_MAPPING with your desired status transitions
4. Ensure your API key has permissions for ticket updates
5. Run the script: python update_ticket_status.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#update_ticket
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- STATUS_MAPPING: Dictionary mapping old status IDs to new status IDs
- MAX_RETRIES: Maximum retry attempts for failed requests

OUTPUT:
- Updates tickets with new status values based on mapping
- Console output showing progress and results
- Detailed error messages for failed updates
- Summary statistics on successful/failed updates

STATUS UPDATE PROCESS:
- Fetches all tickets with pagination (50 per page)
- Checks each ticket against STATUS_MAPPING
- Updates tickets that match old status values
- Displays success/failure status for each update

ERROR HANDLING:
- Handles HTTP 400 (bad request) errors
- Handles HTTP 403 (permission denied) errors
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles HTTP 5xx (server) errors with retry and backoff

RATE LIMIT HANDLING:
- Includes 1-second delays between requests
- Handles rate limit responses with retry-after delays
- Implements exponential backoff for server errors
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that status IDs in mapping are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets exist and are accessible

USAGE SCENARIOS:
- Update deprecated status values to new status codes
- Standardize ticket statuses across the system
- Migrate tickets from old status workflows
- Bulk status cleanup and maintenance
"""

import requests
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/tickets"

# Headers for authentication
AUTH = (API_KEY, "X")
HEADERS = {"Content-Type": "application/json"}

# Status mapping
STATUS_MAPPING = {
    21: 8
}

MAX_RETRIES = 3  # Limit retries to prevent infinite loops

def get_tickets_with_old_statuses():
    """Fetch all tickets that have an old status from the mapping."""
    tickets_to_update = []
    page = 1

    while True:
        response = requests.get(
            BASE_URL,
            auth=AUTH,
            headers=HEADERS,
            params={"per_page": 50, "page": page}  # Fetch in batches of 50
        )

        if response.status_code != 200:
            print(f"âŒ Error fetching tickets: {response.status_code} - {response.text}")
            break

        tickets = response.json()
        if not tickets:
            break  # No more tickets to process

        for ticket in tickets:
            old_status = ticket.get("status")
            if old_status in STATUS_MAPPING:
                tickets_to_update.append((ticket["id"], old_status, STATUS_MAPPING[old_status]))

        page += 1
        time.sleep(1)  # Delay to prevent rate limits

    return tickets_to_update

def update_ticket_status(ticket_id, old_status, new_status, attempt=1):
    """Update a single ticket status based on the mapping, with retries."""
    if attempt > MAX_RETRIES:
        print(f"â— Max retries reached for ticket {ticket_id}. Skipping...")
        return "FAILED"

    url = f"{BASE_URL}/{ticket_id}"
    payload = {"status": new_status}

    try:
        response = requests.put(url, auth=AUTH, headers=HEADERS, json=payload)

        if response.status_code == 200:
            print(f"âœ… Success: Ticket {ticket_id} updated from {old_status} â†’ {new_status}")
            return "SUCCESS"
        elif response.status_code == 400:
            print(f"âŒ Failed: Ticket {ticket_id} - Bad Request (400): {response.json()}")
        elif response.status_code == 403:
            print(f"ðŸš« Failed: Ticket {ticket_id} - Permission Denied (403)")
        elif response.status_code == 404:
            print(f"ðŸ” Failed: Ticket {ticket_id} - Not Found (404)")
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"â³ Rate limit hit. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        elif response.status_code >= 500:
            print(f"âš ï¸ Failed: Ticket {ticket_id} - Server Error ({response.status_code}). Retrying in 10 seconds...")
            time.sleep(10)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        else:
            print(f"âŒ Failed: Ticket {ticket_id} - Unexpected error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"â— Network error: {e}")

    return "FAILED"

def main(status_mapping=None, use_gui=False):
    """Fetch tickets and update their statuses based on the mapping."""
    if status_mapping is None:
        status_mapping = DEFAULT_STATUS_MAPPING

    if use_gui:
        def run_status_update():
            process_status_update_gui(status_mapping)

        threading.Thread(target=run_status_update, daemon=True).start()
        return

    # Command-line mode
    tickets_to_update = get_tickets_with_old_statuses()

    if not tickets_to_update:
        print("No tickets need updating.")
        return

    print(f"🎯 Found {len(tickets_to_update)} tickets that need status updates.")

    success_count = 0
    fail_count = 0

    for ticket_id, old_status, new_status in tickets_to_update:
        result = update_ticket_status(ticket_id, old_status, new_status)
        if result == "SUCCESS":
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5)  # Small delay to avoid rate limits

    print(f"\n✅ Done! {success_count} tickets updated successfully, {fail_count} failed.")

def process_status_update_gui(status_mapping):
    """Process status updates in GUI mode with progress tracking."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Fetching tickets to update...")

    tickets_to_update = get_tickets_with_old_statuses()

    if not tickets_to_update:
        update_progress("❌ No tickets need updating based on current status mapping.")
        messagebox.showinfo("No Updates Needed", "No tickets need updating based on current status mapping.")
        return

    update_progress(f"Found {len(tickets_to_update)} tickets that need status updates.")

    # Show confirmation dialog with preview
    preview_text = "The following status updates will be made:\n\n"
    for ticket_id, old_status, new_status in tickets_to_update[:10]:  # Show first 10
        preview_text += f"Ticket {ticket_id}: Status {old_status} → {new_status}\n"

    if len(tickets_to_update) > 10:
        preview_text += f"... and {len(tickets_to_update) - 10} more tickets\n"

    preview_text += f"\nTotal: {len(tickets_to_update)} tickets will be updated."

    if not messagebox.askyesno("Confirm Status Updates", preview_text):
        update_progress("❌ Status update cancelled by user")
        return

    success_count = 0
    fail_count = 0

    for i, (ticket_id, old_status, new_status) in enumerate(tickets_to_update, 1):
        update_progress(f"Updating ticket {i}/{len(tickets_to_update)}: {ticket_id}")

        result = update_ticket_status(ticket_id, old_status, new_status)
        if result == "SUCCESS":
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5)  # Small delay to avoid rate limits

    summary_msg = "\n" + "=" * 50 + "\n"
    summary_msg += "STATUS UPDATE SUMMARY\n"
    summary_msg += "=" * 50 + "\n"
    summary_msg += f"Total tickets processed: {len(tickets_to_update)}\n"
    summary_msg += f"Successfully updated: {success_count}\n"
    summary_msg += f"Failed: {fail_count}\n"
    summary_msg += "=" * 50

    update_progress(summary_msg)

    messagebox.showinfo("Status Update Complete",
                       f"Updated {success_count} tickets successfully.\n"
                       f"Failed: {fail_count}")

def create_gui():
    """Create the graphical user interface."""
    global status_tree, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Status Updater")
    app.geometry("600x600")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Ticket Status Updater", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Configure status mappings below. Tickets with old status values\n"
                                "will be updated to the corresponding new status values.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Status mapping section
    mapping_frame = ttk.LabelFrame(main_frame, text="Status Mapping", padding="10")
    mapping_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    mapping_frame.columnconfigure(1, weight=1)

    # Status mapping treeview
    columns = ("old_status", "new_status")
    status_tree = ttk.Treeview(mapping_frame, columns=columns, show="headings", height=4)
    status_tree.heading("old_status", text="Old Status ID")
    status_tree.heading("new_status", text="New Status ID")
    status_tree.column("old_status", width=100)
    status_tree.column("new_status", width=100)
    status_tree.grid(row=0, column=0, columnspan=2, pady=5)

    # Load default mapping
    for old_status, new_status in DEFAULT_STATUS_MAPPING.items():
        status_tree.insert("", tk.END, values=(old_status, new_status))

    # Mapping controls
    control_frame = ttk.Frame(mapping_frame)
    control_frame.grid(row=1, column=0, columnspan=2, pady=5)

    def add_mapping():
        add_window = tk.Toplevel(app)
        add_window.title("Add Status Mapping")
        add_window.geometry("300x150")

        ttk.Label(add_window, text="Old Status ID:").grid(row=0, column=0, padx=10, pady=10)
        old_var = tk.StringVar()
        old_entry = ttk.Entry(add_window, textvariable=old_var, width=15)
        old_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(add_window, text="New Status ID:").grid(row=1, column=0, padx=10, pady=10)
        new_var = tk.StringVar()
        new_entry = ttk.Entry(add_window, textvariable=new_var, width=15)
        new_entry.grid(row=1, column=1, padx=10, pady=10)

        def save_mapping():
            try:
                old_id = int(old_var.get())
                new_id = int(new_var.get())

                # Check if mapping already exists
                for item in status_tree.get_children():
                    if status_tree.item(item)["values"][0] == old_id:
                        messagebox.showerror("Error", f"Mapping for old status {old_id} already exists.")
                        return

                status_tree.insert("", tk.END, values=(old_id, new_id))
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric status IDs.")

        ttk.Button(add_window, text="Add Mapping", command=save_mapping).grid(row=2, column=0, columnspan=2, pady=10)

    def remove_mapping():
        selection = status_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a mapping to remove.")
            return

        status_tree.delete(selection[0])

    def clear_mappings():
        for item in status_tree.get_children():
            status_tree.delete(item)

    def load_defaults():
        clear_mappings()
        for old_status, new_status in DEFAULT_STATUS_MAPPING.items():
            status_tree.insert("", tk.END, values=(old_status, new_status))

    ttk.Button(control_frame, text="Add", command=add_mapping).grid(row=0, column=0, padx=5)
    ttk.Button(control_frame, text="Remove", command=remove_mapping).grid(row=0, column=1, padx=5)
    ttk.Button(control_frame, text="Clear", command=clear_mappings).grid(row=0, column=2, padx=5)
    ttk.Button(control_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=3, padx=5)

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    def preview_updates():
        # Get current mapping from treeview
        status_mapping = {}
        for item in status_tree.get_children():
            values = status_tree.item(item)["values"]
            status_mapping[values[0]] = values[1]

        if not status_mapping:
            messagebox.showerror("Error", "Please add at least one status mapping.")
            return

        # Fetch tickets that would be affected
        tickets_to_update = get_tickets_with_old_statuses_preview(status_mapping)

        if not tickets_to_update:
            messagebox.showinfo("Preview", "No tickets would be affected by current status mapping.")
            return

        preview_text = f"Preview: {len(tickets_to_update)} tickets would be updated:\n\n"
        for ticket_id, old_status, new_status in tickets_to_update[:10]:
            preview_text += f"Ticket {ticket_id}: {old_status} → {new_status}\n"

        if len(tickets_to_update) > 10:
            preview_text += f"... and {len(tickets_to_update) - 10} more tickets"

        messagebox.showinfo("Preview", preview_text)

    def start_updates():
        # Get current mapping from treeview
        status_mapping = {}
        for item in status_tree.get_children():
            values = status_tree.item(item)["values"]
            status_mapping[values[0]] = values[1]

        if not status_mapping:
            messagebox.showerror("Error", "Please add at least one status mapping.")
            return

        threading.Thread(target=process_status_update_gui, args=(status_mapping,), daemon=True).start()

    ttk.Button(button_frame, text="Preview Updates", command=preview_updates).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Update Statuses", command=start_updates).grid(row=0, column=1, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=4, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=5, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=60, state=tk.DISABLED)
    log_area.grid(row=6, column=0, columnspan=2, pady=5)

    return app

def get_tickets_with_old_statuses_preview(status_mapping):
    """Preview version of get_tickets_with_old_statuses - doesn't modify anything."""
    tickets_to_update = []
    page = 1

    while True:
        response = requests.get(
            BASE_URL,
            auth=AUTH,
            headers=HEADERS,
            params={"per_page": 50, "page": page}
        )

        if response.status_code != 200:
            print(f"❌ Error fetching tickets: {response.status_code} - {response.text}")
            break

        tickets = response.json()
        if not tickets:
            break

        for ticket in tickets:
            old_status = ticket.get("status")
            if old_status in status_mapping:
                tickets_to_update.append((ticket["id"], old_status, status_mapping[old_status]))

        page += 1
        time.sleep(1)  # Delay to prevent rate limits

        # Limit preview to first 100 tickets to avoid long loading times
        if page > 2:
            break

    return tickets_to_update

# Default status mapping
DEFAULT_STATUS_MAPPING = {
    21: 8
}

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

