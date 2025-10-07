import requests
import time
import base64

# Configuration
api_key = '5TMgbcZdRFY70hSpEdj'
domain = 'benchmarkeducationcompanysandbox'
field_id = '1067000960667'
batch_size = 2  # Further reduce batch size to minimize server load
delay_between_batches = 5  # Increase delay between batches

# Encode API key for Basic Authentication
auth_str = f'{api_key}:X'
auth_bytes = auth_str.encode('utf-8')
auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {auth_base64}'
}

# Rate limit settings
MAX_CALLS_PER_MINUTE = 700
RATE_LIMIT_RESET_TIME = 60

def handle_rate_limiting(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False

def update_custom_dropdown_field(existing_choices, new_choices):
    for i in range(0, len(new_choices), batch_size):
        batch = new_choices[i:i + batch_size]
        combined_choices = existing_choices + batch

        update_payload = {
            'choices': combined_choices
        }

        retry_count = 0
        max_retries = 3
        success = False
        
        while not success and retry_count < max_retries:
            update_response = requests.put(
                f'https://{domain}.freshdesk.com/api/v2/admin/ticket_fields/{field_id}',
                headers=headers,
                json=update_payload
            )

            if update_response.status_code == 200:
                print(f"Batch {i // batch_size + 1} updated successfully.")
                success = True
                existing_choices = combined_choices  # Update existing choices with the latest batch
            elif handle_rate_limiting(update_response):
                continue
            else:
                print(f"Failed to update batch {i // batch_size + 1}: {update_response.status_code} - {update_response.text}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying batch {i // batch_size + 1}...")
                    time.sleep(2)  # Wait before retrying

        # Sleep to respect rate limits and prevent server overload
        time.sleep(delay_between_batches)

def fetch_existing_choices():
    success = False
    while not success:
        response = requests.get(
            f'https://{domain}.freshdesk.com/api/v2/admin/ticket_fields/{field_id}',
            headers=headers
        )

        if response.status_code == 200:
            success = True
            return response.json().get('choices', [])
        elif handle_rate_limiting(response):
            continue
        else:
            raise Exception(f"Failed to fetch field: {response.status_code} - {response.text}")

def main():
    # Step 1: Fetch existing choices
    existing_choices = fetch_existing_choices()

    # Step 2: Define new choices to add
    new_choices = [f'New District {i}' for i in range(1, 2001)]  # Example new choices

    # Step 3: Update the custom dropdown field in batches
    update_custom_dropdown_field(existing_choices, new_choices)

if __name__ == "__main__":
    main()

