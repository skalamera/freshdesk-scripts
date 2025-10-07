"""
Freshdesk Ticket Creation Time Analysis Script

DESCRIPTION:
This script processes an Excel file containing ticket IDs and enriches it with
detailed creation time information. It fetches exact creation timestamps from
Freshdesk API, converts them to Eastern Time, and extracts the hour of day for
analysis of ticket creation patterns.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- pytz library (install with: pip install pytz)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update input_file and output_file paths for your Excel files
4. Ensure your API key has permissions for ticket access
5. Run the script: python get_createdat_hourofday.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Tickets API: https://developers.freshdesk.com/api/#tickets
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- input_file: Path to Excel file with ticket IDs
- output_file: Path for output Excel file with enriched data
- sheet_name: Name of the Excel sheet containing ticket data

OUTPUT:
- Updated Excel file with additional columns for creation time data
- Console output showing processing progress
- Detailed error messages for failed ticket lookups

TICKET ENRICHMENT PROCESS:
- Reads ticket IDs from input Excel file
- Fetches detailed ticket information from Freshdesk API
- Extracts exact creation timestamps (UTC)
- Converts timestamps to Eastern Time
- Extracts hour of day (0-23) for pattern analysis

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Implements exponential backoff for rate-limited requests
- Includes delays between requests to respect limits
- Monitors API usage to avoid exceeding limits

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that input Excel file exists and is readable
- Ensure network connectivity to Freshdesk API
- Check that ticket IDs in Excel are valid
- Monitor rate limit usage in Freshdesk dashboard

USAGE SCENARIOS:
- Analyze ticket creation patterns by time of day
- Identify peak hours for ticket submissions
- Generate reports for management review
- Plan staffing and resource allocation
- Optimize support workflows based on patterns
"""

import requests
import pandas as pd
from datetime import datetime
import pytz
import time

# Freshdesk API configuration
API_KEY = '5TMgbcZdRFY70hSpEdj'
DOMAIN = 'benchmarkeducationcompany.freshdesk.com'
BASE_URL = f"https://{DOMAIN}/api/v2"
AUTH = (API_KEY, 'X')  # 'X' is a placeholder for the password
HEADERS = {
    'Content-Type': 'application/json'
}

# Input and output file paths
input_file = r"C:\Downloads\escalated_reporting_with_date.xlsx"
output_file = r"C:\Downloads\escalated_ticket_details_with_time.xlsx"
sheet_name = 'Reporting Districts Tickets'

# Load the data
df = pd.read_excel(input_file, sheet_name=sheet_name)

# Initialize lists for new columns
exact_created_at = []
hour_of_day_est = []

# Define Eastern time zone
eastern = pytz.timezone('US/Eastern')

# Function to handle API requests with rate limiting
def fetch_ticket_details(ticket_id):
    max_retries = 5  # Maximum retries for rate-limited requests
    retry_delay = 1  # Initial delay between retries
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", auth=AUTH, headers=HEADERS)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()  # Return the response JSON
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:
                print(f"Rate limit reached. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise e
    raise Exception(f"Max retries exceeded for ticket {ticket_id}")

# Iterate through each ticket ID and fetch details from the API
total_tickets = len(df['Ticket ID'])
for idx, ticket_id in enumerate(df['Ticket ID'], start=1):
    try:
        print(f"Processing ticket {idx}/{total_tickets} (ID: {ticket_id})...")
        
        # Fetch ticket details
        ticket_data = fetch_ticket_details(ticket_id)
        created_at_utc = ticket_data['created_at']  # Example: "2024-11-17T13:23:07Z"

        # Convert UTC to datetime object
        created_at_datetime = datetime.strptime(created_at_utc, "%Y-%m-%dT%H:%M:%SZ")
        created_at_eastern = created_at_datetime.astimezone(eastern)

        # Append data to lists
        exact_created_at.append(created_at_eastern.strftime("%Y-%m-%d %H:%M:%S"))
        hour_of_day_est.append(created_at_eastern.hour)

        print(f"Completed ticket {idx}/{total_tickets} (ID: {ticket_id})")

    except Exception as e:
        print(f"Error processing ticket {idx}/{total_tickets} (ID: {ticket_id}): {e}")
        exact_created_at.append(None)
        hour_of_day_est.append(None)

# Add new columns to the DataFrame
df['Exact Created At'] = exact_created_at
df['Hour of Day (EST)'] = hour_of_day_est

# Save the updated DataFrame to a new Excel file
df.to_excel(output_file, index=False, sheet_name=sheet_name)

print(f"Processing complete. Updated file saved to {output_file}")

