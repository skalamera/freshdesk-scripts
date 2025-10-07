"""
Freshdesk Company ID Lookup Script

DESCRIPTION:
This script searches for company IDs in Freshdesk by matching company names
using fuzzy string matching algorithms. It's designed to help map school
district names and other organization names to their corresponding company
IDs for use in ticket creation, data analysis, and integration workflows.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- pandas library (install with: pip install pandas)
- openpyxl library (install with: pip install openpyxl)
- Valid Freshdesk API key with company read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Update COMPANY_NAMES list with the company names you want to find
4. Ensure your API key has permissions for company read access
5. Run the script: python get_companyid.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- Companies API: https://developers.freshdesk.com/api/#companies
- Authentication: Basic Auth with API key

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- COMPANY_NAMES: List of company names to search for
- OUTPUT_FILENAME: Excel file for results (default: 'company_ids.xlsx')

OUTPUT:
- Excel file with company name to ID mappings
- Console output showing search progress and results
- Detailed logging for troubleshooting

COMPANY MATCHING FEATURES:
- Exact string matching (case-insensitive)
- Fuzzy string matching with configurable thresholds
- Name normalization for better matching (handles abbreviations)
- Multiple matching strategies for improved accuracy

CSV OUTPUT FORMAT:
Company Name,Company ID,Match Type,Confidence Score
"Example School District","67012345","Exact Match","1.0"
"Another District","67023456","Fuzzy Match","0.85"

ERROR HANDLING:
- Handles HTTP 404 (companies not found) errors
- Handles HTTP 429 (rate limit) errors with automatic retry
- Handles network and parsing errors
- Validates API responses and data structure
- Continues processing even if individual searches fail

RATE LIMIT HANDLING:
- Automatically detects rate limit responses (HTTP 429)
- Waits for the specified retry-after period
- Continues processing remaining companies after rate limit delay
- Logs rate limit events for monitoring

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has company read permissions
- Check Freshdesk domain is correct
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard
- Check that company names exist in your Freshdesk account

PERFORMANCE CONSIDERATIONS:
- Pre-fetches all companies to minimize API calls
- Uses efficient string matching algorithms
- Handles large company lists with pagination
- Large datasets may take significant time to process

USAGE SCENARIOS:
- Map external company names to Freshdesk company IDs
- Prepare data for bulk ticket creation
- Generate company reference lists for reports
- Data migration and integration projects
- Quality assurance for company data consistency
"""

import requests
import pandas as pd
import time
import json
import logging
import sys
import urllib.parse
from difflib import SequenceMatcher
from collections import defaultdict

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# Script Configuration
OUTPUT_FILENAME = "company_ids.xlsx"
LOG_FILENAME = "company_lookup.log"
REQUEST_TIMEOUT = 30  # 30 seconds timeout for API requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Company names to search for
# Replace this list with your actual company names
COMPANY_NAMES = [
    "WASHINGTON ELEM SD 6",
    "PEORIA UNIFIED SCHOOL DISTRICT 11",
    "LAMMERSVILLE UNIFIED SCHOOL DISTRICT",
    "OAKLAND UNIFIED SCHOOL DISTRICT",
    "DESERT SANDS UNIFIED SCHOOL DISTRICT",
    "WATERBURY PUBLIC SCHOOL DIST",
    "BROWARD COUNTY PUBLIC SCHOOLS",
    "MIAMI DADE COUNTY PUBLIC SCHOOLS",
    "SCHOOL DISTRICT OF PALM BEACH COUNTY",
    "FORSYTH COUNTY SCHOOLS",
    "SPRINGFIELD PUB SCH DIST 186",
    "OSWEGO COMMUNITY UNIT SCHOOL DISTRICT 308",
    "SIOUX CITY CMTY SCHOOL DIST",
    "FAYETTE CO PUBLIC SCHOOLS",
    "HARFORD COUNTY PS",
    "SPRINGFIELD SCHOOL DIST R12",
    "PORTLAND SCHOOL DISTRICT 1J",
    "ALLENTOWN CITY SCHOOL DISTRICT",
    "KNOX COUNTY SCHOOLS",
    "CONROE ISD",
    "NEWPORT NEWS PUBLIC SCHOOLS",
    "HENRICO COUNTY SCHOOL DISTRICT",
    "FAIRFAX CO PUBLIC SCHOOL DIST",
    "ISSAQUAH SCHOOL DISTRICT 411",
    "DEPARTMENT OF DEFENSE EDUCATION ACTIVITY"
]

def validate_configuration():
    """
    Validate that all required configuration is present and valid.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if not API_KEY or API_KEY == "5TMgbcZdRFY70hSpEdj":
        logging.error("API_KEY not configured. Please set your actual Freshdesk API key.")
        print("❌ API_KEY not configured. Please update the script with your API key.")
        return False

    if not DOMAIN or DOMAIN == "benchmarkeducationcompany.freshdesk.com":
        logging.error("DOMAIN not configured. Please set your actual Freshdesk domain.")
        print("❌ DOMAIN not configured. Please update the script with your domain.")
        return False

    if not COMPANY_NAMES:
        logging.error("COMPANY_NAMES list is empty. Please add company names to search for.")
        print("❌ COMPANY_NAMES list is empty. Please add company names to search for.")
        return False

    return True

def make_api_request(url):
    """
    Make a rate-limited API request to Freshdesk.

    Args:
        url (str): Full URL for the API request

    Returns:
        dict or None: API response data, or None if failed
    """
    try:
        logging.debug(f"Making API request to: {url}")
        response = requests.get(url, auth=(API_KEY, 'X'), timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logging.warning(f"Resource not found: {url}")
            return None
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return make_api_request(url)  # Retry the same request
        else:
            logging.error(f"API request failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logging.error(f"Request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for URL {url}: {e}")
        return None

def calculate_similarity(a, b):
    """
    Calculate string similarity ratio between two strings.

    Args:
        a (str): First string to compare
        b (str): Second string to compare

    Returns:
        float: Similarity ratio (0.0 to 1.0)
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_company_name(name):
    """
    Normalize company name for better matching by expanding abbreviations.

    Args:
        name (str): Company name to normalize

    Returns:
        str: Normalized company name
    """
    if not name:
        return ""

    # Convert to lowercase for consistent processing
    name = name.lower()

    # Replace common abbreviations with full terms
    replacements = {
        " sd ": " school district ",
        " ps ": " public schools ",
        " pub ": " public ",
        " sch ": " school ",
        " dist ": " district ",
        " cmty ": " community ",
        " co ": " county ",
        " isd ": " independent school district ",
        " usd ": " unified school district ",
        " elem ": " elementary ",
        " sec ": " secondary ",
        " hs ": " high school ",
        " ms ": " middle school ",
        " es ": " elementary school ",
        " cty ": " county ",
        " cnty ": " county ",
        " dept ": " department ",
        " edu ": " education ",
        " ed ": " education ",
        " sys ": " system ",
        " svc ": " service ",
        " serv ": " service "
    }

    for abbr, full in replacements.items():
        name = name.replace(abbr, full)

    # Remove extra whitespace
    name = " ".join(name.split())

    return name

def get_all_companies():
    """
    Retrieve all companies from Freshdesk for local matching.

    Returns:
        list: List of company dictionaries, or empty list if failed

    Note:
        - Fetches all companies to avoid repeated API calls
        - Uses pagination to handle large datasets
    """
    base_url = f"https://{DOMAIN}/api/v2/companies"
    all_companies = []
    page = 1

    logging.info("Fetching all companies for local matching...")
    print("Fetching all companies for local matching..."
    while True:
        try:
            # Make API request for current page
            response = requests.get(
                f"{base_url}?page={page}&per_page=100",
                auth=(API_KEY, 'X'),
                timeout=REQUEST_TIMEOUT
            )
        
        if response.status_code == 200:
                # Success - parse response data
                data = response.json()

                if not data:
                    # No more data available
                    logging.info(f"Completed fetching all companies. Total pages: {page - 1}")
                    break

                # Add this page of companies to our collection
                all_companies.extend(data)
                logging.info(f"Fetched page {page} ({len(data)} companies)")
                print(f"  Page {page}: {len(data)} companies retrieved")

                page += 1

            elif response.status_code == 429:
                # Rate limit exceeded - retry after delay
                retry_after = int(response.headers.get('Retry-After', 60))
                logging.warning(f"Rate limit exceeded on page {page}. Retrying after {retry_after} seconds...")
                print(f"⏳ Rate limit reached. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue  # Retry the same page

        else:
                # Other error
                logging.error(f"Failed to fetch companies on page {page}. Status: {response.status_code}")
                logging.error(f"Response: {response.text}")
                print(f"❌ Failed to fetch page {page}: {response.status_code}")
                break

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error on page {page}: {e}")
            print(f"❌ Network error on page {page}: {e}")
            break

    total_companies = len(all_companies)
    logging.info(f"Successfully retrieved {total_companies} companies total")
    print(f"✓ Retrieved {total_companies} companies total")

    return all_companies

def find_company_match(target_name, all_companies):
    """
    Find the best matching company using multiple matching strategies.

    Args:
        target_name (str): Company name to search for
        all_companies (list): List of all companies in Freshdesk

    Returns:
        dict: Best matching company with confidence score, or None if no match
    """
    if not target_name or not all_companies:
        return None

    normalized_target = normalize_company_name(target_name)
    best_match = None
    best_score = 0.0
    match_type = "None"
    
    for company in all_companies:
        try:
            company_name = company.get("name", "")
            if not company_name:
                continue

            # Strategy 1: Exact match (case-insensitive)
            if target_name.lower() == company_name.lower():
                return {
                    "company": company,
                    "confidence": 1.0,
                    "match_type": "Exact Match"
                }

            # Strategy 2: Normalized exact match
            normalized_company = normalize_company_name(company_name)
            if normalized_target == normalized_company:
                return {
                    "company": company,
                    "confidence": 1.0,
                    "match_type": "Normalized Exact Match"
                }

            # Strategy 3: Fuzzy matching with different thresholds
            direct_score = calculate_similarity(target_name, company_name)
            normalized_score = calculate_similarity(normalized_target, normalized_company)

            # Use the higher of the two scores
            score = max(direct_score, normalized_score)
            
            # Check against different confidence thresholds
            if score >= 0.9:
                current_type = "Very High Confidence"
            elif score >= 0.8:
                current_type = "High Confidence"
            elif score >= 0.7:
                current_type = "Medium Confidence"
            elif score >= 0.6:
                current_type = "Low Confidence"
            else:
                continue  # Skip low-confidence matches

            # Update best match if this score is higher
            if score > best_score:
                best_score = score
                best_match = {
                    "company": company,
                    "confidence": score,
                    "match_type": current_type
                }

        except Exception as e:
            logging.warning(f"Error comparing '{target_name}' with company: {e}")
            continue

    return best_match

def save_results_to_excel(company_data, filename):
    """
    Save company lookup results to Excel file.

    Args:
        company_data (list): List of company lookup results
        filename (str): Output Excel filename

    Returns:
        bool: True if save successful, False otherwise
    """
    if not company_data:
        logging.warning("No company data to save")
        print("⚠ No company data to save")
        return False

    try:
        # Create DataFrame
        df = pd.DataFrame(company_data)

        # Reorder columns for better readability
        desired_columns = ['Company Name', 'Company ID', 'Match Type', 'Confidence Score', 'Matched Company Name']
        available_columns = [col for col in desired_columns if col in df.columns]

        # Save to Excel
        df.to_excel(filename, index=False, columns=available_columns if available_columns else None)

        file_size = len(df)  # Approximate row count
        logging.info(f"Successfully saved {len(company_data)} company lookups to {filename}")
        print(f"✓ Saved {len(company_data)} company lookups to {filename}")
        return True

    except PermissionError:
        error_msg = f"Permission denied writing to {filename}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False
        except Exception as e:
        error_msg = f"Error saving Excel file: {e}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def analyze_results(company_data):
    """
    Analyze the lookup results and provide insights.

    Args:
        company_data (list): List of company lookup results

    Returns:
        dict: Analysis results and statistics
    """
    if not company_data:
        return {}

    analysis = {
        "total_companies": len(company_data),
        "found_companies": 0,
        "not_found_companies": 0,
        "error_companies": 0,
        "match_type_distribution": defaultdict(int),
        "confidence_distribution": defaultdict(int),
        "problematic_companies": []
    }

    for result in company_data:
        company_id = result.get("Company ID", "")

        if company_id in ["Not Found", "API Error - No Companies Found"]:
            analysis["not_found_companies"] += 1
            analysis["problematic_companies"].append(result.get("Company Name", "Unknown"))
        elif company_id.startswith("Error:"):
            analysis["error_companies"] += 1
            analysis["problematic_companies"].append(result.get("Company Name", "Unknown"))
        else:
            analysis["found_companies"] += 1

        # Match type distribution
        match_type = result.get("Match Type", "None")
        analysis["match_type_distribution"][match_type] += 1

        # Confidence distribution
        confidence = result.get("Confidence Score", 0.0)
        if confidence >= 0.9:
            analysis["confidence_distribution"]["Very High (≥0.9)"] += 1
        elif confidence >= 0.8:
            analysis["confidence_distribution"]["High (≥0.8)"] += 1
        elif confidence >= 0.7:
            analysis["confidence_distribution"]["Medium (≥0.7)"] += 1
        elif confidence >= 0.6:
            analysis["confidence_distribution"]["Low (≥0.6)"] += 1
else:
            analysis["confidence_distribution"]["Very Low (<0.6)"] += 1

    return analysis

def main():
    """
    Main function to orchestrate the company ID lookup process.
    """
    print("Freshdesk Company ID Lookup Tool")
    print("=" * 60)

    logging.info("Starting Freshdesk Company ID Lookup Tool")

    # Validate configuration
    if not validate_configuration():
        print("❌ Configuration validation failed.")
        return 1

    try:
        # Step 1: Pre-fetch all companies for efficient matching
        print("Step 1: Fetching all companies from Freshdesk...")
        all_companies = get_all_companies()

        if not all_companies:
            logging.error("Failed to fetch companies from Freshdesk")
            print("❌ Failed to fetch companies. Please check:")
            print("  - API key has company read permissions")
            print("  - Freshdesk domain is correct")
            print("  - Network connectivity to Freshdesk")
            return 1

        # Show sample of fetched companies
        print("
📋 SAMPLE COMPANIES IN FRESHdesk:"        for i, company in enumerate(all_companies[:5], 1):
            print(f"  {i}. {company.get('name', 'N/A')} (ID: {company.get('id', 'N/A')})")
        if len(all_companies) > 5:
            print(f"  ... and {len(all_companies) - 5} more companies")

        # Step 2: Process each company name
        print("
Step 2: Searching for company matches..."        company_data = []

        for i, target_name in enumerate(COMPANY_NAMES, 1):
            print(f"\n  [{i}/{len(COMPANY_NAMES)}] Searching for: '{target_name}'")

            # Find best match
            match = find_company_match(target_name, all_companies)

            if match:
                company = match["company"]
                confidence = match["confidence"]
                match_type = match["match_type"]

                result = {
                    "Company Name": target_name,
                    "Company ID": company.get("id"),
                    "Match Type": match_type,
                    "Confidence Score": round(confidence, 3),
                    "Matched Company Name": company.get("name")
                }

                print(f"    ✓ {match_type}: '{company.get('name')}' (ID: {company.get('id')}) - Confidence: {confidence:.3f}")
            else:
                result = {
                    "Company Name": target_name,
                    "Company ID": "Not Found",
                    "Match Type": "No Match",
                    "Confidence Score": 0.0,
                    "Matched Company Name": "N/A"
                }
                print(f"    ❌ No match found")

            company_data.append(result)

            # Small delay between searches to be respectful
            time.sleep(0.1)

        # Step 3: Save results
        print("
Step 3: Saving results to Excel..."        if save_results_to_excel(company_data, OUTPUT_FILENAME):
            # Step 4: Analyze results
            print("
Step 4: Analyzing results..."            analysis = analyze_results(company_data)

            # Display analysis results
            print("
📊 LOOKUP ANALYSIS:"            print(f"  Total companies searched: {analysis['total_companies']}")
            print(f"  Companies found: {analysis['found_companies']}")
            print(f"  Companies not found: {analysis['not_found_companies']}")
            print(f"  Companies with errors: {analysis['error_companies']}")

            print("
🎯 MATCH TYPE DISTRIBUTION:"            for match_type, count in analysis['match_type_distribution'].items():
                print(f"  {match_type}: {count}")

            print("
📈 CONFIDENCE DISTRIBUTION:"            for confidence_range, count in analysis['confidence_distribution'].items():
                print(f"  {confidence_range}: {count}")

            if analysis['problematic_companies']:
                print(f"\n⚠ PROBLEMATIC COMPANIES ({len(analysis['problematic_companies'])}):")
                for company_name in analysis['problematic_companies'][:5]:  # Show first 5
                    print(f"  {company_name}")
                if len(analysis['problematic_companies']) > 5:
                    print(f"  ... and {len(analysis['problematic_companies']) - 5} more")

            # Final summary
            print("
" + "=" * 60)
            print("LOOKUP SUMMARY")
            print("=" * 60)
            print(f"✓ Company lookup completed successfully!")
            print(f"  Companies processed: {len(company_data)}")
            print(f"  Companies found: {analysis['found_companies']}")
            print(f"  Success rate: {analysis['found_companies'] / len(company_data) * 100:.1f}%")
            print(f"  Results saved to: {OUTPUT_FILENAME}")
            print(f"  Log file: {LOG_FILENAME}")

            # Show recommendations
            if analysis['not_found_companies'] > 0:
                print(f"\n⚠ {analysis['not_found_companies']} companies were not found")
                print("  Consider checking company names for typos")
                print("  Some companies may not exist in Freshdesk yet")

            if analysis['error_companies'] > 0:
                print(f"\n⚠ {analysis['error_companies']} companies had lookup errors")
                print("  Check logs for detailed error information")

            logging.info("=" * 60)
            logging.info("COMPANY LOOKUP COMPLETED SUCCESSFULLY")
            logging.info("=" * 60)
            logging.info(f"Companies processed: {len(company_data)}")
            logging.info(f"Companies found: {analysis['found_companies']}")
            logging.info(f"Companies not found: {analysis['not_found_companies']}")
            logging.info(f"Success rate: {analysis['found_companies'] / len(company_data) * 100:.1f}%")
            logging.info(f"Results saved to: {OUTPUT_FILENAME}")
            logging.info("=" * 60)

            return 0
        else:
            print("❌ Failed to save results. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print("\n⚠ Lookup interrupted by user")
        logging.info("Lookup interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during lookup: {e}")
        logging.error(f"Unexpected error during lookup: {e}")
        return 1

# Run the script if executed directly
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

