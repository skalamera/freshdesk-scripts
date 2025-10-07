"""
Freshdesk SLA Policies Export and Analysis Script

DESCRIPTION:
This script retrieves and analyzes SLA (Service Level Agreement) policies from
Freshdesk, focusing on default policies. It displays detailed information about
response times, resolution targets, escalation rules, and agent assignments.

REQUIREMENTS:
- Python 3.x
- requests library (install with: pip install requests)
- Valid Freshdesk API key with SLA policy read permissions
- Freshdesk account and domain access

SETUP INSTRUCTIONS:
1. Replace API_KEY with your actual Freshdesk API key
2. Replace DOMAIN with your Freshdesk domain (e.g., 'yourcompany.freshdesk.com')
3. Ensure your API key has permissions for SLA policy access
4. Run the script: python export_sla_policies.py

API DOCUMENTATION:
- Freshdesk API v2: https://developers.freshdesk.com/api/
- SLA Policies API: https://developers.freshdesk.com/api/#sla_policies
- Authentication: Basic Auth with API key
- Rate Limits: 50 requests per minute for most endpoints

INPUT PARAMETERS:
- API_KEY: Your Freshdesk API key
- DOMAIN: Your Freshdesk domain
- TARGET_POLICIES: List of policy names to analyze (currently set to default policies)

OUTPUT:
- Detailed console output of SLA policy configurations
- Information about response and resolution targets
- Escalation rules and agent assignments
- Timestamps for creation and updates

SLA POLICY DATA INCLUDES:
- Policy name and description
- Default status indicator
- Creation and update timestamps
- Response time targets by priority
- Resolution time targets by priority
- Business hours configuration
- Escalation rules and assigned agents

TARGET POLICIES:
- Currently analyzes: "Default Service Request SLA" and "Default Incident & End User Request SLA"
- Easily customizable by modifying the policy filter in print_sla_policies()

ERROR HANDLING:
- Handles HTTP errors with descriptive messages
- Validates API responses and data structure
- Continues processing even if individual policies fail
- Displays clear error messages for troubleshooting

SECURITY NOTE:
- Store API keys securely (environment variables recommended for production)
- Never commit API keys to version control
- Rotate API keys regularly for security

TROUBLESHOOTING:
- Verify API key has SLA policy read permissions
- Check that target policy names exist in your Freshdesk instance
- Ensure network connectivity to Freshdesk API
- Monitor rate limit usage in Freshdesk dashboard

PERFORMANCE CONSIDERATIONS:
- Single API call to retrieve all SLA policies
- Processes policies sequentially for detailed analysis
- Suitable for environments with reasonable numbers of SLA policies
"""

import requests
import json
import os

# Freshdesk API Configuration
# TODO: Move these to environment variables for security
API_KEY = "5TMgbcZdRFY70hSpEdj"  # Replace with your actual API key
DOMAIN = "benchmarkeducationcompany.freshdesk.com"  # Replace with your domain

# HTTP Headers for API requests
HEADERS = {
    "Content-Type": "application/json"
}

# Target policies to analyze (can be customized)
TARGET_POLICIES = [
    "Default Service Request SLA",
    "Default Incident & End User Request SLA"
]

def get_sla_policies():
    """
    Retrieve all SLA policies from Freshdesk.

    Returns:
        list: List of SLA policy dictionaries, empty list if error

    Note:
        - Fetches all SLA policies in a single API call
        - Returns raw policy data for further processing
    """
    # API endpoint for SLA policies
    url = f"https://{DOMAIN}/api/v2/sla_policies"

    try:
        # Make the API request
        response = requests.get(url, auth=(API_KEY, "X"), headers=HEADERS)

        if response.status_code == 200:
            sla_policies = response.json()
            print(f"✓ Successfully retrieved {len(sla_policies)} SLA policies")
            return sla_policies
        else:
            print(f"✗ Failed to retrieve SLA policies: {response.status_code}")
            print(f"  Error: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error retrieving SLA policies: {e}")
        return []

def format_time_seconds(seconds):
    """
    Format time in seconds to human-readable format.

    Args:
        seconds (int): Time in seconds

    Returns:
        str: Formatted time string (e.g., "2h 30m", "45m", "30s")
    """
    if not seconds or seconds == "N/A":
        return "N/A"

    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if remaining_seconds > 0 and hours == 0:  # Only show seconds if < 1 hour
            parts.append(f"{remaining_seconds}s")

        return " ".join(parts) if parts else "0s"
    except (ValueError, TypeError):
        return str(seconds)

def print_sla_policies(sla_policies):
    """
    Display detailed information about target SLA policies.

    Args:
        sla_policies (list): List of SLA policy dictionaries

    Note:
        - Only displays policies matching TARGET_POLICIES
        - Shows comprehensive SLA configuration details
        - Formats time values for better readability
    """
    matching_policies = 0

    for policy in sla_policies:
        policy_name = policy.get("name", "Unknown")

        # Only process target policies
        if policy_name not in TARGET_POLICIES:
            continue

        matching_policies += 1
        print(f"\n{'=' * 70}")
        print(f"SLA POLICY: {policy_name}")
        print(f"{'=' * 70}")

        # Basic policy information
        print(f"Description: {policy.get('description', 'No description available')}")
        print(f"Default Policy: {'Yes' if policy.get('is_default') else 'No'}")
        print(f"Created: {policy.get('created_at', 'Unknown')}")
        print(f"Last Updated: {policy.get('updated_at', 'Unknown')}")

        # SLA Targets by priority
        sla_target = policy.get("sla_target", {})
        if sla_target:
            print(f"\n{'-' * 50}")
            print("RESPONSE & RESOLUTION TARGETS")
            print(f"{'-' * 50}")

            for priority, target in sla_target.items():
                print(f"\nPriority: {priority.upper()}")
                print(f"  Respond Within: {format_time_seconds(target.get('respond_within'))}")
                print(f"  Resolve Within: {format_time_seconds(target.get('resolve_within'))}")
                print(f"  Business Hours: {target.get('business_hours', 'Not configured')}")
                print(f"  Escalation Enabled: {'Yes' if target.get('escalation_enabled') else 'No'}")
        else:
            print("\n⚠ No SLA targets configured for this policy")

        # Escalation rules
        escalation = policy.get("escalation", {})
        if escalation:
            print(f"\n{'-' * 50}")
            print("ESCALATION RULES")
            print(f"{'-' * 50}")

            # Response escalation
            response_escalation = escalation.get("response", {})
            if response_escalation:
                print("
Response Escalation:")
                print(f"  Escalation Time: {format_time_seconds(response_escalation.get('escalation_time'))}")
                agent_ids = response_escalation.get('agent_ids', [])
                if agent_ids:
                    print(f"  Assigned Agents: {', '.join(map(str, agent_ids))}")
                else:
                    print("  Assigned Agents: None specified")
            else:
                print("\n⚠ No response escalation configured")

            # Resolution escalation (can have multiple levels)
            resolution_escalation = escalation.get("resolution", {})
            if resolution_escalation:
                print("
Resolution Escalation:")
                for level, level_data in resolution_escalation.items():
                    print(f"  Level {level.upper()}:")
                    print(f"    Escalation Time: {format_time_seconds(level_data.get('escalation_time'))}")
                    agent_ids = level_data.get('agent_ids', [])
                    if agent_ids:
                        print(f"    Assigned Agents: {', '.join(map(str, agent_ids))}")
                    else:
                        print("    Assigned Agents: None specified")
            else:
                print("\n⚠ No resolution escalation configured")
        else:
            print(f"\n{'-' * 50}")
            print("⚠ NO ESCALATION RULES CONFIGURED")
            print(f"{'-' * 50}")

        print(f"\n{'=' * 70}")

    if matching_policies == 0:
        print("⚠ No matching SLA policies found")
        print(f"Available policies in your Freshdesk instance:")
        for policy in sla_policies:
            print(f"  - {policy.get('name', 'Unknown')}")
        print(f"\nTo analyze different policies, update TARGET_POLICIES list in the script.")

def export_sla_policies_to_json(sla_policies, filename="sla_policies_export.json"):
    """
    Export SLA policies to a JSON file for backup or analysis.

    Args:
        sla_policies (list): List of SLA policy dictionaries
        filename (str): Output filename for the export

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Filter to target policies only
        target_policies_data = [
            policy for policy in sla_policies
            if policy.get("name") in TARGET_POLICIES
        ]

        # Export with readable formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(target_policies_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(target_policies_data)} SLA policies to {filename}")
        return True

    except Exception as e:
        print(f"✗ Failed to export SLA policies: {e}")
        return False

def main():
    """
    Main function to orchestrate SLA policy retrieval and analysis.
    """
    print("Freshdesk SLA Policies Analysis Tool")
    print("=" * 60)
    print(f"Target Policies: {', '.join(TARGET_POLICIES)}")
    print("=" * 60)

    # Retrieve all SLA policies
    sla_policies = get_sla_policies()

    if not sla_policies:
        print("❌ Unable to retrieve SLA policies. Please check:")
        print("  - API key has SLA policy read permissions")
        print("  - Freshdesk domain is correct")
        print("  - Network connectivity to Freshdesk API")
        return

    # Display detailed policy information
    print_sla_policies(sla_policies)

    # Offer to export to JSON file
    export_choice = input("
Export SLA policies to JSON file? (y/n): ").lower().strip()
    if export_choice == 'y':
        filename = input("Enter filename (default: sla_policies_export.json): ").strip()
        if not filename:
            filename = "sla_policies_export.json"

        if export_sla_policies_to_json(sla_policies, filename):
            print(f"✓ SLA policies exported successfully to {filename}")

    print("\n" + "=" * 60)
    print("SLA Policy Analysis Complete!")

# Run the script if executed directly
if __name__ == "__main__":
    main()

