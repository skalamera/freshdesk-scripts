import requests

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
TICKET_ID = 298629
ATTACHMENT_PATH = r"C:\Downloads\4 (2).png"

# API URL for adding a note with an attachment
url = f"https://{DOMAIN}/api/v2/tickets/{TICKET_ID}/notes"

# Headers for authentication
headers = {
    "Authorization": f"{API_KEY}:X",
}

# Open the attachment file
with open(ATTACHMENT_PATH, "rb") as file:
    files = {
        "attachments[]": (ATTACHMENT_PATH.split("\\")[-1], file, "image/png"),
    }

    # Data payload (private note with attachment)
    data = {
        "body": "Here is the attached screenshot for the ticket.",
        "private": "true"  # Freshdesk API expects a string "true"/"false" instead of a boolean
    }

    # Send POST request using multipart/form-data
    response = requests.post(url, auth=(API_KEY, "X"), files=files, data=data)

# Handle response
if response.status_code == 201:
    print("âœ… Attachment added successfully as a note!")
elif response.status_code == 429:
    print("âš ï¸ Rate limit exceeded. Try again later.")
else:
    print(f"âŒ Failed to add attachment: {response.status_code}, {response.text}")

