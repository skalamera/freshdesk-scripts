import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import pandas as pd
import json
import time
import threading

# Constants
API_KEY_SANDBOX = '5TMgbcZdRFY70hSpEdj'
SANDBOX_DOMAIN = 'benchmarkeducationcompanysandbox.freshdesk.com'
PROD_DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
AUTH_SANDBOX = (API_KEY_SANDBOX, 'X')
AUTH_PROD = (API_KEY_SANDBOX, 'X')
HEADERS = {'Content-Type': 'application/json'}
AUTOMATION_TYPES = {
    1: 'Ticket Creation',
    3: 'Time Triggers',
    4: 'Ticket Updates'
}

# Helper function to handle rate limiting
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)
        return True
    return False

def fetch_all_agents(domain, auth):
    agents = []
    page = 1
    while True:
        url = f'https://{domain}/api/v2/agents'
        params = {'page': page, 'per_page': 100}
        response = requests.get(url, auth=auth, headers=HEADERS, params=params)

        # Handle rate limit and retry
        if handle_rate_limit(response):
            continue

        if response.status_code == 200:
            try:
                data = response.json()
                if not data:
                    break
                agents.extend(data)
                page += 1
            except json.JSONDecodeError:
                print(f"Error decoding JSON response on page {page}")
                break
        else:
            print(f"Failed to fetch agents data: {response.status_code} - {response.text}")
            break
    return agents

def fetch_automation_rules(domain, auth, automation_type_id):
    rules = []
    page = 1
    while True:
        url = f'https://{domain}/api/v2/automations/{automation_type_id}/rules'
        params = {'page': page, 'per_page': 100}
        response = requests.get(url, auth=auth, headers=HEADERS, params=params)

        # Handle rate limit and retry
        if handle_rate_limit(response):
            continue

        if response.status_code == 200:
            try:
                data = response.json()
                if not data:
                    break
                rules.extend(data)
                page += 1
            except json.JSONDecodeError:
                print(f"Error decoding JSON response on page {page}")
                break
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            break
    return rules

def fetch_valid_groups(domain, auth):
    url = f'https://{domain}/api/v2/groups'
    response = requests.get(url, auth=auth, headers=HEADERS)

    # Handle rate limit and retry
    if handle_rate_limit(response):
        response = requests.get(url, auth=auth, headers=HEADERS)

    if response.status_code == 200:
        try:
            groups = response.json()
            return {group['name']: group['id'] for group in groups}
        except json.JSONDecodeError:
            print(f"Error decoding JSON response")
            return {}
    else:
        raise Exception(f"Failed to fetch groups: {response.status_code} {response.text}")

def export_to_excel(export_path, domain, auth):
    all_rules = []
    for type_id, type_name in AUTOMATION_TYPES.items():
        rules = fetch_automation_rules(domain, auth, type_id)
        for rule in rules:
            rule_summary = {
                'Automation Type': type_name,
                'Name': rule.get('name'),
                'Position': rule.get('position'),
                'Performer': rule.get('performer'),
                'Active': rule.get('active'),
                'Events': json.dumps(rule.get('events', [])),
                'Conditions': json.dumps(rule.get('conditions', [])),
                'Actions': json.dumps(rule.get('actions', [])),
                'Last Updated': rule.get('updated_at')
            }
            all_rules.append(rule_summary)

    df = pd.DataFrame(all_rules)
    if export_path.endswith('.xlsx'):
        df.to_excel(export_path, index=False)
    elif export_path.endswith('.csv'):
        df.to_csv(export_path, index=False)
    return f"Automation rules have been saved to '{export_path}'."

def save_file():
    def save_task():
        export_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if export_path:
            try:
                domain = SANDBOX_DOMAIN if export_env.get() == "Sandbox" else PROD_DOMAIN
                auth = AUTH_SANDBOX if export_env.get() == "Sandbox" else AUTH_PROD
                message = export_to_excel(export_path, domain, auth)
                messagebox.showinfo("Success", message)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    threading.Thread(target=save_task).start()

# GUI setup
root = tk.Tk()
root.title("Freshdesk Automation Export")
export_env = tk.StringVar(value="Production")  # Set default value to Production

# Dropdown menu to select environment
tk.Label(root, text="Select environment:").pack()
tk.OptionMenu(root, export_env, "Sandbox", "Production").pack()

# Save button
tk.Button(root, text="Save File", command=save_file).pack()

root.mainloop()

