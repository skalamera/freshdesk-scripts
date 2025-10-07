import requests
import json

# Define API credentials and endpoints
api_key = "5TMgbcZdRFY70hSpEdj"
sandbox_domain = "benchmarkeducationcompanysandbox.freshdesk.com"
headers = {
    "Content-Type": "application/json"
}

# Function to create a new company
def create_company(company_name):
    url = f"https://{sandbox_domain}/api/v2/companies"
    company_data = {
        "name": company_name,
    }

    response = requests.post(url, auth=(api_key, "X"), headers=headers, data=json.dumps(company_data))
    
    if response.status_code == 201:
        print("Company created successfully:", response.json())
        return response.json()["id"]  # Return the company ID
    elif response.status_code == 409:
        # Handle duplicate company error
        error_info = response.json().get("errors", [])
        if error_info and "additional_info" in error_info[0]:
            company_id = error_info[0]["additional_info"].get("company_id")
            print(f"Company already exists. Using existing company ID: {company_id}")
            return company_id
        else:
            print("Failed to create company due to duplicate value, but no ID was returned.")
            return None
    else:
        print("Failed to create company:", response.status_code, response.text)
        return None

# Function to create or associate a requester with a company
def create_or_associate_requester(unique_external_id, company_id):
    # First, try to find the requester by unique_external_id
    search_url = f"https://{sandbox_domain}/api/v2/search/contacts?query=\"unique_external_id:{unique_external_id}\""
    response = requests.get(search_url, auth=(api_key, "X"), headers=headers)
    
    if response.status_code == 200:
        contacts = response.json().get("results", [])
        if contacts:
            contact = contacts[0]
            print(f"Requester found with ID: {contact['id']}")
            # Check if the contact is already associated with the company
            if contact.get("company_id") == company_id:
                print("Requester already associated with the company.")
                return contact["id"]
            else:
                # Update the contact to associate it with the company
                update_url = f"https://{sandbox_domain}/api/v2/contacts/{contact['id']}"
                update_data = {
                    "company_id": company_id
                }
                update_response = requests.put(update_url, auth=(api_key, "X"), headers=headers, data=json.dumps(update_data))
                if update_response.status_code == 200:
                    print("Requester successfully associated with the company.")
                    return contact["id"]
                else:
                    print("Failed to associate requester with the company:", update_response.status_code, update_response.text)
                    return None
        else:
            print("Requester not found. Creating a new one.")
    else:
        print("Failed to search for requester:", response.status_code, response.text)

    # If the requester does not exist, create a new one
    create_url = f"https://{sandbox_domain}/api/v2/contacts"
    contact_data = {
        "unique_external_id": unique_external_id,
        "company_id": company_id,
        "name": "Default Requester Name"  # Provide a default name for the requester
    }
    create_response = requests.post(create_url, auth=(api_key, "X"), headers=headers, data=json.dumps(contact_data))
    
    if create_response.status_code == 201:
        print("Requester created and associated with the company:", create_response.json())
        return create_response.json()["id"]
    else:
        print("Failed to create requester:", create_response.status_code, create_response.text)
        return None

# Function to create a new ticket using a requester's ID
def create_ticket(subject, description, company_id, requester_id):
    url = f"https://{sandbox_domain}/api/v2/tickets"
    ticket_data = {
        "subject": subject,
        "description": description,
        "status": 2,  # Assuming 'Open' status
        "priority": 1,  # Assuming 'Low' priority
        "company_id": company_id,
        "requester_id": requester_id  # Use the requester's ID instead of unique_external_id
    }

    response = requests.post(url, auth=(api_key, "X"), headers=headers, data=json.dumps(ticket_data))
    
    if response.status_code == 201:
        print("Ticket created successfully:", response.json())
    else:
        print("Failed to create ticket:", response.status_code, response.text)

# Main execution
if __name__ == "__main__":
    company_name = "New New New Company"
    ticket_subject = "New Support Request"
    ticket_description = "Description of the issue or request."
    test_unique_external_id = "newnewnew1234"  # Test unique external ID

    # Step 1: Attempt to create the company or use the existing one
    company_id = create_company(company_name)

    # Step 2: Ensure the requester is associated with the company
    if company_id:
        requester_id = create_or_associate_requester(test_unique_external_id, company_id)

        # Step 3: Create a new ticket for the company using the requester's ID
        if requester_id:
            create_ticket(ticket_subject, ticket_description, company_id, requester_id)

