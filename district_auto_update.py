import os
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font as tkfont
import threading
import logging
import requests
from requests.auth import HTTPBasicAuth
import time
import queue
import logging
import threading
import time
import tkinter as tk
from queue import Queue
from requests.auth import HTTPBasicAuth
from tkinter.scrolledtext import ScrolledText
import requests

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

log_filename = 'freshdesk_update.log'
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        QueueHandler(log_queue)
    ]
)

api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany'
tickets_endpoint = f'https://{domain}.freshdesk.com/api/v2/tickets'
companies_endpoint = f'https://{domain}.freshdesk.com/api/v2/companies'
import tkinter.font as tkfont
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
log_queue = Queue()
stop_update_flag = threading.Event()

api_key = "5TMgbcZdRFY70hSpEdj"
companies_endpoint = "https://your-freshdesk-domain.com/api/v2/companies"
tickets_endpoint = "https://your-freshdesk-domain.com/api/v2/tickets"

auth = HTTPBasicAuth(api_key, 'X')
headers = {'Content-Type': 'application/json'}

def respect_rate_limit(response=None):
    if response is not None:
        remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remaining < 10:
            wait_time = (60 // remaining) if remaining else 60
            logging.info(f"Approaching rate limit, waiting for {wait_time} seconds")
            time.sleep(wait_time)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logging.warning(f"Rate limit hit, waiting for {retry_after} seconds")
            time.sleep(retry_after)
    else:
        default_sleep_time = 10
        logging.info(f"No response object provided, sleeping for default time of {default_sleep_time} seconds")
        time.sleep(default_sleep_time)

def fetch_companies():
    company_mapping = {}
    page = 1
    while True:
        response = requests.get(f"{companies_endpoint}?per_page=100&page={page}", headers=headers, auth=auth)
        if response.status_code == 429:
            respect_rate_limit(response)
            continue
        elif response.status_code != 200:
            logging.error(f"Failed to fetch companies. Status code: {response.status_code} Response: {response.content}")
            break

        companies = response.json()
        if not companies:
            break

        for company in companies:
            company_mapping[company['id']] = company['name']

        page += 1
        if response:
            respect_rate_limit(response)

    return company_mapping

def update_ticket_custom_field(ticket_id, company_name, ticket_data):
    DEFAULT_SOURCE = 3
    update_data = {
        'custom_fields': {'cf_district241195': company_name},
        'source': ticket_data.get('source') or DEFAULT_SOURCE
    }

    response = requests.put(f'{tickets_endpoint}/{ticket_id}', json=update_data, headers=headers, auth=auth)
    respect_rate_limit(response)

    if response.status_code != 200:
        logging.error(f"Failed to update ticket {ticket_id}. Status code: {response.status_code} Response: {response.content}")
        return False
    logging.info(f"Ticket {ticket_id} updated successfully.")
    return True

def run_update(start_id, end_id, ticket_id_list, output_box, update_progress):
    company_mapping = fetch_companies()
    if not company_mapping:
        logging.error("Company mapping could not be created, script will not proceed.")
        return

    updated_tickets_count = 0
    processed_tickets_count = 0  # Initialize counter for processed tickets
    total_tickets_to_update = (end_id - start_id + 1) + len(ticket_id_list)

    if start_id > 0 and end_id >= start_id:
        for ticket_id in range(start_id, end_id + 1):
            if stop_update_flag.is_set():
                logging.info("Update process was stopped by user.")
                break

            processed_tickets_count += 1  # Increment the processed ticket count
            progress = (processed_tickets_count / total_tickets_to_update) * 100  # Calculate progress based on processed tickets
            update_progress(ticket_id, progress)  # Update progress in the GUI

            response = requests.get(f"{tickets_endpoint}/{ticket_id}", headers=headers, auth=auth)
            respect_rate_limit(response)

            if response.status_code != 200:
                logging.error(f"Failed to fetch ticket {ticket_id}. Status code: {response.status_code} Response: {response.content}")
                continue

            ticket_data = response.json()
            company_id = ticket_data.get('company_id')
            if company_id and company_id in company_mapping:
                if update_ticket_custom_field(ticket_id, company_mapping[company_id], ticket_data):
                    updated_tickets_count += 1

    for ticket_id in ticket_id_list:
        if stop_update_flag.is_set():
            break

        processed_tickets_count += 1  # Increment the processed ticket count for each ticket in the list
        progress = (processed_tickets_count / total_tickets_to_update) * 100  # Recalculate progress
        update_progress(ticket_id, progress)  # Update progress in the GUI

        response = requests.get(f"{tickets_endpoint}/{ticket_id}", headers=headers, auth=auth)
        respect_rate_limit(response)

        if response.status_code != 200:
            logging.error(f"Failed to fetch ticket {ticket_id}. Status code: {response.status_code} Response: {response.content}")
            continue

        ticket_data = response.json()
        company_id = ticket_data.get('company_id')
        if company_id and company_id in company_mapping:
            if update_ticket_custom_field(ticket_id, company_mapping[company_id], ticket_data):
                updated_tickets_count += 1

    success_rate = (updated_tickets_count / total_tickets_to_update) * 100
    logging.info(f"Updated a total of {updated_tickets_count} out of {total_tickets_to_update} tickets ({success_rate:.2f}% success rate).")
    logging.info("The update process has been completed.")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Freshdesk Ticket Updater - Delimited List')
        self.geometry('1200x900')
        self.configure(bg='gray')

        widget_background = 'gray'
        widget_foreground = "gray"
        button_font = tkfont.Font(family='Helvetica', size=10, weight='bold')

        title_font = tkfont.Font(family='MS Gothic', size=16, weight='bold')
        title_label = tk.Label(self, text="Freshdesk Ticket Updater - Delimited List", font=title_font, bg='gray', fg='black')
        title_label.pack(side=tk.TOP, pady=(10, 20))

        instructions_text = ("This app is designed to update the District Dropdown (cf_district241195, id=1067000953326) "
                             "field within a Freshdesk ticket by iterating through the specified Ticket ID range, "
                             "matching the dropdown value selection to the Company (id=1067000671494) associated to each ticket.\n\nThe script manages rate limiting by using the X-RateLimit-Remaining header to anticipate when it is approaching the limit and proactively slows down requests. If the limit is reached and a 429 status code is received, it utilizes the Retry-After header to pause requests for the recommended amount of time before retrying. This dual approach helps maintain a steady request flow without overloading the API.")
        self.instructions_label = tk.Label(self, text=instructions_text, wraplength=580, justify="left", bg='black', fg='green')
        self.instructions_label.pack(pady=(0, 10))

        self.start_label = tk.Label(self, text="", bg='gray', fg='black')
        self.start_label.pack()
        self.start_entry = tk.Entry(self, bg=widget_background, fg=widget_foreground)
        self.start_entry.pack()

        self.end_label = tk.Label(self, text="", bg='gray', fg='black')
        self.end_label.pack()
        self.end_entry = tk.Entry(self, bg=widget_background, fg=widget_foreground)
        self.end_entry.pack(pady=(0, 10))

        self.ticket_id_list_label = tk.Label(self, text="Comma-separated ticket ID List (Example: 12345, 67890, 01928):", bg='gray', fg='black')
        self.ticket_id_list_label.pack()
        self.ticket_id_list_entry = tk.Text(self, height=5, width=75, bg='black', fg='green')
        self.ticket_id_list_entry.pack(pady=(0, 10))

        self.output_box = ScrolledText(self, state='disabled', height=30, width=75, bg='black', fg='green')
        self.output_box.pack(pady=(0, 10))

        self.update_button = tk.Button(self, text="Update District Dropdown Selections", command=self.start_update_thread, bg='black', fg='green', font=button_font)
        self.update_button.pack(pady=(0, 10))

        self.stop_button = tk.Button(self, text="Stop Update", command=self.stop_update, bg='black', fg='green', font=button_font)
        self.stop_button.pack(pady=(0, 10))

        self.export_button = tk.Button(self, text="Export Log", command=self.export_log, bg='black', fg='green', font=button_font)
        self.export_button.pack(pady=(0, 10))

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
        ticket_id_list_str = self.ticket_id_list_entry.get("1.0", tk.END).strip()
        ticket_id_list = [int(id.strip()) for id in ticket_id_list_str.split(',') if id.strip().isdigit()]
        stop_update_flag.clear()

        start_id_str = self.start_entry.get()
        end_id_str = self.end_entry.get()
        start_id = int(start_id_str) if start_id_str.isdigit() else 0
        end_id = int(end_id_str) if end_id_str.isdigit() else 0

        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, f"Update process started.\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')

        t = threading.Thread(target=run_update, args=(start_id, end_id, ticket_id_list, self.output_box, self.update_progress))
        t.daemon = True
        t.start()

    def update_progress(self, ticket_id, progress):
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, f"Updating ticket {ticket_id}... ({progress:.2f}% completed)\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')

    def stop_update(self):
        stop_update_flag.set()
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, "Stopping the update process...\n")
        self.output_box.yview(tk.END)
        self.output_box.config(state='disabled')

    def export_log(self):
        content = self.output_box.get("1.0", tk.END)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if filepath:
            try:
                with open(filepath, 'w') as file:
                    file.write(content.strip())
                    messagebox.showinfo("Export Successful", f"Log exported successfully to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export log. Error: {e}")

if __name__ == "__main__":
    print("Creating GUI...")
    app = Application()
    print("GUI created, starting main loop...")
    app.mainloop()
    print("Script finished")

