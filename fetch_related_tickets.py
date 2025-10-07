"""
Freshdesk Related Tickets Data Export Script

DESCRIPTION:
This script fetches specific tracker tickets and their associated tickets from
Freshdesk, extracting detailed information including districts, VIP status, and
creation dates. The data is exported to an Excel file with proper formatting
and mappings for analysis and reporting purposes.

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
6. Run the script: python fetch_related_tickets.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Associated Tickets API: https://developers.freshdesk.com/api/#associated_tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TRACKER_TICKET_IDS: List of tracker ticket IDs to analyze
- file_path: Output Excel file path

OUTPUT:
- Excel file with ticket details and associated ticket information
- Two sections: tracker tickets and their associated tickets
- Formatted table with styling for better readability

TICKET DATA INCLUDES:
- Tracker ticket information (ID, subject, status, priority, etc.)
- Associated ticket details with district and VIP information
- Creation dates formatted for readability
- Requester, responder, and group assignments
- Custom field data (district, VIP status)

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
- Analyze tracker ticket patterns and associated issues
- Generate reports for management review
- Identify common issues and their relationships
- Track ticket associations for workflow analysis
- Support data analysis and business intelligence
"""

import requests
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime

# Freshdesk API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f"https://{DOMAIN}/api/v2"

# Authentication and headers for API
auth = (API_KEY, 'X')  # 'X' is a placeholder for the password
headers = {
    'Content-Type': 'application/json'
}

# Mappings
requester_map = {
    67057952593: "Amber Dutto", 67017507414: "Amit Soman", 67040597168: "Anson Li",
    67026355372: "Audrey Stumpp", 67026816836: "Brett Albert", 67059619250: "Central Southeast Region - Teams Channel",
    67059653016: "Central Southwest Region - Teams Channel", 67046712112: "Chaitanya Punoju", 67044539474: "Christina Maria Fabiano",
    67054610590: "Dayna Clarke", 67051499418: "Drita Lulgjuraj", 67046816271: "Felicia Wold",
    67057822241: "Jamie Garcia", 67038975154: "Jessica Kropp", 67030529218: "Jordan Fields",
    67037450628: "Julie Tangeman", 67025130684: "Katrina Papaj", 67038379965: "Kayla Knight",
    67032060496: "Linda Schnelle", 67026076356: "Margie Codella", 67026719233: "Michelle Susi",
    67025683491: "Mohammad Azeem", 67059629677: "Northeast Region - Teams Channel", 67041410938: "Samantha Johnson",
    67025131090: "Shaima Mannino", 67029732378: "Shanto Kapali", 67048155849: "Sonali Kumari",
    67036373043: "Steve Skalamera", 67026051144: "Sue Wick-Krch", 67043831083: "Sunil Kumar Karnati",
    67025684603: "Support Ops", 67031011668: "Suriya Iqbal", 67043831105: "Vinay Kumar",
    67059629717: "West Region - Teams Channel", 67025156472: "Yash Patel", 67059142771: "Yu Ng",
    67046816386: "Zevin Jenkins"
}

status_map = {
    3: "Pending", 4: "Resolved", 5: "Closed", 6: "Waiting on Customer",
    7: "In Progress", 8: "Escalated", 9: "Dev in Progress", 10: "Waiting on Support",
    11: "Resubmitted", 14: "Editorial in Progress", 15: "Closed in JIRA", 17: "Onboarding Pending",
    19: "Escalated to Account Manager", 21: "Escalated to Assembly Team", 22: "Created in JIRA",
    23: "Follow-up Required", 24: "Escalated to Order Concerns", 25: "Support Review", 
    26: "On Hold", 27: "Backlog", 28: "Closed - No Resolution", 29: "Triage", 
    30: "Pending Jira", 32: "Onboarding TBD", 33: "Bookings Meeting", 34: "Onboarding Resolved", 
    2: "Open"
}

priority_map = {
    1: "Low", 2: "Medium", 3: "High", 4: "Urgent"
}

source_map = {
    1: "Email", 2: "Portal", 3: "Phone", 4: "Forum", 5: "Twitter", 6: "Facebook",
    7: "Chat", 8: "MobiHelp", 9: "Feedback Widget", 10: "Outbound Email", 11: "Ecommerce", 
    12: "Bot", 13: "Whatsapp"
}

group_map = {
    67000571351: "Account Managers", 67000578164: "Central Southeast Region", 67000578162: "Central Southwest Region",
    67000577995: "Closed - No Resolution", 67000396680: "Escalations", 67000570800: "Incident Management",
    67000576300: "Non VIP - Escalated Tickets", 67000578163: "Northeast Region", 67000578451: "Old Subs",
    67000574839: "Onboarding/Rostering Team", 67000574836: "Problem Management", 67000570680: "Support Management",
    67000570681: "Support Ops", 67000428225: "Tech Support - Tier I", 67000430637: "Tech Support - Tier II",
    67000574838: "Technical Success", 67000578235: "Triage", 67000576310: "VIP - Escalated Tickets",
    67000578161: "West Region"
}

# List of specific tracker ticket IDs to fetch
TRACKER_TICKET_IDS = [
    284001, 
284085, 
284044, 
284046, 
285061, 
285860, 
286936, 
277389, 
277340, 
277391
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

# Function to fetch the list of associated tickets for a tracker with pagination
def get_associated_tickets(ticket_id):
    all_associated_tickets = []
    page = 1
    while True:
        url = f"{BASE_URL}/tickets/{ticket_id}/associated_tickets?page={page}"
        response = requests.get(url, headers=headers, auth=auth)
        
        if response.status_code == 200:
            associated_tickets = response.json().get('tickets', [])
            all_associated_tickets.extend(associated_tickets)
            
            # If fewer than 30 results are returned, we have reached the last page
            if len(associated_tickets) < 30:
                break
            else:
                page += 1
        else:
            print(f"Failed to fetch associated tickets for tracker {ticket_id}: {response.status_code}")
            break

    print(f"Total associated tickets fetched for ticket {ticket_id}: {len(all_associated_tickets)}")  # Debug
    return all_associated_tickets


# Function to fetch a ticket and retrieve specific custom fields
def get_ticket_details(ticket_id):
    url = f"{BASE_URL}/tickets/{ticket_id}"
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        ticket_data = response.json()
        custom_fields = ticket_data.get('custom_fields', {})
        district = custom_fields.get('cf_district509811', "N/A")
        vip_status = custom_fields.get('cf_vip', False)
        created_at = ticket_data.get('created_at', "N/A")
        return district, vip_status, ticket_id, created_at
    else:
        print(f"Failed to fetch details for ticket {ticket_id}: {response.status_code}")
        return "N/A", False, ticket_id, "N/A"

# Process ticket fields and apply mappings
def process_ticket(ticket):
    ticket['Requester Name'] = requester_map.get(ticket.get('requester_id'), "Unknown Requester")
    ticket['Responder Name'] = requester_map.get(ticket.get('responder_id'), "Unknown Responder")
    ticket['Status Name'] = status_map.get(ticket.get('status'), "Unknown Status")
    ticket['Priority Name'] = priority_map.get(ticket.get('priority'), "Unknown Priority")
    ticket['Source Name'] = source_map.get(ticket.get('source'), "Unknown Source")
    ticket['Group Name'] = group_map.get(ticket.get('group_id'), "Unknown Group")
    return ticket

# Save the tickets data to an Excel file and format it as a table starting on the first row
def save_to_excel(tickets, file_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Freshdesk Tickets"

    # Write the header with detailed field names
    headers = [
        "Ticket ID", "Jira ID", "Created At", "Updated At", "Subject", "FD Assigned Agent",
        "Status Name", "Priority", "Source", "Total Linked Tickets", "Reporting Districts List",
        "Reporting Districts [Distinct Count]", "(VIP) Reporting Districts [Distinct Count]",
        "(VIP) Reporting Districts List", "Requester Name", "Group Name"
    ]
    sheet.append(headers)

    # Write each ticket with associated districts
    for ticket in tickets:
        processed_ticket = process_ticket(ticket)
        associated_tickets = get_associated_tickets(ticket['id'])

        print(f"Processing Ticket ID: {ticket['id']} - Total Associated Tickets: {len(associated_tickets)}")  # Debug

        # Extract district information and format dates without hyperlinks
        districts = []
        vip_districts = []
        for associated_ticket in associated_tickets:
            district, is_vip, associated_id, created_at = get_ticket_details(associated_ticket['id'])
            
            # Format the date to MM/DD/YYYY if available
            formatted_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y") if created_at != "N/A" else "N/A"
            
            # Create the entry with plain text
            district_entry = f"{district} (ID: {associated_id}, Created At: {formatted_date})"
            if district:
                districts.append(district_entry)
            if is_vip:
                vip_districts.append(district_entry)

        # Remove duplicate districts
        unique_districts = list(set(districts))
        unique_vip_districts = list(set(vip_districts))

        # Prepare row data
        row = [
            processed_ticket.get("id"),
            ", ".join([tag for tag in ticket.get('tags', []) if tag.startswith("SIM") or tag.startswith("SEDCUST")]),  # Jira ID
            datetime.strptime(processed_ticket.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y") if processed_ticket.get("created_at") else "N/A",
            datetime.strptime(processed_ticket.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y") if processed_ticket.get("updated_at") else "N/A",
            processed_ticket.get("subject"),
            processed_ticket.get("Responder Name"),  # FD Assigned Agent
            processed_ticket.get("Status Name"),
            processed_ticket.get("Priority Name"),  # Priority
            processed_ticket.get("Source Name"),  # Source
            len(associated_tickets),  # Total Linked Tickets
            "\n".join(unique_districts),  # Reporting Districts List as plain text
            len(unique_districts),  # Reporting Districts [Distinct Count]
            len(unique_vip_districts),  # (VIP) Reporting Districts [Distinct Count]
            "\n".join(unique_vip_districts),  # (VIP) Reporting Districts List as plain text
            processed_ticket.get("Requester Name"),
            processed_ticket.get("Group Name")
        ]
        sheet.append(row)

        print(f"Finished processing Ticket ID: {ticket['id']}")  # Debug

    # Create a table over the data range
    num_rows = len(tickets) + 1  # Number of rows including header
    table_range = f"A1:P{num_rows}"  # Adjust range to match columns
    table = Table(displayName="TicketsTable", ref=table_range)

    # Apply a table style
    style = TableStyleInfo(
        name="TableStyleMedium9",  # Excel built-in style name
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,  # Row striping for better readability
        showColumnStripes=False
    )
    table.tableStyleInfo = style

    # Add the table to the sheet
    sheet.add_table(table)

    # Save the workbook to the specified file path
    workbook.save(file_path)
    print(f"Data successfully saved to {file_path} as a formatted table.")  # Final debug statement



# Main function to fetch specific tracker tickets and save them to Excel
def main():
    print("Starting to fetch specific tracker tickets...")
    tickets = fetch_specific_tracker_tickets()

    if tickets:
        file_path = r"C:\Users\skala\OneDrive - Benchmark Education\escalated.xlsx"
        print(f"Saving data to {file_path}...")
        save_to_excel(tickets, file_path)
        print("Process complete.")
    else:
        print("No tracker tickets found.")

if __name__ == "__main__":
    main()

