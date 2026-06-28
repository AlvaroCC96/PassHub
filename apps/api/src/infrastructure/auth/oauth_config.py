"""Google OAuth client configuration placeholder.

Credentials are sourced from `SecuritySettings.google_oauth_client_id/secret`.
No authorization-code flow is implemented yet — this module exists so the
upcoming auth module has a fixed place to wire up `authlib` or `httpx`-based
OAuth exchange without touching `core` or `domain`.
"""
