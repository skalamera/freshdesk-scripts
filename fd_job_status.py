import requests

# Replace with your details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
UUID = "9a337de4-59f6-408b-80ee-ce752917dab9"
STATUS_URL = f"https://{DOMAIN}/api/v2/reports/omni_schedule/{UUID}"

# Authentication
AUTH = (API_KEY, "X")

def check_export_status():
    try:
        response = requests.get(STATUS_URL, auth=AUTH)
        response.raise_for_status()
        data = response.json()
        print("Export Status:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching export status: {e}")
        return None

if __name__ == "__main__":
    export_status = check_export_status()

