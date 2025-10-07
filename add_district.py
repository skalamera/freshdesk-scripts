import requests
from tkinter import Tk, Label, Entry, Button, messagebox

# Provided API key, domain, and custom field ID
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
CUSTOM_FIELD_ID = '67000953326'

def add_value_to_field(value):
    url = f"https://{DOMAIN}/api/v2/ticket_fields/{CUSTOM_FIELD_ID}"
    
    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {API_KEY}'
    }
    
    # Update the payload with the new value for the dropdown
    payload = {
        "custom_field": {
            "choices": [value]
        }
    }
    
    # Make the API request
    response = requests.put(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        messagebox.showinfo("Success", "Value added successfully!")
    else:
        messagebox.showerror("Error", f"Failed to add value. Status code: {response.status_code}, Response: {response.text}")

def on_submit():
    add_value_to_field(value_entry.get())

root = Tk()
root.title("Add Value to Freshdesk Field")

value_label = Label(root, text="Value to Add:")
value_label.grid(row=0, column=0, sticky="e")
value_entry = Entry(root)
value_entry.grid(row=0, column=1)

submit_button = Button(root, text="Add Value", command=on_submit)
submit_button.grid(row=1, column=0, columnspan=2)

root.mainloop()

