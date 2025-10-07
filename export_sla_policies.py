import requests
import json

# Define API credentials and endpoints
api_key = "5TMgbcZdRFY70hSpEdj"
production_domain = "benchmarkeducationcompany.freshdesk.com"
headers = {
    "Content-Type": "application/json"
}

# Function to get all SLA policies
def get_sla_policies():
    url = f"https://{production_domain}/api/v2/sla_policies"
    response = requests.get(url, auth=(api_key, "X"), headers=headers)
    
    if response.status_code == 200:
        sla_policies = response.json()
        print(f"Successfully retrieved {len(sla_policies)} SLA policies.")
        return sla_policies
    else:
        print("Failed to retrieve SLA policies:", response.status_code, response.text)
        return []

# Function to print SLA policy details to the console with targets and escalation
def print_sla_policies(sla_policies):
    for policy in sla_policies:
        if policy["name"] in ["Default Service Request SLA", "Default Incident & End User Request SLA"]:
            print(f"SLA Policy Name: {policy['name']}")
            print(f"Description: {policy.get('description', 'No description')}")
            print(f"Default: {policy.get('is_default', 'Not specified')}")
            print(f"Created At: {policy['created_at']}")
            print(f"Updated At: {policy['updated_at']}")
            print("Targets:")

            sla_target = policy.get("sla_target", {})
            if sla_target:
                for priority, target in sla_target.items():
                    print(f"  - Priority: {priority}")
                    print(f"    Respond Within: {target.get('respond_within', 'N/A')} seconds")
                    print(f"    Resolve Within: {target.get('resolve_within', 'N/A')} seconds")
                    print(f"    Business Hours: {target.get('business_hours', 'N/A')}")
                    print(f"    Escalation Enabled: {target.get('escalation_enabled', 'N/A')}")
            else:
                print("  No SLA targets found.")

            escalation = policy.get("escalation", {})
            if escalation:
                print("Escalation:")
                response_escalation = escalation.get("response", {})
                if response_escalation:
                    print(f"  Response Escalation Time: {response_escalation.get('escalation_time', 'N/A')} seconds")
                    print(f"  Agents: {', '.join(map(str, response_escalation.get('agent_ids', [])))}")
                else:
                    print("  No response escalation details found.")

                resolution_escalation = escalation.get("resolution", {})
                if resolution_escalation:
                    for level, level_data in resolution_escalation.items():
                        print(f"  - {level.capitalize()} Resolution Escalation Time: {level_data.get('escalation_time', 'N/A')} seconds")
                        print(f"    Agents: {', '.join(map(str, level_data.get('agent_ids', [])))}")
                else:
                    print("  No resolution escalation details found.")
            else:
                print("  No escalation details found.")
            
            print("-" * 50)

# Main execution
if __name__ == "__main__":
    sla_policies = get_sla_policies()
    if sla_policies:
        print_sla_policies(sla_policies)

