import requests
import json

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
RELATED_TICKET_ID = 115423  # The ticket to which the tracker will be linked
ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for creating a new tracker ticket
create_ticket_url = f"https://{DOMAIN}/api/v2/tickets"

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
    "Content-Type": "application/json"
}

# Step 1: Create the tracker ticket (without attachment)
ticket_payload = {
    "description": "This is a tracker ticket linked to another issue.",
    "subject": "Tracker Ticket for Issue #115423",
    "email": "sskalamera@benchmarkeducation.com",  # Required to create the ticket
    "related_ticket_ids": [RELATED_TICKET_ID],  # Must be an array of integers
    "priority": 1,  # 1 = Low, 2 = Medium, 3 = High, 4 = Urgent
    "status": 2,  # 2 = Open, 3 = Pending, 4 = Resolved, 5 = Closed
    "cc_emails": ["skalamera@gmail.com"]  # Must be an array
}

# Send request to create tracker ticket
create_response = requests.post(create_ticket_url, auth=(API_KEY, "X"), headers=headers, json=ticket_payload)

# Check if ticket creation was successful
if create_response.status_code == 201:
    tracker_ticket = create_response.json()  # Get response as JSON
    tracker_ticket_id = tracker_ticket["id"]  # Extract new ticket ID
    print(f"âœ… Tracker ticket created successfully! Ticket ID: {tracker_ticket_id}")
else:
    print(f"âŒ Failed to create tracker ticket: {create_response.status_code}, {create_response.text}")
    exit()  # Stop script if creation fails

# Step 2: Update the newly created tracker ticket with the attachment
update_ticket_url = f"https://{DOMAIN}/api/v2/tickets/{tracker_ticket_id}/notes"

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Payload for adding a private note with the attachment
    update_payload = {
        "body": "Attaching relevant screenshot to the tracker ticket.",
        "private": "true"  # Must be string "true" or "false" when using multipart
    }

    # Send request to update the ticket with the attachment
    update_response = requests.post(update_ticket_url, auth=(API_KEY, "X"), files=files, data=update_payload)

# Check if update was successful
if update_response.status_code == 201:
    print("âœ… Attachment added successfully to the tracker ticket!")
else:
    print(f"âŒ Failed to add attachment: {update_response.status_code}, {update_response.text}")

