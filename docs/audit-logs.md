# Audit Logging

Every critical action, such as authenticating, sending a DTE, or modifying configurations, triggers the creation of an `AuditLog` record.

### Schema Attributes
- `company_id` / `user_id`: Tenant context
- `entity_type` / `entity_id`: Polymorphic reference to the modified resource
- `action`: The exact event (e.g. `pdf_generated`, `emailed`)
- `previous_data` / `new_data`: JSON diff
- `ip_address` / `user_agent`: Extracted automatically from the request context

This allows for deep troubleshooting and security compliance.
