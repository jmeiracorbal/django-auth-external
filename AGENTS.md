# django-auth-external

## what this library does

Generates and validates JWT tokens for distributed Django services. Designed for architectures where one service issues tokens and multiple services validate them independently.

The library handles only the cryptographic layer: signing, signature verification, and expiry. Session invalidation, revocation, and event handling are the responsibility of the consuming application.

## package structure

```
django_auth_external/
  config.py        — TokenConfig dataclass
  exceptions.py    — typed exception hierarchy
  token.py         — generate_token, validate_token (pure Python, no Django)
  middleware.py    — AuthExternalMiddleware (Django)
  drf.py           — ExternalTokenAuthentication (DRF, optional)
```

The core (`token.py`, `config.py`, `exceptions.py`) has no Django dependency. Middleware and DRF integration are separate modules.

<!-- rule:claims-are-required -->
## claims are defined at config time

`TokenConfig.claims` is the contract. `generate_token` raises `MissingClaim` if the provided payload does not include every claim listed there. Do not make claims optional or add silent defaults — the caller must supply them all explicitly.

<!-- rule:no-domain-knowledge -->
## no domain knowledge

The library does not know what `user_id`, `email`, or any other claim means. Those are just strings defined in `TokenConfig.claims`. Do not add field-specific logic or special handling for specific claim names.

<!-- rule:no-invalidation -->
## token invalidation is not this library's responsibility

This library does not handle token revocation, session invalidation, or profile change events. Those are application concerns. When a profile changes, the application publishes an event (e.g. via an event bus) and each consuming service decides how to handle it. This library only answers: is this token cryptographically valid and not expired?

<!-- rule:no-redis -->
## no Redis dependency

This library has no Redis dependency and must not acquire one. Any stateful invalidation logic belongs in the consuming application or a separate utility, not here.

<!-- rule:django-settings -->
## settings contract

The library reads a single Django settings key: `AUTH_EXTERNAL` (dict). Domain values are required and raise `ImproperlyConfigured` at startup if absent. Only technical/cryptographic parameters have defaults.

Required (domain — no default):
- `SECRET_KEY`: signing secret
- `SUBJECT_CLAIM`: which JWT claim identifies the subject (e.g. `"user_id"`, `"sub"`, `"email"`)
- `TOKEN_TTL_SECONDS`: token lifetime in seconds — session policy, not a library concern

Optional (technical — defaults are reasonable):
- `CLAIMS`: list of required claims (default `[]`)
- `ALGORITHM`: signing algorithm (default `"HS256"`)

```python
AUTH_EXTERNAL = {
    "SECRET_KEY": "...",
    "SUBJECT_CLAIM": "user_id",
    "TOKEN_TTL_SECONDS": 3600,
    "CLAIMS": ["user_id", "email"],
    "ALGORITHM": "HS256",
}
```

<!-- rule:no-user-storage -->
## this library does not store users

No models, no migrations, no sessions. Token generation and validation only.
