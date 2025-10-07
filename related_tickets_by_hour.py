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

