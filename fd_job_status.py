"""
Freshdesk Report Job Status Checker Script

DESCRIPTION:
This script checks the status of a scheduled Freshdesk report export job using
its UUID. It provides information about the export job status, progress, and
completion details for monitoring and automation purposes.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with reports read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update UUID with the UUID of your scheduled export job
4. Ensure your API key has permissions for reports access
5. Run the script: python fd_job_status.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Reports API: https://developers.freshdesk.com/api/#reports
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- UUID: UUID of the scheduled export job to check
- STATUS_URL: Complete API URL for the job status

OUTPUT:
- Console output showing job status and details
- Detailed response information from the API
- Error messages if job status cannot be retrieved

JOB STATUS INFORMATION:
- Job completion status and progress
- Export file details and download URLs
- Error information if job failed
- Timestamps for job start and completion

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Displays detailed error information for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has reports read permissions
- Check that UUID is valid and job exists
- Ensure network connectivity to Freshdesk API
- Check that scheduled export job was created properly

USAGE SCENARIOS:
- Monitor automated report export jobs
- Check job completion before downloading files
- Validate scheduled export configurations
- Integration with automated reporting workflows
"""

import requests
import logging
import sys

# Replace with your details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
UUID = "9a337de4-59f6-408b-80ee-ce752917dab9"
STATUS_URL = f"https://{DOMAIN}/api/v2/reports/omni_schedule/{UUID}"

# Authentication
AUTH = (API_KEY, "X")

# Configure logging to both file and console
LOG_FILENAME = 'job_status_check.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_export_status():
    logging.info(f"Checking export status for UUID: {UUID}")
    print(f"Checking export status for UUID: {UUID}")
    try:
        response = requests.get(STATUS_URL, auth=AUTH)
        response.raise_for_status()
        data = response.json()
        print("Export Status:", data)
        logging.info(f"Export status retrieved successfully: {data}")
        return data
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching export status: {e}"
        print(error_msg)
        logging.error(error_msg)
        return None

if __name__ == "__main__":
    export_status = check_export_status()

