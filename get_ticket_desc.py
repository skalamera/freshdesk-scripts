"""
Freshdesk Ticket Descriptions Batch Retrieval Script

DESCRIPTION:
This script retrieves descriptions for multiple Freshdesk tickets and exports
them to an Excel file with comprehensive logging. It processes a predefined
list of ticket IDs and handles rate limiting automatically.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with ticket read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update ticket_ids list with the ticket IDs you want to retrieve
4. Ensure your API key has the necessary permissions for ticket access
5. Run the script: python get_ticket_desc.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- ticket_ids: List of ticket IDs to retrieve descriptions for
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain

OUTPUT:
- Excel file with ticket IDs and their descriptions
- Log file with detailed operation information
- Console output showing progress and results

EXCEL OUTPUT FORMAT:
- Column 1: Ticket ID
- Column 2: Description (or "No description available" if empty)

LOGGING:
- Creates 'ticket_fetch_log.log' with detailed operation logs
- Logs successful fetches, errors, and rate limit handling
- Includes timestamps for troubleshooting

ERROR HANDLING:
- Handles HTTP 404 (ticket not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Continues processing even if individual tickets fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining tickets after rate limit delay

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has ticket read permissions
- Check that ticket IDs in the list are valid
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check log file for detailed error information

PERFORMANCE CONSIDERATIONS:
- Processes tickets sequentially to respect rate limits
- Includes small delays between requests if needed
- Large ticket lists may take significant time to process
"""

import requests
import pandas as pd
import time
import logging
import os

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ticket_fetch_log.log"),
        logging.StreamHandler()  # Also log to console
    ]
)

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain
BASE_URL = f"https://{DOMAIN}/api/v2/tickets/"

# List of ticket IDs to retrieve descriptions for
# Replace this list with your actual ticket IDs
ticket_ids = [
    293528, 293352, 293203, 293181, 293156, 293128, 292629, 292587, 291674,
    290332, 290217, 290199, 290196, 290174, 290152, 290146, 290134, 290073,
    290070, 290065, 290041, 289939, 289899, 289885, 289866, 289855, 289775,
    289675, 289645, 289644, 289638, 289599, 289569, 289567, 289541, 289524,
    289518, 289461, 289443, 289435, 289388, 289339, 289322, 289320, 289319,
    289231, 289225, 289204, 289160, 289151, 289075, 289062, 289059, 289046,
    289027, 288982, 288915, 288908, 288838, 288755, 288751, 288699, 288695,
    288692, 288659, 288657, 288621, 288609, 288582, 288581, 288528, 288521,
    288502, 288453, 288447, 288438, 288361, 288355, 288353, 288313, 288280,
    288221, 288115, 288087, 287980, 287943, 287860, 287841, 287748, 287747,
    287715, 287679, 287627, 287626, 287624, 287592, 287582, 287577, 287575,
    287570, 287557, 287535, 287476, 287464, 287461, 287427, 287380, 287371,
    287354, 287330, 287315, 287312, 287299, 287288, 287276, 287268, 287253,
    287250, 287238, 287235, 287227, 287215, 287099, 287085, 287080, 287079,
    287056, 286816, 286806, 286779, 286660, 286630, 286570, 286560, 286549,
    286511, 286472, 286358, 286344, 286337, 286324, 286318, 286277, 286264,
    286253, 286244, 286194, 286062, 286022, 285921, 285809, 285783, 285769,
    285768, 285766, 285759, 285743, 285732, 285657, 285604, 285568, 285556,
    285552, 285491, 285429, 285395, 285358, 285346, 285341, 285315, 285309,
    285298, 285294, 285191, 285178, 285167, 285156, 285007, 284986, 284966,
    284886, 284791, 284749, 284667, 284663, 284645, 284636, 284552, 284538,
    284504, 284374, 284334, 284321, 284284, 284167, 284163, 283946, 283898,
    283883, 283875, 283871, 283861, 283855, 283833, 283760, 283755, 283568,
    283565, 283532, 283465, 283443, 283403, 283292, 283229, 283167, 283055,
    283036, 283027, 282964, 282922, 282900, 282897, 282894, 282892, 282886,
    282883, 282880, 282789, 282728, 282696, 282693, 282539, 282526, 282525,
    282519, 282518, 282500, 282484, 282480, 282416, 282412, 282394, 282270,
    282205, 282165, 282149, 282144, 282073, 281993, 281992, 281990, 281980,
    281969, 281961, 281959, 281953, 281727, 281717, 281667, 281641, 281376,
    281313, 281230, 281224, 281129, 280915, 280909, 280855, 280791, 280764,
    280756, 277711, 277696, 277676, 277654, 277651, 277570, 277511, 277503,
    277454, 277325, 277176, 277122, 277119, 277042, 277017, 277005, 276837,
    276624, 276480, 276476, 276439, 276431, 276380, 276299, 276223, 276167,
    276137, 275983, 275948, 275945, 275898, 275861, 275848, 275832, 275816,
    275703, 275563, 275523, 275518, 275389, 275341, 275337, 275314, 275185,
    275165, 275157, 274839, 274619, 274595, 274535, 274402, 274388, 274378,
    274252, 274136, 274017, 273991, 273947, 273755, 273694, 273627, 273597,
    273461, 273433, 273255, 273241, 273212, 273183, 273172, 273162, 272740,
    272569, 272176, 272066, 272058, 272055, 271856, 271366, 271341, 271330,
    271208, 271179, 271167, 271059, 270775, 270705, 270679, 270407, 270286,
    270277, 270270, 270265, 270114, 270019, 270008, 269949, 269792, 269768,
    269627
]

# HTTP Headers for API requests
headers = {
    "Content-Type": "application/json",
}

def fetch_ticket_description(ticket_id):
    """
    Fetch the description for a single ticket.

    Args:
        ticket_id (int): The ticket ID to fetch

    Returns:
        tuple: (ticket_id, description) or (ticket_id, None) if failed
    """
    try:
        # Make API request for ticket details
        response = requests.get(
            f"{BASE_URL}{ticket_id}",
            auth=(API_KEY, "X"),
            headers=headers
        )

        if response.status_code == 200:
            # Success - extract description
            ticket_data = response.json()
            description = ticket_data.get("description_text", "No description available")
            logging.info(f"Successfully fetched Ticket ID {ticket_id}")
            return ticket_id, description

        elif response.status_code == 404:
            # Ticket not found
            logging.warning(f"Ticket ID {ticket_id} not found (404)")
            return ticket_id, None

        elif response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Rate limit reached for Ticket ID {ticket_id}. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            # Retry the request
            return fetch_ticket_description(ticket_id)

        else:
            # Other error
            logging.error(f"Failed to fetch Ticket ID {ticket_id}. HTTP Status Code: {response.status_code}")
            return ticket_id, None

    except Exception as e:
        logging.error(f"Error fetching Ticket ID {ticket_id}: {e}")
        return ticket_id, None

def main():
    """
    Main function to process all tickets and export to Excel.
    """
    print("Starting batch ticket description retrieval...")
    print(f"Processing {len(ticket_ids)} tickets...")

    # Collect data for all tickets
    data = []

    for i, ticket_id in enumerate(ticket_ids, 1):
        print(f"Processing ticket {i}/{len(ticket_ids)}: ID {ticket_id}")

        # Fetch ticket description
        ticket_id_result, description = fetch_ticket_description(ticket_id)

        if description is not None:
            data.append({
                "Ticket ID": ticket_id_result,
                "Description": description
            })

        # Small delay between requests to be respectful
        time.sleep(0.1)

    # Export to Excel
    if data:
        df = pd.DataFrame(data)
        output_file = "ticket_descriptions_with_logs.xlsx"

        try:
            df.to_excel(output_file, index=False)
            print(f"\n✓ Successfully exported {len(data)} ticket descriptions to {output_file}")
            logging.info(f"Ticket descriptions exported to {output_file}")
        except Exception as e:
            print(f"✗ Failed to export to Excel: {e}")
            logging.error(f"Failed to export to Excel: {e}")
    else:
        print("✗ No ticket data to export")
        logging.warning("No ticket data collected for export")

    print(f"\nProcessing complete. Check 'ticket_fetch_log.log' for detailed logs.")

# Run the script if executed directly
if __name__ == "__main__":
    main()

