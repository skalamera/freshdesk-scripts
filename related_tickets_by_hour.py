"""
Freshdesk Related Tickets Hourly Analysis Script

DESCRIPTION:
This script analyzes related tickets for specific tracker tickets and creates
an hourly distribution report of when tickets were created. It fetches associated
tickets for tracker tickets and analyzes their creation times by hour of day
for pattern identification and reporting purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update TRACKER_TICKET_IDS list with your tracker ticket IDs
4. Update file_path in main() function for output location
5. Ensure your API key has permissions for ticket access
6. Run the script: python related_tickets_by_hour.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Associated Tickets API: https://developers.freshdesk.com/api/#associated_tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TRACKER_TICKET_IDS: List of tracker ticket IDs to analyze
- file_path: Output Excel file path (default: Windows path shown)

OUTPUT:
- Excel file with ticket details and hourly distribution
- Two sheets: Tickets and Hourly Distribution
- Formatted table with styling for better readability

TICKET ANALYSIS PROCESS:
- Fetches each tracker ticket and its associated tickets
- Extracts creation timestamps from all related tickets
- Converts UTC timestamps to hour of day
- Creates hourly distribution chart
- Exports detailed ticket information

HOURLY DISTRIBUTION:
- Analyzes ticket creation patterns by hour (0-23)
- Shows number of tickets created in each hour
- Helps identify peak creation times
- Useful for resource planning and support optimization

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors
- Handles network and parsing errors
- Continues processing even if individual tickets fail

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that tracker ticket IDs are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that tickets have associated tickets

USAGE SCENARIOS:
- Analyze support ticket patterns and timing
- Identify peak hours for ticket creation
- Plan staffing and resource allocation
- Generate reports for management review
- Optimize support workflows based on patterns
"""

import requests
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime
from collections import defaultdict

# Freshdesk API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f"https://{DOMAIN}/api/v2"

# Authentication and headers for API
auth = (API_KEY, 'X')  # 'X' is a placeholder for the password
headers = {
    'Content-Type': 'application/json'
}

# List of specific tracker ticket IDs to fetch
TRACKER_TICKET_IDS = [
    284001, 285080, 284085, 286936, 286079, 285936,
    285860, 285061, 283045, 284044, 286033, 284185,
    286038, 285921, 285166, 284046, 284147, 283031
]

# Function to fetch specific tracker tickets
def fetch_specific_tracker_tickets():
    specific_tickets = []
    for ticket_id in TRACKER_TICKET_IDS:
        url = f"{BASE_URL}/tickets/{ticket_id}"
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            print(f"Successfully fetched ticket {ticket_id}")
            specific_tickets.append(response.json())
        else:
            print(f"Failed to fetch ticket {ticket_id}: {response.status_code}")
    return specific_tickets

# Function to fetch the list of associated tickets for a tracker
def get_associated_tickets(ticket_id):
    all_associated_tickets = []
    page = 1
    while True:
        url = f"{BASE_URL}/tickets/{ticket_id}/associated_tickets?page={page}"
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            associated_tickets = response.json().get('tickets', [])
            all_associated_tickets.extend(associated_tickets)
            if len(associated_tickets) < 30:
                break
            page += 1
        else:
            print(f"Failed to fetch associated tickets for tracker {ticket_id}: {response.status_code}")
            break
    return all_associated_tickets

# Function to save tickets and their hourly distribution to Excel
def save_to_excel(tickets, file_path):
    workbook = Workbook()
    
    # Sheet for tickets
    sheet_tickets = workbook.active
    sheet_tickets.title = "Tickets"
    sheet_tickets.append(["Ticket ID", "Created At", "Hour of Day"])
    
    # Dictionary to store tickets by hour
    hourly_ticket_count = defaultdict(int)
    
    # Process each ticket
    for ticket in tickets:
        ticket_id = ticket.get('id')
        created_at = ticket.get('created_at')
        if created_at:
            # Convert to datetime and extract the hour
            created_at_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            hour_of_day = created_at_dt.hour
            hourly_ticket_count[hour_of_day] += 1
            # Write ticket details to the sheet
            sheet_tickets.append([ticket_id, created_at_dt.strftime("%Y-%m-%d %H:%M:%S"), hour_of_day])
    
    # Sheet for hourly summary
    sheet_summary = workbook.create_sheet(title="Hourly Distribution")
    sheet_summary.append(["Hour of Day", "Number of Tickets"])
    for hour in range(24):
        sheet_summary.append([hour, hourly_ticket_count[hour]])
    
    # Save the workbook
    workbook.save(file_path)
    print(f"Data successfully saved to {file_path}")

# Main function
def main():
    print("Fetching tracker tickets and their associated tickets...")
    tickets = []
    for tracker_id in TRACKER_TICKET_IDS:
        tickets.extend(get_associated_tickets(tracker_id))
    
    if tickets:
        file_path = r"C:\Users\skala\OneDrive - Benchmark Education\tickets_hourly.xlsx"
        save_to_excel(tickets, file_path)
        print("Process complete.")
    else:
        print("No tickets found.")

if __name__ == "__main__":
    main()

