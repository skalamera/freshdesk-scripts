"""
Freshdesk Automation Rule Creation Script

DESCRIPTION:
This script creates a time-triggered automation rule in Freshdesk that assigns
unassigned tickets to appropriate regional groups based on the company's state
information. The automation runs daily and processes tickets based on their
creation time and status.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with automation rules write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace api_key with your actual Freshdesk API key
2. Replace domain with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update region_to_group mapping with your actual group IDs
4. Update automation conditions and actions as needed
5. Ensure your API key has permissions for automation rules creation
6. Run the script: python fd_automation_import.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Automation Rules API: https://developers.freshdesk.com/api/#automation_rules
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- api_key: Your Freshdesk API key
- domain: Your Freshdesk domain
- automation_type_id: Type of automation (3 = Time-triggered)
- region_to_group: Mapping of regions to group IDs

OUTPUT:
- Creates a time-triggered automation rule
- Console output showing success/failure status
- Detailed response information if creation fails

AUTOMATION RULE DETAILS:
- Type: Time-triggered automation (runs at 8 AM daily)
- Triggers on tickets created within the last day
- Filters for tickets with 'Unassigned' status (ID: 2)
- Assigns tickets to regional groups based on company state
- Updates region custom field for each ticket

REGION MAPPING:
- Maps US states to regional groups (Central Southeast, Central Southwest, Northeast, West)
- Handles international and DoDEA (Department of Defense Education Activity) cases
- Assigns unmapped states to Northeast region as default

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has automation rules write permissions
- Check that group IDs in mapping are correct
- Ensure network connectivity to Freshdesk API
- Verify that automation type ID is valid
- Check that required custom fields exist

USAGE SCENARIOS:
- Automate ticket assignment based on geographic regions
- Implement consistent regional routing for support tickets
- Reduce manual ticket assignment workload
- Ensure proper ticket distribution across regional teams
- Maintain service level agreements by region
"""

import requests
import json
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompany.freshdesk.com'
automation_type_id = 3  # Time-triggered automation type

# Mapping of regions to groups
region_to_group = {
    "Central Southeast": 67000578164,
    "Central Southwest": 67000578162,
    "Northeast": 67000578163,
    "West": 67000578161,
    "International": 67000578163,
    "DoDEA": 67000578163
}

# Create the conditions for the rule
conditions = [
    {
        "resource_type": "ticket",
        "field_name": "status",
        "operator": "in",
        "value": ["2"]  # Status 'Unassigned' has ID 2 in Freshdesk
    },
    {
        "resource_type": "ticket",
        "field_name": "created_at",
        "operator": "greater_than",
        "value": 0  # This ensures it includes tickets from any time within the last day
    }
]

# Create the actions for the rule based on region
actions = []
for region, group_id in region_to_group.items():
    actions.append({
        "field_name": "group_id",
        "value": group_id,
        "resource_type": "same_ticket",
        "custom_fields": {
            "cf_region": region
        }
    })

# Create the automation rule
automation_rule = {
    "name": "Assign Unassigned Tickets Based on Region at 8 AM",
    "position": 1,
    "active": True,
    "conditions": [
        {
            "name": "condition_set_1",
            "match_type": "all",
            "properties": conditions
        }
    ],
    "actions": actions
}

# Configure logging to both file and console
LOG_FILENAME = 'automation_creation.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Make the API request to create the rule
logging.info("Creating automation rule...")
print("Creating automation rule...")
url = f'https://{domain}/api/v2/automations/{automation_type_id}/rules'
headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(automation_rule))

if response.status_code == 201:
    print("Automation rule created successfully.")
    logging.info("Automation rule created successfully.")
else:
    error_msg = f"Failed to create automation rule. Status Code: {response.status_code}"
    print(error_msg)
    print("Response:", response.json())
    logging.error(error_msg)

def main(rule_config=None, use_gui=False):
    """Main function with optional GUI mode."""
    if rule_config is None:
        rule_config = get_default_rule_config()

    if use_gui:
        def run_rule_creation():
            process_rule_creation_gui(rule_config)

        threading.Thread(target=run_rule_creation, daemon=True).start()
        return

    # Command-line mode
    logging.info("Creating automation rule...")
    print("Creating automation rule...")

    create_automation_rule(rule_config)

def process_rule_creation_gui(rule_config):
    """Process rule creation in GUI mode with progress updates."""
    def update_progress(message):
        progress_var.set(message)
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        app.update_idletasks()

    update_progress("Creating automation rule...")

    success = create_automation_rule(rule_config)

    if success:
        update_progress("✅ Automation rule created successfully!")
        messagebox.showinfo("Success", "Automation rule created successfully!")
    else:
        update_progress("❌ Failed to create automation rule")
        messagebox.showerror("Error", "Failed to create automation rule")

def create_gui():
    """Create the graphical user interface."""
    global rule_name_var, automation_type_var, region_tree, conditions_text, actions_text, log_area, progress_var, app

    app = tk.Tk()
    app.title("Freshdesk Automation Rule Creator")
    app.geometry("800x700")

    # Main frame
    main_frame = ttk.Frame(app, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(main_frame, text="Automation Rule Creator", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Instructions
    instructions = tk.Label(main_frame,
                           text="Configure the automation rule below. This tool creates time-triggered\n"
                                "automation rules for assigning tickets based on regional criteria.",
                           justify="left", fg="gray")
    instructions.grid(row=1, column=0, columnspan=2, pady=10)

    # Basic settings
    settings_frame = ttk.LabelFrame(main_frame, text="Basic Settings", padding="10")
    settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    settings_frame.columnconfigure(1, weight=1)

    # Rule name
    ttk.Label(settings_frame, text="Rule Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
    rule_name_var = tk.StringVar(value="Assign Unassigned Tickets Based on Region at 8 AM")
    rule_name_entry = ttk.Entry(settings_frame, textvariable=rule_name_var, width=50)
    rule_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

    # Automation type
    ttk.Label(settings_frame, text="Automation Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
    automation_type_var = tk.StringVar(value="3")
    automation_type_combo = ttk.Combobox(settings_frame, textvariable=automation_type_var,
                                        values=["3 - Time-triggered"], state="readonly")
    automation_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    # Region mapping section
    mapping_frame = ttk.LabelFrame(main_frame, text="Region to Group Mapping", padding="10")
    mapping_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    # Region mapping treeview
    columns = ("region", "group_id")
    region_tree = ttk.Treeview(mapping_frame, columns=columns, show="headings", height=6)
    region_tree.heading("region", text="Region")
    region_tree.heading("group_id", text="Group ID")
    region_tree.column("region", width=150)
    region_tree.column("group_id", width=100)
    region_tree.grid(row=0, column=0, columnspan=2, pady=5)

    # Load default region mapping
    for region, group_id in DEFAULT_REGION_MAPPING.items():
        region_tree.insert("", tk.END, values=(region, group_id))

    # Mapping controls
    control_frame = ttk.Frame(mapping_frame)
    control_frame.grid(row=1, column=0, columnspan=2, pady=5)

    def add_mapping():
        add_window = tk.Toplevel(app)
        add_window.title("Add Region Mapping")
        add_window.geometry("300x150")

        ttk.Label(add_window, text="Region:").grid(row=0, column=0, padx=10, pady=10)
        region_var = tk.StringVar()
        region_entry = ttk.Entry(add_window, textvariable=region_var, width=20)
        region_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(add_window, text="Group ID:").grid(row=1, column=0, padx=10, pady=10)
        group_id_var = tk.StringVar()
        group_id_entry = ttk.Entry(add_window, textvariable=group_id_var, width=20)
        group_id_entry.grid(row=1, column=1, padx=10, pady=10)

        def save_mapping():
            try:
                region = region_var.get().strip()
                group_id = int(group_id_var.get())

                if not region:
                    messagebox.showerror("Error", "Please enter a region name.")
                    return

                # Check if region already exists
                for item in region_tree.get_children():
                    if region_tree.item(item)["values"][0] == region:
                        messagebox.showerror("Error", f"Region '{region}' already exists.")
                        return

                region_tree.insert("", tk.END, values=(region, group_id))
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric group ID.")

        ttk.Button(add_window, text="Add Mapping", command=save_mapping).grid(row=2, column=0, columnspan=2, pady=10)

    def remove_mapping():
        selection = region_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a mapping to remove.")
            return

        region_tree.delete(selection[0])

    def clear_mappings():
        for item in region_tree.get_children():
            region_tree.delete(item)

    def load_defaults():
        clear_mappings()
        for region, group_id in DEFAULT_REGION_MAPPING.items():
            region_tree.insert("", tk.END, values=(region, group_id))

    ttk.Button(control_frame, text="Add", command=add_mapping).grid(row=0, column=0, padx=5)
    ttk.Button(control_frame, text="Remove", command=remove_mapping).grid(row=0, column=1, padx=5)
    ttk.Button(control_frame, text="Clear", command=clear_mappings).grid(row=0, column=2, padx=5)
    ttk.Button(control_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=3, padx=5)

    # Rule configuration section
    config_frame = ttk.LabelFrame(main_frame, text="Rule Configuration", padding="10")
    config_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

    # Conditions
    ttk.Label(config_frame, text="Conditions (JSON):").grid(row=0, column=0, sticky=tk.W, pady=5)
    conditions_text = scrolledtext.ScrolledText(config_frame, height=4, width=60)
    conditions_text.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
    conditions_text.insert('1.0', json.dumps(DEFAULT_CONDITIONS, indent=2))

    # Actions
    ttk.Label(config_frame, text="Actions (JSON):").grid(row=1, column=0, sticky=tk.W, pady=5)
    actions_text = scrolledtext.ScrolledText(config_frame, height=4, width=60)
    actions_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

    def update_actions():
        """Update actions based on current region mapping."""
        try:
            region_mapping = {}
            for item in region_tree.get_children():
                values = region_tree.item(item)["values"]
                region_mapping[values[0]] = values[1]

            actions = []
            for region, group_id in region_mapping.items():
                actions.append({
                    "field_name": "group_id",
                    "value": group_id,
                    "resource_type": "same_ticket",
                    "custom_fields": {
                        "cf_region": region
                    }
                })

            actions_text.delete('1.0', tk.END)
            actions_text.insert('1.0', json.dumps(actions, indent=2))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update actions: {str(e)}")

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=10)

    def preview_rule():
        try:
            # Get current configuration
            region_mapping = {}
            for item in region_tree.get_children():
                values = region_tree.item(item)["values"]
                region_mapping[values[0]] = values[1]

            conditions = json.loads(conditions_text.get('1.0', tk.END).strip())
            actions = json.loads(actions_text.get('1.0', tk.END).strip())

            rule_config = {
                "name": rule_name_var.get(),
                "automation_type_id": int(automation_type_var.get()),
                "position": 1,
                "active": True,
                "conditions": [{"name": "condition_set_1", "match_type": "all", "properties": conditions}],
                "actions": actions
            }

            preview_text = "Rule Preview:\n\n"
            preview_text += f"Name: {rule_config['name']}\n"
            preview_text += f"Type: {rule_config['automation_type_id']}\n"
            preview_text += f"Regions: {len(region_mapping)}\n"
            preview_text += f"Actions: {len(actions)}\n"

            messagebox.showinfo("Rule Preview", preview_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview rule: {str(e)}")

    def start_creation():
        try:
            # Validate inputs
            if not rule_name_var.get().strip():
                messagebox.showerror("Error", "Please enter a rule name.")
                return

            if region_tree.get_children() == ():
                messagebox.showerror("Error", "Please add at least one region mapping.")
                return

            # Get current configuration
            region_mapping = {}
            for item in region_tree.get_children():
                values = region_tree.item(item)["values"]
                region_mapping[values[0]] = values[1]

            conditions = json.loads(conditions_text.get('1.0', tk.END).strip())
            actions = json.loads(actions_text.get('1.0', tk.END).strip())

            rule_config = {
                "name": rule_name_var.get(),
                "automation_type_id": int(automation_type_var.get()),
                "position": 1,
                "active": True,
                "conditions": [{"name": "condition_set_1", "match_type": "all", "properties": conditions}],
                "actions": actions
            }

            threading.Thread(target=process_rule_creation_gui, args=(rule_config,), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create rule configuration: {str(e)}")

    def load_defaults():
        rule_name_var.set("Assign Unassigned Tickets Based on Region at 8 AM")
        automation_type_var.set("3")
        load_defaults_mapping()
        conditions_text.delete('1.0', tk.END)
        conditions_text.insert('1.0', json.dumps(DEFAULT_CONDITIONS, indent=2))
        update_actions()

    def load_defaults_mapping():
        clear_mappings()
        for region, group_id in DEFAULT_REGION_MAPPING.items():
            region_tree.insert("", tk.END, values=(region, group_id))

    ttk.Button(button_frame, text="Preview Rule", command=preview_rule).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Create Rule", command=start_creation).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Load Defaults", command=load_defaults).grid(row=0, column=2, padx=5)

    # Progress and log area
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=progress_var).grid(row=6, column=0, columnspan=2, pady=5)

    ttk.Label(main_frame, text="Operation Log:").grid(row=7, column=0, columnspan=2, pady=5)
    log_area = scrolledtext.ScrolledText(main_frame, height=8, width=70, state=tk.DISABLED)
    log_area.grid(row=8, column=0, columnspan=2, pady=5)

    return app

def create_automation_rule(rule_config):
    """Create automation rule - refactored to accept configuration."""
    logging.info("Creating automation rule...")
    print("Creating automation rule...")

    url = f'https://{domain}/api/v2/automations/{rule_config["automation_type_id"]}/rules'
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, auth=(api_key, 'X'), headers=headers, data=json.dumps(rule_config))

    if response.status_code == 201:
        print("Automation rule created successfully.")
        logging.info("Automation rule created successfully.")
        return True
    else:
        error_msg = f"Failed to create automation rule. Status Code: {response.status_code}"
        print(error_msg)
        print("Response:", response.json())
        logging.error(error_msg)
        return False

def get_default_rule_config():
    """Get default rule configuration."""
    return {
        "name": "Assign Unassigned Tickets Based on Region at 8 AM",
        "automation_type_id": 3,
        "position": 1,
        "active": True,
        "conditions": [{"name": "condition_set_1", "match_type": "all", "properties": DEFAULT_CONDITIONS}],
        "actions": get_default_actions()
    }

def get_default_actions():
    """Get default actions based on region mapping."""
    actions = []
    for region, group_id in DEFAULT_REGION_MAPPING.items():
        actions.append({
            "field_name": "group_id",
            "value": group_id,
            "resource_type": "same_ticket",
            "custom_fields": {
                "cf_region": region
            }
        })
    return actions

# Default configurations
DEFAULT_REGION_MAPPING = {
    "Central Southeast": 67000578164,
    "Central Southwest": 67000578162,
    "Northeast": 67000578163,
    "West": 67000578161,
    "International": 67000578163,
    "DoDEA": 67000578163
}

DEFAULT_CONDITIONS = [
    {
        "resource_type": "ticket",
        "field_name": "status",
        "operator": "in",
        "value": ["2"]  # Status 'Unassigned' has ID 2 in Freshdesk
    },
    {
        "resource_type": "ticket",
        "field_name": "created_at",
        "operator": "greater_than",
        "value": 0  # This ensures it includes tickets from any time within the last day
    }
]

# Run GUI if --gui flag is passed, otherwise run command line mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        app = create_gui()
        app.mainloop()
    else:
        main()

