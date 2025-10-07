"""
Freshdesk Ticket Tag Addition Script

DESCRIPTION:
This script adds 'qa' tags to multiple Freshdesk tickets in batch. It processes
a predefined list of ticket IDs, checks if they already have the 'qa' tag,
and adds it if missing. Includes rate limiting and comprehensive logging.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with ticket read/write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to tag
4. Ensure your API key has permissions for ticket updates
5. Run the script: python add_tags.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- ticket_ids: List of ticket IDs to add 'qa' tags to
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain

OUTPUT:
- Updates tickets with 'qa' tag if not already present
- Comprehensive logging to console and file
- Progress tracking and rate limit handling

LOGGING:
- Creates detailed logs of all operations
- Logs successful updates, skips, and errors
- Includes timestamps for troubleshooting

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles network and connection errors
- Validates existing tags before updating
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Processes tickets in batches with delays
- Waits 10 seconds every 50 requests
- Respects Freshdesk API rate limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket update permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check logs for detailed error information

PERFORMANCE CONSIDERATIONS:
- Batch processing with rate limit delays
- Large ticket lists may take significant time to process
- Adjust batch size and delays based on your rate limits
"""

import requests
import time
import logging
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ticket_tag_addition.log"),
        logging.StreamHandler()  # Also log to console
    ]
)

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain
API_URL = f"https://{DOMAIN}/api/v2/tickets"

# HTTP Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# Default list of ticket IDs to add 'qa' tags to
# Replace this list with your actual ticket IDs
DEFAULT_TICKET_IDS = [
    292584, 292599, 294867, 294931, 294934, 295987, 297199, 297302, 297903, 298495,
    298514, 298681, 299126, 299921, 294741, 295051, 297006, 294032, 294298, 295213,
    297286, 297988, 294145, 294302, 295478, 295740, 296020, 296247, 297695, 298415,
    298575, 293115, 294340, 295541, 296529, 296964, 297102, 298239, 298479, 298502,
    298951, 297907, 295037, 295053, 296045, 297278, 293650, 294805, 296043, 292670,
    294201, 294967, 295184, 294792, 293707, 296573, 296806, 297227, 297487, 293588,
    295979, 296422, 298171, 293839, 294441, 294618, 295397, 296436, 297201, 297725,
    297862, 297948, 298116, 298179, 299217, 294538, 294099, 296638, 296764, 297311,
    297315, 297393, 297512, 297612, 294438, 294725, 295505, 293406, 294264, 299218
]

# Common tags that can be added
COMMON_TAGS = ['qa', 'urgent', 'high-priority', 'low-priority', 'bug', 'feature', 'enhancement', 'support']

def update_ticket_tags(ticket_id, tag_to_add='qa'):
    """
    Add a specified tag to a specific ticket if not already present.

    This function fetches the current ticket details, checks if the specified tag
    already exists, and adds it if missing.

    Args:
        ticket_id (int): The ticket ID to update
        tag_to_add (str): The tag to add to the ticket

    Returns:
        bool: True if successfully updated, False otherwise
    """
    try:
        # Fetch existing ticket details
        response = requests.get(
            f"{API_URL}/{ticket_id}",
            auth=(API_KEY, "X"),
            headers=HEADERS
        )

        if response.status_code == 200:
            ticket_data = response.json()
            existing_tags = ticket_data.get("tags", [])

            # Check if tag is already present
            if tag_to_add in existing_tags:
                logging.info(f"Ticket {ticket_id} already has '{tag_to_add}' tag. Skipping.")
                return True

            # Add tag to existing tags (remove duplicates)
            updated_tags = list(set(existing_tags + [tag_to_add]))
            payload = {"tags": updated_tags}

            # Update ticket with new tags
            update_response = requests.put(
                f"{API_URL}/{ticket_id}",
                auth=(API_KEY, "X"),
                json=payload,
                headers=HEADERS
            )

            if update_response.status_code == 200:
                logging.info(f"✓ Successfully added '{tag_to_add}' tag to ticket {ticket_id}")
                return True
            else:
                logging.error(f"✗ Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
                return False

        elif response.status_code == 404:
            logging.warning(f"⚠ Ticket {ticket_id} not found (404)")
            return False
        else:
            logging.error(f"✗ Error fetching ticket {ticket_id}: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"✗ Request error for ticket {ticket_id}: {str(e)}")
        return False

def main(ticket_ids=None, tag_to_add='qa', use_gui=False):
    """
    Main function to process all tickets with rate limiting.

    Args:
        ticket_ids (list): List of ticket IDs to process
        tag_to_add (str): Tag to add to tickets
        use_gui (bool): Whether to use GUI mode
    """
    if ticket_ids is None:
        ticket_ids = DEFAULT_TICKET_IDS

    if use_gui:
        # GUI mode - use threading to keep GUI responsive
        def run_batch_update():
            process_tickets_gui(ticket_ids, tag_to_add)

        threading.Thread(target=run_batch_update, daemon=True).start()
        return

    # Command-line mode
    print("Starting batch ticket tag addition...")
    print(f"Processing {len(ticket_ids)} tickets...")
    print(f"Tag to add: {tag_to_add}")
    print("=" * 60)

    success_count = 0
    skip_count = 0
    error_count = 0

    # Process tickets in batches with rate limiting
    for index, ticket_id in enumerate(ticket_ids, start=1):
        print(f"Processing ticket {index}/{len(ticket_ids)}: ID {ticket_id}")

        # Update the ticket
        if update_ticket_tags(ticket_id, tag_to_add):
            success_count += 1
        elif "already has" in str(logging.getLogger().handlers[0].stream.getvalue()):
            skip_count += 1
        else:
            error_count += 1

        # Handle rate limits: pause every 50 requests
        if index % 50 == 0:
            print(f"Processed {index} tickets. Pausing for rate limit...")
            logging.info(f"Pausing for rate limit after {index} requests...")
            time.sleep(10)

    # Print final summary
    print("\n" + "=" * 60)
    print("BATCH UPDATE SUMMARY")
    print("=" * 60)
    print(f"Total tickets processed: {len(ticket_ids)}")
    print(f"Successfully updated: {success_count}")
    print(f"Already had '{tag_to_add}' tag: {skip_count}")
    print(f"Errors/failures: {error_count}")
    print("=" * 60)

    logging.info(f"Batch update completed. Success: {success_count}, Skipped: {skip_count}, Errors: {error_count}")

def process_tickets_gui(ticket_ids, tag_to_add):
    """
    Process tickets in GUI mode with progress updates.
    """
    success_count = 0
    skip_count = 0
    error_count = 0

    # Update GUI elements
    def update_progress(current, total, message=""):
        progress_var.set(f"Processing: {current}/{total} tickets ({int((current/total)*100)}%)")
        if message:
            log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress(0, len(ticket_ids), "Starting batch ticket tag addition...")
    update_progress(0, len(ticket_ids), f"Tag to add: {tag_to_add}")

    # Process tickets in batches with rate limiting
    for index, ticket_id in enumerate(ticket_ids, start=1):
        update_progress(index, len(ticket_ids), f"Processing ticket {index}/{len(ticket_ids)}: ID {ticket_id}")

        # Update the ticket
        if update_ticket_tags(ticket_id, tag_to_add):
            success_count += 1
        elif "already has" in str(logging.getLogger().handlers[0].stream.getvalue()):
            skip_count += 1
        else:
            error_count += 1

        # Handle rate limits: pause every 50 requests
        if index % 50 == 0:
            update_progress(index, len(ticket_ids), f"Processed {index} tickets. Pausing for rate limit...")
            logging.info(f"Pausing for rate limit after {index} requests...")
            time.sleep(10)

    # Print final summary
    summary_msg = "\n" + "=" * 60 + "\n"
    summary_msg += "BATCH UPDATE SUMMARY\n"
    summary_msg += "=" * 60 + "\n"
    summary_msg += f"Total tickets processed: {len(ticket_ids)}\n"
    summary_msg += f"Successfully updated: {success_count}\n"
    summary_msg += f"Already had '{tag_to_add}' tag: {skip_count}\n"
    summary_msg += f"Errors/failures: {error_count}\n"
    summary_msg += "=" * 60

    update_progress(len(ticket_ids), len(ticket_ids), summary_msg)
    logging.info(f"Batch update completed. Success: {success_count}, Skipped: {skip_count}, Errors: {error_count}")

    # Show completion message
    messagebox.showinfo("Tag Addition Complete",
                       f"Processed {len(ticket_ids)} tickets.\n"
                       f"Successfully updated: {success_count}\n"
                       f"Already had tag: {skip_count}\n"
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

def create_gui():
    """Create the graphical user interface."""
    global tag_var, ticket_ids_text, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Ticket Tag Manager")
    app.geometry("600x500")

    # Tag selection
    tk.Label(app, text="Tag Management", font=("Arial", 12, "bold")).pack(pady=10)

    tag_frame = tk.Frame(app)
    tag_frame.pack(pady=5, padx=20, fill="x")

    tk.Label(tag_frame, text="Tag to Add:").grid(row=0, column=0, sticky="w")
    tag_var = tk.StringVar(value="qa")
    tag_combo = ttk.Combobox(tag_frame, textvariable=tag_var, values=COMMON_TAGS, width=27)
    tag_combo.grid(row=0, column=1, padx=10)
    tag_combo.bind('<KeyRelease>', lambda e: update_tag_suggestions(e, tag_var, tag_combo))

    # Ticket IDs input
    tk.Label(app, text="Ticket IDs (one per line or comma-separated):").pack(pady=5)

    ticket_ids_text = tk.Text(app, height=8, width=60)
    ticket_ids_text.pack(pady=5, padx=20)

    # Load default ticket IDs
    ticket_ids_text.insert('1.0', '\n'.join(map(str, DEFAULT_TICKET_IDS[:10])))  # Show first 10 as example
    ticket_ids_text.insert(tk.END, '\n... (add more ticket IDs above)')

    # Buttons
    button_frame = tk.Frame(app)
    button_frame.pack(pady=10)

    def start_processing():
        tag_to_add = tag_var.get().strip()
        ticket_input = ticket_ids_text.get('1.0', tk.END).strip()

        if not tag_to_add:
            messagebox.showerror("Error", "Please specify a tag to add.")
            return

        ticket_ids = parse_ticket_ids(ticket_input)

        if not ticket_ids:
            messagebox.showerror("Error", "Please provide valid ticket IDs (numbers only).")
            return

        # Run in separate thread to keep GUI responsive
        threading.Thread(target=process_tickets_gui, args=(ticket_ids, tag_to_add), daemon=True).start()

    tk.Button(button_frame, text="Start Tag Addition",
              command=start_processing,
              bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT, padx=5)

    def clear_form():
        tag_var.set("qa")
        ticket_ids_text.delete('1.0', tk.END)

    tk.Button(button_frame, text="Clear Form",
              command=clear_form, padx=20).pack(side=tk.LEFT, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    tk.Label(app, textvariable=progress_var).pack(pady=5)

    tk.Label(app, text="Operation Log:").pack(pady=5)
    log_area = scrolledtext.ScrolledText(app, height=10, width=70, state=tk.DISABLED)
    log_area.pack(pady=5, padx=20)

    # Instructions
    instructions = tk.Label(app,
                           text="Instructions:\n"
                                "1. Select or type the tag you want to add\n"
                                "2. Enter ticket IDs (one per line or comma-separated)\n"
                                "3. Click 'Start Tag Addition' to begin",
                           justify="left", fg="gray")
    instructions.pack(pady=10, padx=20)

    return app

def update_tag_suggestions(event, tag_var, tag_combo):
    """Update tag suggestions as user types."""
    typed = tag_var.get().lower()
    if len(typed) >= 2:
        suggestions = [tag for tag in COMMON_TAGS if typed in tag.lower()]
        if suggestions:
            tag_combo['values'] = suggestions

# Run GUI if no command line arguments, otherwise run command line mode
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        # GUI mode
        app = create_gui()
        app.mainloop()
    else:
        # Command line mode - use default ticket IDs and 'qa' tag
        main()

