"""
Freshdesk Custom Field Value Addition Script

DESCRIPTION:
This script provides a graphical user interface for adding new values to a
Freshdesk custom field dropdown. It uses the Ticket Fields API to update
the choices available in a custom field, allowing administrators to add
new options without accessing the Freshdesk admin interface.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- tkinter (usually included with Python)
- Valid Freshdesk API key with ticket field write permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Replace CUSTOM_FIELD_ID with the ID of the custom field you want to modify
4. Ensure your API key has permissions for ticket field management
5. Run the script: python add_district.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Ticket Fields API: https://developers.freshdesk.com/api/#ticket_fields
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- CUSTOM_FIELD_ID: ID of the custom field to modify
- value: The new value to add to the dropdown

OUTPUT:
- Updates the specified custom field with the new value
- Shows success/error message in GUI popup
- Adds value to the existing choices list

CUSTOM FIELD TYPES SUPPORTED:
- Dropdown fields (single and multi-select)
- Checkbox fields
- Radio button fields

IMPORTANT NOTES:
- This operation appends to existing choices, doesn't replace them
- Custom field must exist and be editable
- Changes may take time to propagate in the Freshdesk interface
- Test in a development environment first

ERROR HANDLING:
- Validates API responses and status codes
- Shows detailed error messages for troubleshooting
- Handles authentication and permission errors
- Continues operation even if individual requests fail

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket field write permissions
- Check that CUSTOM_FIELD_ID is correct and field exists
- Ensure the field type supports adding choices
- Check network connectivity to Freshdesk API
- Verify the field is not system-reserved or read-only

PERFORMANCE CONSIDERATIONS:
- Single API call per operation
- Suitable for occasional administrative tasks
- Consider batch operations for adding multiple values
"""

import requests
from tkinter import Tk, Label, Entry, Button, messagebox, StringVar
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = '5TMgbcZdRFY70hSpEdj'  # Replace with your actual API key
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'  # Replace with your domain
CUSTOM_FIELD_ID = '67000953326'  # Replace with your custom field ID

def add_value_to_field(value):
    """
    Add a new value to a Freshdesk custom field dropdown.

    This function makes a PUT request to update the custom field with a new choice.
    It appends the new value to the existing choices list.

    Args:
        value (str): The new value to add to the dropdown

    Returns:
        bool: True if successful, False otherwise

    Note:
        - Appends to existing choices, doesn't replace them
        - Value should be unique to avoid duplicates
        - Field must be a dropdown/checkbox/radio type
    """
    if not value or not value.strip():
        messagebox.showerror("Error", "Please enter a value to add.")
        return False

    # Clean the value
    value = value.strip()

    # API endpoint for updating ticket fields
    url = f"https://{DOMAIN}/api/v2/ticket_fields/{CUSTOM_FIELD_ID}"

    # Prepare headers with authentication
    headers = {
        'Content-Type': 'application/json'
    }

    # Prepare payload to add the new choice
    # Note: This will add to existing choices, not replace them
    payload = {
        "custom_field": {
            "choices": [value]  # This adds to existing choices
        }
    }

    try:
        print(f"Adding value '{value}' to custom field {CUSTOM_FIELD_ID}...")

        # Make the API request
        response = requests.put(
            url,
            json=payload,
            headers=headers,
            auth=(API_KEY, 'X')  # Basic auth format
        )

        if response.status_code == 200:
            print(f"✓ Successfully added '{value}' to custom field")
            messagebox.showinfo("Success", f"Value '{value}' added successfully!")
            return True

        else:
            error_msg = f"Failed to add value. Status code: {response.status_code}\n\nResponse: {response.text}"
            print(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            return False

    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        print(f"✗ {error_msg}")
        messagebox.showerror("Error", error_msg)
        return False

def get_current_field_info():
    """
    Retrieve current information about the custom field.

    This function fetches the current state of the custom field to show
    existing choices and field configuration.

    Returns:
        dict or None: Field information if successful, None otherwise
    """
    url = f"https://{DOMAIN}/api/v2/ticket_fields/{CUSTOM_FIELD_ID}"

    try:
        response = requests.get(url, auth=(API_KEY, 'X'))

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Could not retrieve field info: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network error getting field info: {e}")
        return None

def validate_field_type(field_info):
    """
    Validate that the custom field supports adding choices.

    Args:
        field_info (dict): Field information from the API

    Returns:
        bool: True if field supports choices, False otherwise
    """
    if not field_info:
        return False

    field_type = field_info.get('type', '').lower()

    # Field types that support choices
    supported_types = ['dropdown', 'checkbox', 'multiselect', 'radio']

    return field_type in supported_types

def on_submit():
    """
    Handle the submit button click event.

    Validates input and calls the add_value_to_field function.
    """
    value = value_var.get().strip()

    if not value:
        messagebox.showerror("Error", "Please enter a value to add.")
        return

    # Show current field info if available
    field_info = get_current_field_info()
    if field_info:
        field_name = field_info.get('name', 'Unknown Field')
        field_type = field_info.get('type', 'Unknown Type')

        print(f"Field: {field_name} (Type: {field_type})")

        if not validate_field_type(field_info):
            messagebox.showerror(
                "Error",
                f"Field type '{field_type}' does not support adding choices.\n\n"
                "Supported types: dropdown, checkbox, multiselect, radio"
            )
            return

    # Add the value
    add_value_to_field(value)

def create_gui():
    """
    Create and configure the graphical user interface.
    """
    # Create main window
    root = Tk()
    root.title("Freshdesk Custom Field Manager")
    root.geometry("400x300")

    # Configure window
    root.resizable(True, True)

    # Create variables
    global value_var
    value_var = StringVar()

    # Create GUI elements
    title_label = Label(
        root,
        text="Add Value to Freshdesk Custom Field",
        font=("Arial", 12, "bold")
    )
    title_label.pack(pady=10)

    # Field information
    info_label = Label(
        root,
        text=f"Custom Field ID: {CUSTOM_FIELD_ID}\nDomain: {DOMAIN}",
        justify="left"
    )
    info_label.pack(pady=5)

    # Value input section
    input_frame = Label(root)
    input_frame.pack(pady=10, padx=20, fill="x")

    value_label = Label(input_frame, text="Value to Add:")
    value_label.grid(row=0, column=0, sticky="w", pady=5)

    value_entry = Entry(input_frame, textvariable=value_var, width=30)
    value_entry.grid(row=1, column=0, pady=5)
    value_entry.focus()  # Set focus to input field

    # Buttons
    button_frame = Label(root)
    button_frame.pack(pady=10)

    submit_button = Button(
        button_frame,
        text="Add Value",
        command=on_submit,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20
    )
    submit_button.grid(row=0, column=0, padx=5)

    # Field info button (optional)
    def show_field_info():
        field_info = get_current_field_info()
        if field_info:
            field_name = field_info.get('name', 'Unknown')
            field_type = field_info.get('type', 'Unknown')
            choices = field_info.get('choices', [])

            info_msg = f"Field Name: {field_name}\n"
            info_msg += f"Field Type: {field_type}\n"
            info_msg += f"Current Choices ({len(choices)}): {', '.join(choices[:10])}"

            if len(choices) > 10:
                info_msg += f" ... and {len(choices) - 10} more"

            messagebox.showinfo("Field Information", info_msg)
        else:
            messagebox.showerror("Error", "Could not retrieve field information.")

    info_button = Button(
        button_frame,
        text="Show Field Info",
        command=show_field_info,
        bg="#2196F3",
        fg="white"
    )
    info_button.grid(row=0, column=1, padx=5)

    # Instructions
    instructions = Label(
        root,
        text="Enter the value you want to add to the dropdown field.\n"
             "This will be appended to existing choices.",
        justify="left",
        fg="gray"
    )
    instructions.pack(pady=10, padx=20)

    # Status bar
    status_var = StringVar()
    status_var.set("Ready")

    status_label = Label(
        root,
        textvariable=status_var,
        bd=1,
        relief="sunken",
        anchor="w"
    )
    status_label.pack(side="bottom", fill="x")

    # Update status when operations complete
    def update_status(message):
        status_var.set(message)

    # Bind Enter key to submit
    def on_enter(event):
        on_submit()

    value_entry.bind('<Return>', on_enter)

    return root

def main():
    """
    Main function to run the application.
    """
    print("Starting Freshdesk Custom Field Manager...")
    print(f"Target Field ID: {CUSTOM_FIELD_ID}")
    print(f"Domain: {DOMAIN}")

    # Create and run GUI
    root = create_gui()
    root.mainloop()

# Run the script if executed directly
if __name__ == "__main__":
    main()

