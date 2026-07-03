"""Audit event name constants for the public_access module.

These are string identifiers only — structlog events are logged with
`category="public_access.audit"` following the same pattern used by every
other module.  No events are dispatched yet; these constants are declared
here so presentation/service code can reference them by name without
magic strings.
"""

PUBLIC_ACCESS_CREATED = "PUBLIC_ACCESS_CREATED"
PUBLIC_ACCESS_ENABLED = "PUBLIC_ACCESS_ENABLED"
PUBLIC_ACCESS_DISABLED = "PUBLIC_ACCESS_DISABLED"
PUBLIC_TOKEN_REGENERATED = "PUBLIC_TOKEN_REGENERATED"
PUBLIC_PIN_CHANGED = "PUBLIC_PIN_CHANGED"
PUBLIC_SESSION_CREATED = "PUBLIC_SESSION_CREATED"
PUBLIC_SESSION_REVOKED = "PUBLIC_SESSION_REVOKED"
