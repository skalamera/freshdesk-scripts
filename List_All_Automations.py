"""
Freshdesk Automation Rules Export GUI

DESCRIPTION:
This script provides a graphical user interface for exporting Freshdesk automation
rules from either sandbox or production environments. It fetches automation rules
by type (Ticket Creation, Time Triggers, Ticket Updates) and exports them to
Excel or CSV format for analysis and documentation purposes.

REQUIREMENTS:
- Python 3.x
- tkinter (usually included with Python)
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- Valid Freshdesk API key with automation rules read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY_SANDBOX with your actual Freshdesk API key
2. Replace SANDBOX_DOMAIN and PROD_DOMAIN with your actual domains
3. Ensure your API key has permissions for automation rules access
4. Run the script: python List_All_Automations.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Automation Rules API: https://developers.freshdesk.com/api/#automation_rules
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY_SANDBOX: Your Freshdesk API key
- SANDBOX_DOMAIN: Sandbox environment domain
- PROD_DOMAIN: Production environment domain
- AUTOMATION_TYPES: Mapping of automation type IDs to names

OUTPUT:
- Excel/CSV file with automation rules data
- GUI interface for environment selection and file export
- Console output showing progress and results

AUTOMATION TYPES EXPORTED:
- Type 1: Ticket Creation automations
- Type 3: Time Trigger automations
- Type 4: Ticket Update automations

EXCEL/CSV OUTPUT INCLUDES:
- Automation Type (Creation, Time Triggers, Updates)
- Rule Name and Position
- Performer and Active status
- Events, Conditions, and Actions (JSON format)
- Last Updated timestamp

ERROR HANDLING:
- Handles HTTP 404 (rules not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual rule types fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining rule types after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has automation rules read permissions
- Check Freshdesk domain names are correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that automation rules exist in your Freshdesk account

PERFORMANCE CONSIDERATIONS:
- Processes automation rules in pages (100 per page by default)
- Handles pagination automatically
- Large numbers of rules may take significant time to process
- GUI remains responsive during background processing

USAGE SCENARIOS:
- Document automation rules for compliance auditing
- Analyze automation configurations across environments
- Backup automation rules before making changes
- Compare automation setups between sandbox and production
"""

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

