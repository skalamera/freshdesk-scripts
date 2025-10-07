import requests

# Constants
API_KEY = "5TMgbcZdRFY70hSpEdj"
DOMAIN = "benchmarkeducationcompany.freshdesk.com"
BASE_URL = f"https://{DOMAIN}/api/v2/agents"

def get_agents():
    headers = {
        "Content-Type": "application/json"
    }
    try:
        agents = []
        page = 1

        while True:
            response = requests.get(
                f"{BASE_URL}?page={page}",
                auth=(API_KEY, "X"),
                headers=headers
            )

            # Handle rate limits
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"Rate limit reached. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()  # Raise error for bad status codes
            data = response.json()

            # Break if no more agents
            if not data:
                break

            # Append agents to the list
            agents.extend(data)
            page += 1

        # Print agents and responder IDs
        for agent in agents:
            print(f"Name: {agent['contact']['name']}, Responder ID: {agent['id']}")
        
        return agents

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Run the function
if __name__ == "__main__":
    get_agents()

