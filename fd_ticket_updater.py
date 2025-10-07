
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font as tkfont
from tkinter import filedialog
import threading
import logging
import requests
from requests.auth import HTTPBasicAuth
import time
import queue
import os
# Set up logging to queue
log_queue = queue.Queue()

# Global flag to control the update process
stop_update_flag = threading.Event()


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

# The name of the log file
log_filename = 'freshdesk_update.log'

# Full path to where the log file will be stored - same directory as the script
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_filename)

# Configure logging with the new log file path
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        QueueHandler(log_queue)
    ]
)

# Replace 'your_api_key' with your actual Freshdesk API key
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompanysandbox'
tickets_endpoint = f'https://{domain}.freshdesk.com/api/v2/tickets'
companies_endpoint = f'https://{domain}.freshdesk.com/api/v2/companies'

# Authentication
auth = HTTPBasicAuth(api_key, 'X')

# Headers
headers = {
    'Content-Type': 'application/json',
}

# Function to handle rate limiting with more precision
def respect_rate_limit(response=None):
    if response is not None:
        remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remaining < 10:  # Arbitrary number, can be adjusted
            wait_time = (60 // remaining) if remaining else 60  # Wait time based on remaining calls
            logging.info(f"Approaching rate limit, waiting for {wait_time} seconds")
            time.sleep(wait_time)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logging.warning(f"Rate limit hit, waiting for {retry_after} seconds")
            time.sleep(retry_after)
    else:
        # No response object, so we use a default sleep time
        default_sleep_time = 10
        logging.info(f"No response object provided, sleeping for default time of {default_sleep_time} seconds")
        time.sleep(default_sleep_time)


# Function to fetch all companies with pagination
def fetch_companies():
    company_mapping = {}
    page = 1
    while True:
        response = requests.get(f"{companies_endpoint}?per_page=100&page={page}", headers=headers, auth=auth)
        if response.status_code == 429:
            respect_rate_limit(response)
            continue  # Try to fetch the same page again
        elif response.status_code != 200:
            logging.error(f"Failed to fetch companies. Status code: {response.status_code} Response: {response.content}")
            break

        companies = response.json()
        if not companies:
            break

        for company in companies:
            company_mapping[company['id']] = company['name']

        page += 1
        # Only call respect_rate_limit if there is a response object
        if response:
            respect_rate_limit(response)

    return company_mapping


# Function to update a single ticket's custom field
def update_ticket_custom_field(ticket_id, company_name, ticket_data):
    DEFAULT_SOURCE = 3
    update_data = {
        'custom_fields': {'cf_district241195': company_name},
        'source': ticket_data.get('source') or DEFAULT_SOURCE
    }

    response = requests.put(f'{tickets_endpoint}/{ticket_id}', json=update_data, headers=headers, auth=auth)
    respect_rate_limit(response)  # Pass the response object to respect the rate limit

    if response.status_code != 200:
        logging.error(f"Failed to update ticket {ticket_id}. Status code: {response.status_code} Response: {response.content}")
        return False
    logging.info(f"Ticket {ticket_id} updated successfully.")
    return True


# Function to run the update process
def run_update(start_id, end_id, output_box, update_progress):
    company_mapping = fetch_companies()  # Fetch company data
    if not company_mapping:
        logging.error("Company mapping could not be created, script will not proceed.")
        return

    updated_tickets_count = 0
    total_tickets_to_update = end_id - start_id + 1  # Calculate the total number of tickets to update

    for ticket_id in range(start_id, end_id + 1):
        if stop_update_flag.is_set():
            logging.info("Update process was stopped by user.")
            break  # Exiting the loop if stop flag is set

        # Calculate and log the progress
        progress = ((ticket_id - start_id) / total_tickets_to_update) * 100
        update_progress(ticket_id, progress)  # Update progress in the GUI

        response = requests.get(f"{tickets_endpoint}/{ticket_id}", headers=headers, auth=auth)
        respect_rate_limit(response)  # Pass the response object to respect the rate limit

        if response.status_code != 200:
            logging.error(f"Failed to fetch ticket {ticket_id}. Status code: {response.status_code} Response: {response.content}")
            continue

        ticket_data = response.json()
        company_id = ticket_data.get('company_id')
        if company_id and company_id in company_mapping:
            if update_ticket_custom_field(ticket_id, company_mapping[company_id], ticket_data):
                updated_tickets_count += 1

    success_rate = (updated_tickets_count / total_tickets_to_update) * 100  # Calculate the success rate
    logging.info(f"Updated a total of {updated_tickets_count} out of {total_tickets_to_update} tickets ({success_rate:.2f}% success rate).")
    logging.info("The update process has been completed.")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Freshdesk Ticket Updater')
        self.geometry('600x600')
        self.configure(bg='gray')  # Set the background to black

        # All the widgets will have the following color configuration
        widget_background = 'black'  # Gray background for text fields
        widget_foreground = "#32CD32"  # Green font color
        button_font = tkfont.Font(family='Helvetica', size=10, weight='bold')  # Bold font for buttons

        # Title Label with larger, bold font
        title_font = tkfont.Font(family='MS Gothic', size=16, weight='bold')  # Define the font
        title_label = tk.Label(self, text="FD TICKET UPDATER", font=title_font, bg='gray', fg='black')
        title_label.pack(side=tk.TOP, pady=(10, 20))  # Add padding to create space around the title

        # Instructions Label
        instructions_text = ("This app is designed to update the District Dropdown (cf_district241195, id=1067000953326) "
                             "field within a Freshdesk ticket by iterating through the specified Ticket ID range, "
                             "matching the dropdown value selection to the Company (id=1067000671494) associated to each ticket.\n\nThe script manages rate limiting by using the X-RateLimit-Remaining header to anticipate when it is approaching the limit and proactively slows down requests. If the limit is reached and a 429 status code is received, it utilizes the Retry-After header to pause requests for the recommended amount of time before retrying. This dual approach helps maintain a steady request flow without overloading the API.")
        self.instructions_label = tk.Label(self, text=instructions_text, wraplength=580, justify="left", bg='black', fg=widget_foreground)
        self.instructions_label.pack(pady=(0, 10))


               # Start ID Entry
        self.start_label = tk.Label(self, text="Starting Ticket ID:", bg='gray', fg='black')
        self.start_label.pack()
        self.start_entry = tk.Entry(self, bg=widget_background, fg=widget_foreground)
        self.start_entry.pack()

        # End ID Entry
        self.end_label = tk.Label(self, text="Ending Ticket ID:", bg='gray', fg='black')
        self.end_label.pack()
        self.end_entry = tk.Entry(self, bg=widget_background, fg=widget_foreground)
        self.end_entry.pack(pady=(0, 10))  # Add some vertical padding below the entry

        # Output Box
        self.output_box = ScrolledText(self, state='disabled', height=10, bg=widget_background, fg=widget_foreground)
        self.output_box.pack(pady=(0, 10))

        # Update Button
        self.update_button = tk.Button(self, text="Update District Dropdown Selections", command=self.start_update_thread, bg=widget_background, fg=widget_foreground, font=button_font)
        self.update_button.pack(pady=(0, 10))

        # Stop Button
        self.stop_button = tk.Button(self, text="Stop Update", command=self.stop_update, bg=widget_background, fg=widget_foreground, font=button_font)
        self.stop_button.pack(pady=(0, 10))

        # Export Button - Moved under the Stop Update button
        self.export_button = tk.Button(self, text="Export Log", command=self.export_log, bg=widget_background, fg=widget_foreground, font=button_font)
        self.export_button.pack(pady=(0, 10))

        # Start logging thread
        self.after(100, self.poll_log_queue)

    def poll_log_queue(self):
        while not log_queue.empty():
            try:
                record = log_queue.get(block=False)
                self.output_box.config(state='normal')
                self.output_box.insert(tk.END, record + '\n')
                self.output_box.yview(tk.END)
                self.output_box.config(state='disabled')
            except queue.Empty:
                pass
        self.after(100, self.poll_log_queue)

    def start_update_thread(self):
        # Clear the stop flag before starting the update thread
        stop_update_flag.clear()

        # Get the start and end IDs from the entry fields
        start_id = int(self.start_entry.get())
        end_id = int(self.end_entry.get())
        
        # Update the output box with a message that the process has started
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, f"Go Birds!\nUpdate process started for tickets {start_id} to {end_id}\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')
        
        # Pass the update_progress method to the update thread
        t = threading.Thread(target=run_update, args=(start_id, end_id, self.output_box, self.update_progress))
        t.daemon = True
        t.start()

    def update_progress(self, ticket_id, progress):
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, f"Updating ticket {ticket_id}... ({progress:.2f}% completed)\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')

    def stop_update(self):
        # Set the stop flag to true to signal the update thread to stop
        stop_update_flag.set()
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, "Stopping the update process...\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')

    def export_log(self):
        """Exports the content of the output box to a text file."""
        content = self.output_box.get("1.0", tk.END)  # Get content from the output box
        # Ask the user for a location and filename to save the log
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if filepath:  # If a filepath was selected
            try:
                with open(filepath, 'w') as file:
                    file.write(content.strip())  # Write content to the file
                    messagebox.showinfo("Export Successful", f"Log exported successfully to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export log. Error: {e}")


if __name__ == "__main__":
    print("Creating GUI...")
    app = Application()
    print("GUI created, starting main loop...")
    app.mainloop()
    print("Script finished")

