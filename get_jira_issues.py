import requests
from requests.auth import HTTPBasicAuth
import json

# Define the API URL for the specific issue
issue_key = "SEDCUST-5007"  # Ensure this is a string
url = f"https://benchmarkeducation.atlassian.net/rest/api/3/issue/{issue_key}"

# Authentication using your email and API token
auth = HTTPBasicAuth(
    "sskalamera@benchmarkeducation.com",
    "ATATT3xFfGF0A9uOaSYsYVnzKs75H0BIvv0RWn7T4aKO8PZ8ruFA8ZSnsaMN1g59Xh4FUp-pviN68Yx7DbrLLRCsggppBUedG-DWAM4h-V9WBTfme0RtH224-hPrrbPI-bgoudLxTS6qYlsnQb3Mi6OsK0Cw6zrSX9486A"
)

# Define the headers
headers = {
    "Accept": "application/json"
}

# Make the API request
response = requests.request("GET", url, headers=headers, auth=auth)

# Process the response
if response.status_code == 200:
    issue_data = json.loads(response.text)
    print(json.dumps(issue_data, sort_keys=True, indent=4, separators=(",", ": ")))
else:
    print(f"Error {response.status_code}: {response.text}")

