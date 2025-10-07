import requests

API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
TRACKER_ID = 299766

url = f"https://{DOMAIN}/api/v2/tickets/{TRACKER_ID}"
response = requests.get(url, auth=(API_KEY, "X"))

if response.status_code == 200:
    print(response.json())  # Check the ticket details
else:
    print(f"Failed to fetch tracker details: {response.status_code}")
    print(response.text)

