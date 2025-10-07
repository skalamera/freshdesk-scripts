import requests
import time

# Freshdesk API details
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/tickets"

# Headers for authentication
AUTH = (API_KEY, "X")
HEADERS = {"Content-Type": "application/json"}

# Status mapping
STATUS_MAPPING = {
    21: 8
}

MAX_RETRIES = 3  # Limit retries to prevent infinite loops

def get_tickets_with_old_statuses():
    """Fetch all tickets that have an old status from the mapping."""
    tickets_to_update = []
    page = 1

    while True:
        response = requests.get(
            BASE_URL,
            auth=AUTH,
            headers=HEADERS,
            params={"per_page": 50, "page": page}  # Fetch in batches of 50
        )

        if response.status_code != 200:
            print(f"âŒ Error fetching tickets: {response.status_code} - {response.text}")
            break

        tickets = response.json()
        if not tickets:
            break  # No more tickets to process

        for ticket in tickets:
            old_status = ticket.get("status")
            if old_status in STATUS_MAPPING:
                tickets_to_update.append((ticket["id"], old_status, STATUS_MAPPING[old_status]))

        page += 1
        time.sleep(1)  # Delay to prevent rate limits

    return tickets_to_update

def update_ticket_status(ticket_id, old_status, new_status, attempt=1):
    """Update a single ticket status based on the mapping, with retries."""
    if attempt > MAX_RETRIES:
        print(f"â— Max retries reached for ticket {ticket_id}. Skipping...")
        return "FAILED"

    url = f"{BASE_URL}/{ticket_id}"
    payload = {"status": new_status}

    try:
        response = requests.put(url, auth=AUTH, headers=HEADERS, json=payload)

        if response.status_code == 200:
            print(f"âœ… Success: Ticket {ticket_id} updated from {old_status} â†’ {new_status}")
            return "SUCCESS"
        elif response.status_code == 400:
            print(f"âŒ Failed: Ticket {ticket_id} - Bad Request (400): {response.json()}")
        elif response.status_code == 403:
            print(f"ðŸš« Failed: Ticket {ticket_id} - Permission Denied (403)")
        elif response.status_code == 404:
            print(f"ðŸ” Failed: Ticket {ticket_id} - Not Found (404)")
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"â³ Rate limit hit. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        elif response.status_code >= 500:
            print(f"âš ï¸ Failed: Ticket {ticket_id} - Server Error ({response.status_code}). Retrying in 10 seconds...")
            time.sleep(10)
            return update_ticket_status(ticket_id, old_status, new_status, attempt + 1)  # Retry
        else:
            print(f"âŒ Failed: Ticket {ticket_id} - Unexpected error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"â— Network error: {e}")

    return "FAILED"

def main():
    """Fetch tickets and update their statuses based on the mapping."""
    tickets_to_update = get_tickets_with_old_statuses()

    if not tickets_to_update:
        print("No tickets need updating.")
        return

    print(f"ðŸŽ¯ Found {len(tickets_to_update)} tickets that need status updates.")

    success_count = 0
    fail_count = 0

    for ticket_id, old_status, new_status in tickets_to_update:
        result = update_ticket_status(ticket_id, old_status, new_status)
        if result == "SUCCESS":
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5)  # Small delay to avoid rate limits

    print(f"\nâœ… Done! {success_count} tickets updated successfully, {fail_count} failed.")

if __name__ == "__main__":
    main()

