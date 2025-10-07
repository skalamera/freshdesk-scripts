import requests
import time
import pandas as pd

# Freshdesk API Details
API_KEY = "5TMgbcZdRFY70hSpEdj"
FRESHDESK_DOMAIN = "benchmarkeducationcompany.freshdesk.com"
HEADERS = {
    "Content-Type": "application/json"
}

# List of tracker ticket IDs
tracker_ticket_ids = [
    3365, 
4948, 
9793, 
57132, 
57186, 
70115, 
73457, 
83834, 
90414, 
93633, 
174332, 
193030, 
197708, 
200282, 
200283, 
201086, 
201456, 
201807, 
201934, 
203521, 
204477, 
222900, 
226344, 
229534, 
229843, 
232223, 
235746, 
235835, 
236086, 
236508, 
236979, 
238704, 
239314, 
240609, 
240828, 
241051, 
242101, 
242666, 
243190, 
244211, 
244272, 
244740, 
245280, 
245391, 
246765, 
248650, 
248872, 
249052, 
253317, 
255515, 
255678, 
259464, 
259594, 
259694, 
264708, 
265183, 
268554, 
270771, 
272028, 
273582, 
273986, 
274150, 
275282, 
275308, 
275336, 
275717, 
275901, 
275937, 
276088, 
276411, 
276555, 
276572, 
276635, 
276758, 
277233, 
280920, 
280924, 
281375, 
281731, 
282259, 
282616, 
282919, 
282920, 
282921, 
283191, 
283586, 
283598, 
283610, 
283827, 
283862, 
283904, 
283937, 
283958, 
284387, 
284474, 
284540, 
284660, 
284759, 
284999, 
285101, 
285296, 
285360, 
285373, 
285488, 
285575, 
285874, 
285953, 
286096, 
286146, 
286290, 
286294, 
286349, 
286364, 
286596, 
286646, 
286658, 
286802, 
287266, 
287271, 
287671, 
287681, 
287792, 
287941, 
287983, 
287997, 
287998, 
288059, 
288088, 
288102, 
288281, 
288377, 
288393, 
288598, 
288917, 
288941, 
288945, 
288968, 
289157, 
289269, 
289275, 
289335, 
289483, 
289496, 
289522, 
289583, 
289616, 
289633, 
289657, 
289752, 
289787, 
289801, 
289824, 
289901, 
290037, 
290148, 
290219, 
290220, 
291332, 
292656, 
292685, 
292690, 
292694, 
292968, 
293220, 
293322, 
293327, 
293333, 
293393, 
293496, 
293536, 
293539, 
293547, 
293574, 
293664, 
293706, 
293731, 
293787, 
293800, 
293891, 
293946, 
294012, 
294014, 
294175, 
294262, 
294279, 
294287, 
294367, 
294377, 
294437, 
294443, 
294556, 
294621, 
294720, 
294737, 
294762, 
294763, 
294774, 
294805, 
294821, 
294863, 
294868, 
295038, 
295042, 
295098, 
295172, 
295173, 
295182, 
295245, 
295317, 
295372, 
295396, 
295442, 
295444, 
295453, 
295533, 
295581, 
295597, 
295610, 
295614, 
295615, 
295657, 
295667, 
295679, 
295766, 
295772, 
295808, 
295928, 
295994, 
296002, 
296017, 
296026, 
296041, 
296043, 
296053, 
296112, 
296129, 
296136, 
296139, 
296206, 
296232, 
296241, 
296273, 
296362, 
296394, 
296404, 
296412, 
296440, 
296480, 
296496, 
296588, 
296593, 
296610, 
296632, 
296633, 
296636, 
296644, 
296673, 
296679, 
296686, 
296697, 
296747, 
296786, 
296793, 
296796, 
296803, 
296889, 
296981, 
296985, 
297039, 
297048, 
297049, 
297061, 
297071, 
297080, 
297101, 
297145, 
297150, 
297158, 
297170, 
297181
]

# Function to fetch associated tickets
def fetch_associated_tickets(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    print(f"Fetching associated tickets for Tracker Ticket ID: {ticket_id}...")

    response = requests.get(url, auth=(API_KEY, "X"), headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        associated_tickets = data.get("associated_tickets_list", [])
        print(f"  âœ… Found {len(associated_tickets)} associated tickets for {ticket_id}.")
        return associated_tickets
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"  âš ï¸ Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_associated_tickets(ticket_id)
    else:
        print(f"  âŒ Error {response.status_code}: Unable to fetch data for {ticket_id}")
        return []

# Function to fetch company_id and district from a ticket
def fetch_ticket_details(ticket_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    print(f"  ðŸ” Fetching company ID and district for Associated Ticket ID: {ticket_id}...")

    response = requests.get(url, auth=(API_KEY, "X"), headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        company_id = data.get("company_id")
        district = data.get("custom_fields", {}).get("cf_district509811", "Unknown")
        
        # Ensure district is a string
        district = str(district) if district is not None else "Unknown"

        if company_id:
            print(f"    âœ… Company ID {company_id} found for Ticket {ticket_id}.")
        else:
            print(f"    âš ï¸ No company ID found for Ticket {ticket_id}.")

        print(f"    ðŸ« District: {district}")

        return company_id, district
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"  âš ï¸ Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_ticket_details(ticket_id)
    else:
        print(f"  âŒ Error {response.status_code}: Unable to fetch details for {ticket_id}")
        return None, "Unknown"

# Function to fetch state from a company
def fetch_company_state(company_id):
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies/{company_id}"
    print(f"    ðŸŒ Fetching State for Company ID: {company_id}...")

    response = requests.get(url, auth=(API_KEY, "X"), headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        state = data.get("custom_fields", {}).get("state", "Unknown")

        # Ensure state is a string
        state = str(state) if state is not None else "Unknown"

        print(f"      âœ… State '{state}' retrieved for Company ID {company_id}.")
        return state
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"    âš ï¸ Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_company_state(company_id)
    else:
        print(f"    âŒ Error {response.status_code}: Unable to fetch state for Company ID {company_id}")
        return "Unknown"

# Fetch associated tickets for each tracker
results = []
total_tickets = len(tracker_ticket_ids)

print("\nðŸš€ Starting data retrieval...\n")
for index, tracker_ticket_id in enumerate(tracker_ticket_ids, start=1):
    print(f"ðŸ”¹ Processing {index}/{total_tickets}: Tracker Ticket ID {tracker_ticket_id}")
    
    associated_tickets = fetch_associated_tickets(tracker_ticket_id)
    states = []
    districts = []

    for associated_ticket in associated_tickets:
        company_id, district = fetch_ticket_details(associated_ticket)

        if company_id:
            state = fetch_company_state(company_id)
        else:
            state = "No Company"

        states.append(state)
        districts.append(district)

        # Respect rate limits
        time.sleep(0.1)

    # Ensure all values are strings to avoid TypeError
    states = [str(s) if s is not None else "Unknown" for s in states]
    districts = [str(d) if d is not None else "Unknown" for d in districts]

    results.append({
        "Tracker Ticket ID": tracker_ticket_id,
        "Associated Tickets": ", ".join(map(str, associated_tickets)) if associated_tickets else "None",
        "States": ", ".join(states) if states else "No Associated Tickets",
        "Districts": ", ".join(districts) if districts else "No Associated Tickets"
    })

    # Respect rate limits
    time.sleep(0.1)

print("\nâœ… Data retrieval completed. Preparing to export...\n")

# Save to Excel
df = pd.DataFrame(results)
output_file = "associated_tickets_with_states_and_districts.xlsx"
df.to_excel(output_file, index=False)

print(f"âœ… Data successfully exported to {output_file}\n")

