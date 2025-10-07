import requests
import time
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
auth = (API_KEY, 'X')
headers = {'Content-Type': 'application/json'}
RATE_LIMIT = 700  # Enterprise plan rate limit
RATE_LIMIT_WINDOW = 60  # in seconds

# Initialize rate limit variables
rate_limit_remaining = RATE_LIMIT
rate_limit_reset_time = time.time() + RATE_LIMIT_WINDOW

# Helper function to make API requests with rate limiting
def make_request(method, endpoint, params=None, data=None):
    global rate_limit_remaining, rate_limit_reset_time
    while rate_limit_remaining == 0:
        sleep_time = max(rate_limit_reset_time - time.time(), 0)
        time.sleep(sleep_time)
        rate_limit_remaining = RATE_LIMIT
    
    url = f'https://{DOMAIN}/api/v2{endpoint}'
    response = requests.request(method, url, headers=headers, params=params, json=data, auth=auth)
    
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', RATE_LIMIT))
    rate_limit_reset_time = time.time() + RATE_LIMIT_WINDOW
    
    response.raise_for_status()
    return response.json() if response.content else None

# Fetch contacts of a company
def get_contacts_by_company(company_id):
    contacts = []
    page = 1
    while True:
        response = make_request('GET', f'/contacts?company_id={company_id}&page={page}')
        if not response:
            break
        contacts.extend(response)
        page += 1
    return contacts

# Update company domains
def update_company_domains(company_id, domains):
    make_request('PUT', f'/companies/{company_id}', data={'domains': domains})

# Move contacts to a new company
def move_contacts_to_company(contact_ids, new_company_id):
    for contact_id in contact_ids:
        make_request('PUT', f'/contacts/{contact_id}', data={'company_id': new_company_id})

# Delete company
def delete_company(company_id):
    make_request('DELETE', f'/companies/{company_id}')

# Main function to move contacts and domain
def move_contacts_and_domain(source_company_id, incorrect_domain, correct_company_id, delete_company_flag, log):
    log.insert(tk.END, f'Starting process to move contacts and domain from {incorrect_domain} in company {source_company_id}...\n')

    # Get contacts of source company
    source_company_contacts = get_contacts_by_company(source_company_id)

    # Remove domain from source company
    source_company = make_request('GET', f'/companies/{source_company_id}')
    source_company_domains = source_company.get('domains', [])
    if incorrect_domain in source_company_domains:
        source_company_domains.remove(incorrect_domain)
        update_company_domains(source_company_id, source_company_domains)
        log.insert(tk.END, f'Removed domain {incorrect_domain} from source company.\n')

    # Get correct company details
    correct_company = make_request('GET', f'/companies/{correct_company_id}')
    correct_company_domains = correct_company.get('domains', [])

    # Debug: Print current domains of the correct company
    log.insert(tk.END, f'Current domains of correct company ({correct_company_id}): {correct_company_domains}\n')

    # Update domains
    try:
        log.insert(tk.END, f'Updating domains...\n')
        if incorrect_domain not in correct_company_domains:
            correct_company_domains.append(incorrect_domain)
        update_company_domains(correct_company_id, correct_company_domains)
        log.insert(tk.END, f'Added domain {incorrect_domain} to correct company.\n')
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            log.insert(tk.END, f'Error: Conflict when updating domains. Domain {incorrect_domain} might already exist in another company.\n')
            return
        else:
            raise

    # Filter and move contacts
    log.insert(tk.END, f'Moving contacts...\n')
    contact_ids_to_move = [contact['id'] for contact in source_company_contacts if incorrect_domain in contact['email']]
    move_contacts_to_company(contact_ids_to_move, correct_company_id)
    log.insert(tk.END, f'Moved contacts from source company to correct company.\n')

    # Delete source company if flag is set
    if delete_company_flag:
        log.insert(tk.END, f'Deleting source company after moving domain and associated contacts...\n')
        delete_company(source_company_id)
        log.insert(tk.END, f'Deleted source company.\n')

    log.insert(tk.END, f'Process completed successfully.\n')

# Function to move only contacts
def move_only_contacts(source_company_id, target_company_id, delete_source_flag, move_all_flag, domains_to_move, log):
    log.insert(tk.END, f'Starting process to move contacts from company {source_company_id} to {target_company_id}...\n')

    # Get contacts of source company
    source_company_contacts = get_contacts_by_company(company_id=source_company_id)

    # Filter contacts by domain if move_all_flag is False
    if not move_all_flag:
        domain_list = [domain.strip() for domain in domains_to_move.split(',')]
        contact_ids_to_move = [contact['id'] for contact in source_company_contacts if any(domain in contact['email'] for domain in domain_list)]
    else:
        contact_ids_to_move = [contact['id'] for contact in source_company_contacts]

    # Move contacts
    log.insert(tk.END, f'Moving contacts...\n')
    move_contacts_to_company(contact_ids_to_move, target_company_id)
    log.insert(tk.END, f'Moved contacts from source company to target company.\n')

    # Delete source company if flag is set
    if delete_source_flag:
        log.insert(tk.END, f'Deleting source company after moving contacts...\n')
        delete_company(source_company_id)
        log.insert(tk.END, f'Deleted source company.\n')

    log.insert(tk.END, f'Process completed successfully.\n')

# Function to start the domain move process from GUI
def start_domain_process():
    source_company_id = source_company_id_var.get()
    incorrect_domain = domain_var.get()
    correct_company_id = correct_company_id_var.get()
    delete_company_flag = delete_company_var.get()

    # Debug logging
    print(f"Source Company ID: {source_company_id}")
    print(f"Domain to Move: {incorrect_domain}")
    print(f"Correct Company ID: {correct_company_id}")
    
    if not source_company_id or not incorrect_domain or not correct_company_id:
        messagebox.showerror("Error", "Please provide source company ID, domain, and correct company ID.")
        return

    try:
        source_company_id = int(source_company_id)
        correct_company_id = int(correct_company_id)
        move_contacts_and_domain(source_company_id, incorrect_domain, correct_company_id, delete_company_flag, log_text)
    except ValueError:
        messagebox.showerror("Error", "Company IDs must be numbers.")

# Function to start the contact move process from GUI
def start_contact_process():
    source_company_id = source_company_id_var2.get()
    target_company_id = target_company_id_var.get()
    delete_source_flag = delete_source_var.get()
    move_all_flag = move_all_var.get()
    domains_to_move = domains_var.get()

    # Debug logging
    print(f"Source Company ID: {source_company_id}")
    print(f"Target Company ID: {target_company_id}")
    print(f"Move All Contacts: {move_all_flag}")
    print(f"Domains to Move: {domains_to_move}")
    
    if not source_company_id or not target_company_id:
        messagebox.showerror("Error", "Please provide both source and target company IDs.")
        return

    try:
        source_company_id = int(source_company_id)
        target_company_id = int(target_company_id)
        move_only_contacts(source_company_id, target_company_id, delete_source_flag, move_all_flag, domains_to_move, log_text)
    except ValueError:
        messagebox.showerror("Error", "Company IDs must be numbers.")

# Function to export logs to a file
def export_logs():
    log_content = log_text.get(1.0, tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(log_content)
        messagebox.showinfo("Success", "Logs exported successfully.")

# Function to enable or disable the domain entry based on the checkbox
def toggle_domain_entry():
    if move_all_var.get():
        domains_entry.configure(state=tk.DISABLED)
    else:
        domains_entry.configure(state=tk.NORMAL)

# GUI setup
root = tk.Tk()
root.title("Freshdesk Contact and Domain Manager")

# Initialize StringVar variables
source_company_id_var = tk.StringVar()
domain_var = tk.StringVar()
correct_company_id_var = tk.StringVar()
source_company_id_var2 = tk.StringVar()
target_company_id_var = tk.StringVar()
domains_var = tk.StringVar()

# Section 1: Move Domain and Associated Contacts
tk.Label(root, text="Move Domain and Associated Contacts").grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

tk.Label(root, text="Source Company ID:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
source_company_id_entry = tk.Entry(root, textvariable=source_company_id_var, width=30)
source_company_id_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Domain to Move:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
domain_entry = tk.Entry(root, textvariable=domain_var, width=30)
domain_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Correct Company ID:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
correct_company_id_entry = tk.Entry(root, textvariable=correct_company_id_var, width=30)
correct_company_id_entry.grid(row=3, column=1, padx=10, pady=5)

delete_company_var = tk.BooleanVar()
delete_company_check = tk.Checkbutton(root, text="Delete Company After Moving Domain and Associated Contacts", variable=delete_company_var)
delete_company_check.grid(row=4, column=0, columnspan=2, pady=5)

start_domain_button = tk.Button(root, text="Start Process", command=start_domain_process)
start_domain_button.grid(row=5, column=0, columnspan=2, pady=10)

# Section 2: Move Contacts Only
tk.Label(root, text="Move Contacts Only").grid(row=6, column=0, columnspan=2, pady=10, sticky="w")

tk.Label(root, text="Source Company ID:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
source_company_id_entry2 = tk.Entry(root, textvariable=source_company_id_var2, width=30)
source_company_id_entry2.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Target Company ID:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
target_company_id_entry = tk.Entry(root, textvariable=target_company_id_var, width=30)
target_company_id_entry.grid(row=8, column=1, padx=10, pady=5)

move_all_var = tk.BooleanVar()
move_all_check = tk.Checkbutton(root, text="Move All Contacts", variable=move_all_var, command=toggle_domain_entry)
move_all_check.grid(row=9, column=0, columnspan=2, pady=5)

tk.Label(root, text="Domains to Move (comma-separated):").grid(row=10, column=0, padx=10, pady=5, sticky="e")
domains_entry = tk.Entry(root, textvariable=domains_var, width=30)
domains_entry.grid(row=10, column=1, padx=10, pady=5)

delete_source_var = tk.BooleanVar()
delete_source_check = tk.Checkbutton(root, text="Delete Source Company After Moving Contacts", variable=delete_source_var)
delete_source_check.grid(row=11, column=0, columnspan=2, pady=5)

start_contact_button = tk.Button(root, text="Start Process", command=start_contact_process)
start_contact_button.grid(row=12, column=0, columnspan=2, pady=10)

# Log area and export button
log_text = scrolledtext.ScrolledText(root, width=70, height=20)
log_text.grid(row=13, column=0, columnspan=2, padx=10, pady=10)

export_button = tk.Button(root, text="Export Logs", command=export_logs)
export_button.grid(row=14, column=0, columnspan=2, pady=10)

root.mainloop()

