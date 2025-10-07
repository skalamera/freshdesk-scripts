import tkinter as tk
from tkinter import messagebox
import requests
import json

# Configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
auth = (API_KEY, 'X')  # Use the correct authentication
headers = {'Content-Type': 'application/json'}  # Header specifying content type

def create_or_update_company(company_name, state):
    url = f'https://{DOMAIN}/api/v2/companies/autocomplete?name={company_name}'
    response = requests.get(url, auth=auth)
    companies = response.json().get('companies', [])

    # Using 'state' as the field name based on your API fetch details
    company_data = {
        "name": company_name,
        "custom_fields": {
            "state": state  # Directly using 'state' as shown in your API data
        }
    }
    company_data_json = json.dumps(company_data)

    if companies:
        company_id = companies[0]['id']
        update_url = f'https://{DOMAIN}/api/v2/companies/{company_id}'
        response = requests.put(update_url, auth=auth, headers=headers, data=company_data_json)
        if response.status_code != 200:
            raise Exception(f"Failed to update company: {response.text}")
    else:
        create_url = f'https://{DOMAIN}/api/v2/companies'
        response = requests.post(create_url, auth=auth, headers=headers, data=company_data_json)
        if response.status_code != 201:
            raise Exception(f"Failed to create company: {response.text}")

    if 'id' in response.json():
        return response.json()['id']
    else:
        raise Exception("No company ID found in API response.")


def create_or_update_contact(full_name, email, company_id=None):
    url = f'https://{DOMAIN}/api/v2/contacts?email={email}'
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        contacts_response = response.json()
        if contacts_response:
            contact = contacts_response[0]
            contact_id = contact.get('id')
            if contact_id:
                update_url = f'https://{DOMAIN}/api/v2/contacts/{contact_id}'
                contact_data = {
                    "name": full_name,
                    "email": email
                }
                if company_id:
                    contact_data["company_id"] = company_id
                response = requests.put(update_url, auth=auth, headers=headers, data=json.dumps(contact_data))
                if response.status_code == 200:
                    return contact_id, "Updated"
                else:
                    print(f"Failed to update contact: {response.text}")
                    return None
            else:
                print("No ID found in the contact data.")
                return None
        else:
            print("No contacts found for the given email.")
            return None
    elif response.status_code == 404:
        create_url = f'https://{DOMAIN}/api/v2/contacts'
        contact_data = {
            "name": full_name,
            "email": email
        }
        if company_id:
            contact_data["company_id"] = company_id
        response = requests.post(create_url, auth=auth, headers=headers, data=json.dumps(contact_data))
        if response.status_code == 201:
            return response.json()['id'], "Created"
        else:
            print(f"Failed to create contact: {response.text}")
            return None
    else:
        print(f"Error checking contact existence with status {response.status_code}: {response.text}")
        return None

def create_ticket(contact_id, subject, description, status=2, priority=1):
    # Ensure contact_id is an integer
    if not isinstance(contact_id, int):
        raise TypeError(f"Expected integer for contact_id, got {type(contact_id)} instead.")

    ticket_data = {
        "subject": subject,
        "description": description,
        "status": status,
        "priority": priority,
        "requester_id": contact_id,
        "group_id": 67000578451,  # "Old Subs" group
        "responder_id": 67051499418  # Specified agent
    }
    ticket_data_json = json.dumps(ticket_data)
    print("Sending ticket data:", ticket_data)  # Debug print to check the data

    url = f'https://{DOMAIN}/api/v2/tickets'
    response = requests.post(url, auth=auth, headers=headers, data=ticket_data_json)
    if response.status_code != 201:
        raise Exception(f"Failed to create ticket: {response.text}")
    return response.json()

def run_test_cases(selected_cases):
    results = []
    # Use one default contact for all tickets
    contact_result = create_or_update_contact("Test User", "test.user@example.com")
    
    if contact_result and contact_result[0]:
        contact_id, status = contact_result
        
        for case in selected_cases:
            try:
                ticket = create_ticket(
                    contact_id, 
                    case['subject'], 
                    f"This is an automated test ticket for {case['subject']}."
                )
                results.append(f"Ticket created: {case['subject']} (ID: {ticket['id']})")
            except Exception as e:
                results.append(f"Error for {case['subject']}: {str(e)}")
    else:
        results.append("Failed to create or update contact. No tickets created.")
        
    messagebox.showinfo("Test Results", "\n".join(results))

# GUI Setup
root = tk.Tk()
root.title("Test Ticket Creator")

# New test cases with the specified subjects
test_cases = [
    {"subject": "Assembly 1", "var": tk.BooleanVar()},
    {"subject": "Assembly 2", "var": tk.BooleanVar()},
    {"subject": "Assembly Rollover 1", "var": tk.BooleanVar()},
    {"subject": "Assembly Rollover 2", "var": tk.BooleanVar()},
    {"subject": "SEDCUST 1", "var": tk.BooleanVar()},
    {"subject": "SEDCUST 2", "var": tk.BooleanVar()},
    {"subject": "SIM - ASSIGNMENT 1", "var": tk.BooleanVar()},
    {"subject": "SIM - ASSIGNMENT 2", "var": tk.BooleanVar()},
]

# Adding checkboxes
for idx, case in enumerate(test_cases):
    tk.Checkbutton(root, text=case["subject"], variable=case["var"]).grid(row=idx, column=0, sticky='w')

# Select All checkbox
select_all_var = tk.BooleanVar()
def toggle_all():
    for case in test_cases:
        case["var"].set(select_all_var.get())
        
tk.Checkbutton(root, text="Select All", variable=select_all_var, command=toggle_all).grid(row=len(test_cases), column=0, sticky='w')

# Button to run tests
run_button = tk.Button(root, text="Create Selected Tickets", 
                      command=lambda: run_test_cases([case for case in test_cases if case["var"].get()]))
run_button.grid(row=len(test_cases) + 1, column=0, pady=10)

# Status indicator
status_label = tk.Label(root, text="All tickets will be assigned to 'Old Subs' group")
status_label.grid(row=len(test_cases) + 2, column=0, pady=5)

root.mainloop()
