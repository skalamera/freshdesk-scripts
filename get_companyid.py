import requests
import pandas as pd
import time
import json
import urllib.parse
from difflib import SequenceMatcher

# Freshdesk API credentials
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/companies"

# List of company names
company_names = [
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

# Headers for authentication
auth = (API_KEY, "X")

# Function to calculate string similarity (0-1 scale)
def similarity_ratio(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Function to normalize school district names for better matching
def normalize_name(name):
    # Convert to lowercase
    name = name.lower()
    # Replace common abbreviations
    name = name.replace(" sd ", " school district ")
    name = name.replace(" ps ", " public schools ")
    name = name.replace(" pub ", " public ")
    name = name.replace(" sch ", " school ")
    name = name.replace(" dist ", " district ")
    name = name.replace(" cmty ", " community ")
    name = name.replace(" co ", " county ")
    name = name.replace(" isd ", " independent school district ")
    # Remove common unnecessary words
    return name

# Function to search for company and get its ID with fuzzy matching
def get_company_id(target_name):
    # Debug the response from the API to understand the error
    print(f"Trying direct search for: '{target_name}'")
    
    # Instead of using autocomplete, search directly with filter
    # URL encode the company name for the query
    encoded_name = urllib.parse.quote(target_name)
    search_url = f"{BASE_URL}/filter?query=\"name:'{encoded_name}'\"" 
    
    try:
        response = requests.get(search_url, auth=auth)
        
        print(f"Direct search status code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"Direct search returned {len(results)} results")
            
            if results and len(results) > 0:
                # Return the first match if any found
                return results[0]["id"]
    except Exception as e:
        print(f"Direct search error: {str(e)}")
    
    # If direct search failed, try the full company list with fuzzy matching
    print(f"Beginning fuzzy search for '{target_name}'")
    all_companies = []
    
    try:
        # Get all companies in one request if possible, or use pagination
        list_url = f"{BASE_URL}?per_page=100"  # Maximum allowed per page
        response = requests.get(list_url, auth=auth)
        
        if response.status_code == 200:
            companies = response.json()
            all_companies.extend(companies)
            print(f"Fetched {len(all_companies)} companies for comparison")
        else:
            print(f"Error fetching companies: {response.status_code}")
            print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
            
    except Exception as e:
        print(f"Error in company listing: {str(e)}")
        
    # Find best match using fuzzy string comparison if we have companies
    if not all_companies:
        return "API Error - No Companies Found"
        
    normalized_target = normalize_name(target_name)
    best_match = None
    best_score = 0.6  # Lower threshold to find more matches
    
    for company in all_companies:
        try:
            company_name = company["name"]
            normalized_company = normalize_name(company_name)
            
            # Try both direct and normalized comparison
            direct_score = similarity_ratio(target_name, company_name)
            normalized_score = similarity_ratio(normalized_target, normalized_company)
            score = max(direct_score, normalized_score)
            
            # Debug: Show all potential matches
            if score > 0.5:  # Show any relatively close matches
                print(f"Potential match: '{company_name}' score: {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_match = company
        except Exception as e:
            print(f"Error comparing with company: {str(e)}")
    
    if best_match:
        print(f"Best match for '{target_name}': '{best_match['name']}' with confidence {best_score:.2f}")
        return best_match["id"]
    
    return "Not Found"

# Store results
print("Searching for companies. This may take several minutes...")
company_data = []

# First fetch all companies once to save API calls
print("Pre-fetching all companies...")
all_companies_response = requests.get(f"{BASE_URL}?per_page=100", auth=auth)
all_companies = []

if all_companies_response.status_code == 200:
    all_companies = all_companies_response.json()
    print(f"Successfully pre-fetched {len(all_companies)} companies")
    
    # Print the first few companies to see what data looks like
    if all_companies:
        print("Sample company data:")
        for i in range(min(3, len(all_companies))):
            print(f"  {i+1}. {all_companies[i].get('name', 'N/A')} (ID: {all_companies[i].get('id', 'N/A')})")
else:
    print(f"Error pre-fetching companies: {all_companies_response.status_code}")
    print(f"Response: {all_companies_response.text[:200]}...")

for name in company_names:
    print(f"\nSearching for: {name}")
    try:
        # First try direct matching with the pre-fetched companies
        match_found = False
        normalized_target = normalize_name(name)
        
        for company in all_companies:
            company_name = company.get("name", "")
            if not company_name:
                continue
                
            # Try exact match first (case-insensitive)
            if name.lower() == company_name.lower():
                print(f"Exact match found: {company_name}")
                company_data.append({"Company Name": name, "Company ID": company["id"]})
                match_found = True
                break
                
            # Try normalized matching
            normalized_company = normalize_name(company_name)
            score = similarity_ratio(normalized_target, normalized_company)
            
            if score > 0.8:  # High confidence match
                print(f"High confidence match: '{company_name}' with score {score:.2f}")
                company_data.append({"Company Name": name, "Company ID": company["id"]})
                match_found = True
                break
        
        # If no match found with pre-fetched data, try the API directly
        if not match_found:
            company_id = get_company_id(name)
            print(f"Result for {name}: {company_id}")
            company_data.append({"Company Name": name, "Company ID": company_id})
            
    except Exception as e:
        print(f"Error processing company '{name}': {str(e)}")
        company_data.append({"Company Name": name, "Company ID": f"Error: {str(e)}"})

# Convert to DataFrame
df = pd.DataFrame(company_data)

# Save to Excel
output_file = "company_ids.xlsx"
df.to_excel(output_file, index=False)

print(f"Excel file '{output_file}' has been created successfully.")

