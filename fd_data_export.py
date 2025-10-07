import requests
import base64
import os

# Step 1: Freshdesk API URL
freshdesk_api_url = "https://benchmarkeducationcompany.freshdesk.com/reports/omni_schedule/download_file.json?uuid=89c6af78-f312-4cdc-81c1-39d92a436dcf"
api_key = "5TMgbcZdRFY70hSpEdj"  # Freshdesk API key

# Properly format the Authorization header
auth_string = f"{api_key}:X"  # Append ':X' as required for Basic Auth
auth_header = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# Step 2: Make API Request
response = requests.get(freshdesk_api_url, headers=headers)

if response.status_code == 200:
    try:
        data = response.json()
        print("JSON Response:", data)  # Debug: Print the full response
        if "export" in data and "url" in data["export"]:
            s3_url = data["export"]["url"]  # Extract the S3 URL
            
            # Step 3: Download the CSV file from the S3 URL
            csv_response = requests.get(s3_url)
            if csv_response.status_code == 200:
                # Step 4: Save the file to the specified OneDrive folder
                onedrive_path = r"C:\Users\skala\OneDrive - Benchmark Education"  # Specified OneDrive folder path
                file_name = "freshdesk_export.csv"
                file_path = os.path.join(onedrive_path, file_name)
                
                with open(file_path, "wb") as file:
                    file.write(csv_response.content)
                
                print(f"CSV file successfully downloaded and saved to {file_path}")
            else:
                print(f"Failed to download CSV file. Status code: {csv_response.status_code}")
        else:
            print("The JSON response does not contain the expected 'export' key or 'url' field.")
    except ValueError as e:
        print("Failed to parse JSON response:", e)
else:
    print(f"Failed to fetch data from Freshdesk API. Status code: {response.status_code}")

