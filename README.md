## Freshdesk Scripts Collection

A comprehensive collection of Python scripts for automating Freshdesk operations, data analysis, and workflow management.

**Note:** Scripts marked with 🖥️ have graphical user interfaces (GUI) for easier operation. To launch GUI scripts, run them with the `--gui` flag (e.g., `python script_name.py --gui`) and the interface will appear.

### 📋 Script Categories

#### 🎫 Ticket Management
- **`create_ticket.py`** 🖥️ - Creates new support tickets with customizable parameters
- **`create_test_ticket.py`** 🖥️ - Generates test tickets for development and testing
- **`create_ticket_with_attach.py`** 🖥️ - Creates tickets and immediately adds file attachments
- **`multi_ticket_create.py`** 🖥️ - Bulk creation of tickets for testing scenarios
- **`test_create_company_ticket.py`** - Creates companies and associated test tickets
- **`update_ticket_status.py`** 🖥️ - Updates ticket status values in bulk
- **`update_ticket_with_attach.py`** 🖥️ - Adds attachments to existing tickets
- **`bulk_update_internal_checkbox.py`** 🖥️ - Sets internal flags on multiple tickets
- **`delete_conversation.py`** 🖥️ - Removes all conversations from a ticket
- **`link_to_tracker.py`** 🖥️ - Links tickets to tracker tickets for organization

#### 📊 Data Retrieval & Analytics
- **`single_ticket_details_retriever.py`** - Retrieves comprehensive ticket information
- **`ticket_descriptions_exporter.py`** - Extracts ticket descriptions and metadata
- **`ticket_qa_tagger.py`** 🖥️ - Fetches ticket conversation history and adds QA tags
- **`agent_ticket_activities_analyzer.py`** - Analyzes ticket activity and timeline
- **`fetch_and_analyze_ticket_activities.py`** - SLA policy application analysis
- **`fetch_ticket_ids_by_email.py`** - Retrieves ticket IDs by email for processing
- **`fetch_ticket_requester_by_ticket_id.py`** - Retrieves ticket requester information by ticket ID
- **`fetch_tix_with_jira_id_tag.py`** - Retrieves tickets with JIRA ID tags
- **`related_tickets_by_hour.py`** - Analyzes ticket creation patterns by hour
- **`fetch_related_tickets.py`** - Exports tracker and associated ticket data
- **`ticket_creation_time_analyzer.py`** - Analyzes ticket creation time patterns

#### 🔗 Associations & Relationships
- **`associated_tickets_state_district_analyzer.py`** - Retrieves associated tickets with state/district data
- **`prime_associations_retriever.py`** - Finds primary ticket associations
- **`prime_association_tags_extractor.py`** - Extracts tags from prime associated tickets
- **`add_tags.py`** 🖥️ - Adds QA tags to tickets for organization
- **`ticket_tag_manager.py`** - GUI tool for adding/removing any tags from tickets
- **`agent_responder_ids_retriever.py`** - Identifies ticket responders and assignments
- **`assigned_agent.py`** - Analyzes agent assignment patterns

#### 🏢 Company & Contact Management
- **`fd_contact_and_domain_manager.py`** 🖥️ - Manages contacts and domain relationships
- **`contacts_with_tickets.py`** - Finds contacts associated with tickets
- **`company_name_to_id_mapper.py`** - Maps company names to IDs using fuzzy matching
- **`delete_contacts.py`** - Removes contact records from Freshdesk
- **`test_create_company_ticket.py`** - Creates companies and associated tickets

#### 🤖 Automation & Workflow
- **`fd_automation_import.py`** 🖥️ - Creates time-triggered automation rules
- **`List_All_Automations.py`** - GUI tool for exporting automation rules
- **`match_sla_policy.py`** 🖥️ - Tests SLA policy application to tickets
- **`export_sla_policies.py`** - Analyzes and exports SLA policy configurations
- **`fetch_sla_policies_to_excel.py`** - Exports SLA policies to Excel format
- **`fetch_sla_policies_with_reminders.py`** - Retrieves SLA policies with reminder settings
- **`region_updater.py`** - GUI tool for updating ticket regions and account managers
- **`unmerge_and_assign.py`** - Unmerges tickets and assigns to regional groups
- **`vip_companies_exporter.py`** - Exports VIP company information to CSV

#### 📚 Knowledge Base & Content
- **`knowledge_base_article_url_generator.py`** 🖥️ - Generates direct URLs for knowledge base articles
- **`knowledge_base_articles_exporter.py`** 🖥️ - Exports all knowledge base articles with cleaned content

#### 🛠️ Utilities & Tools
- **`merged_ticket_identifier.py`** - Identifies merged Freshdesk tickets and exports to Excel
- **`add_district.py`** - GUI tool for adding district dropdown values
- **`agent_information_retriever.py`** - Retrieves agent information and IDs
- **`fd_data_export.py`** - Downloads scheduled Freshdesk data export files
- **`fd_job_status.py`** - Checks status of scheduled export jobs
- **`export_ticket_info.py`** - Exports ticket information for reporting

#### 🧪 Testing & Development
- **`sandbox.py`** - Development sandbox for testing API configurations

### 🚀 Getting Started

1. **Setup**: Scripts are currently configured with the Support Ops API key and benchmarkeducationcompany domain - update these in each script as needed
2. **Permissions**: Ensure your API key has appropriate permissions for each operation. Your FD account will need an Admin role
3. **Installation**: Install required libraries using `pip install -r requirements.txt`
4. **Usage**: Run scripts with `python script_name.py`

### 📚 Documentation

Each script includes comprehensive documentation with:
- Detailed descriptions and use cases
- Setup instructions and requirements
- API documentation references
- Error handling and troubleshooting
- Security considerations

### 🔧 Requirements

- Python 3.x
- Required libraries: requests, pandas, openpyxl, tkinter (for GUI scripts)
- Valid Freshdesk API credentials
- Appropriate API permissions for each operation (Admin)




