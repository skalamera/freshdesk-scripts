## Freshdesk Scripts Consolidation

This folder contains curated Python scripts for interacting with the Freshdesk API. The following consolidation was performed:

- Removed scripts containing OpenAI keys and usages: `ticket_details_actions.py`, `get_conversations_with_chatgpt.py`
- Removed redundant or duplicate scripts: `merge_id_copy.py`, `delete_contacts2.py`, `fetch_ticket_activities.py`

All scripts that previously had hardcoded Freshdesk API keys were updated to use the provided key: `5TMgbcZdRFY70hSpEdj`.

### Grouped Use Cases (kept scripts)

- Ticket creation and updates: `create_ticket.py`, `create_test_ticket.py`, `create_ticket_with_attach.py`, `update_ticket_with_attach.py`, `update_ticket_status.py`, `fd_ticket_updater.py`, `match_sla_policy.py`, `internal_checkbox_updater.py`, `region_updater.py`, `multi_ticket_create.py`, `create_company_ticket.py`, `delete_conversation.py`, `link_to_tracker.py`, `test_sub_ticket_creation.py`

- Ticket retrieval, conversations, and analytics: `get_ticket_details.py`, `get_ticket_desc.py`, `get_conversations.py`, `get_ticket_activities.py`, `fetch_and_analyze_ticket_activities.py`, `fetch_ticket_requesters.py`, `fetch_ticket_ids.py`, `related_tickets_by_hour.py`, `fetch_related_tickets.py`, `get_createdat_hourofday.py`

- Associations, tags, and relationships: `get_associated_tix.py`, `get_prime_association.py`, `get_prime_assoc_tags.py`, `get_tags.py`, `add_tags.py`, `get_responder_id.py`, `assigned_agent.py`

- Contacts/companies and domain management: `fd_contact_and_domain_manager.py`, `contacts_with_tickets.py`, `get_companyid.py`, `delete_contacts.py`, `create_company_ticket.py`

- Merging/unmerging and linkage: `merge_id.py`, `unmerge_and_assign.py`, `celigo_merged.py`

- SLA policies: `export_sla_policies.py`, `fetch_sla_policies_to_excel.py`, `fetch_sla_policies_with_reminders.py`

- Data export and reporting: `fd_data_export.py`, `fd_job_status.py`, `fd_automation_import.py`, `List_All_Automations.py`, `get_article_url.py`, `get_articles.py`, `URL Extractor/app_exe.py`

- District/region automation: `add_district.py`, `add_choices_district_dropdown.py`, `update_districts_delimited.py`, `district_auto_update.py`, `region_updater.py`, `get_vip_districts.py`

- Sandbox/test: `sandbox.py`

### Notes

- Client utilities remain embedded in each script as requested (no shared module).
- Scripts that heavily overlapped were pruned to reduce duplication while preserving functionality in the remaining scripts.
- If you want further consolidation (e.g., merging conversation/ticket activity analysis), we can extend the surviving script(s) with flags/parameters.


