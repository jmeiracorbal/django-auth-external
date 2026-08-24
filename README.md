# django-auth-external

[![PyPI version](https://img.shields.io/pypi/v/django-auth-external.svg)](https://pypi.org/project/django-auth-external/)
[![Python](https://img.shields.io/pypi/pyversions/django-auth-external.svg)](https://pypi.org/project/django-auth-external/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/jmeiracorbal/django-auth-external/actions/workflows/tests.yml/badge.svg)](https://github.com/jmeiracorbal/django-auth-external/actions)

JWT token generation and validation for Django. Built for architectures where one service issues tokens and multiple services validate them using a shared secret.

This library handles only the cryptographic layer: signing, verification, and expiry. Session invalidation and revocation are the responsibility of the consuming application.

## install

```bash
pip install django-auth-external
```

With Django REST Framework support:

```bash
pip install django-auth-external[drf]
```

## quick start

Define the token schema in `settings.py`:

```python
AUTH_EXTERNAL = {
    "SECRET_KEY": "your-secret-key",
    "CLAIMS": ["user_id", "email", "modules"],
    "TOKEN_TTL_SECONDS": 28800,  # 8 hours
}
```

Add the middleware:

```python
MIDDLEWARE = [
    ...
    "django_auth_external.middleware.AuthExternalMiddleware",
]
```

Generate a token (in the authentication service):

```python
from django_auth_external import TokenConfig, generate_token

config = TokenConfig(secret_key="your-secret-key", claims=["user_id", "email", "modules"])
token = generate_token(
    {"user_id": "abc-123", "email": "user@example.com", "modules": ["api", "admin"]},
    config,
)
```

Validate in a view:

```python
def my_view(request):
    if request.auth_payload is None:
        return HttpResponse(status=401)
    user_id = request.auth_payload["user_id"]
    ...
```

## configuration

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `SECRET_KEY` | yes | — | Signing secret. Must be identical across all services. |
| `CLAIMS` | no | `[]` | Claim names required in the token payload. |
| `ALGORITHM` | no | `"HS256"` | JWT signing algorithm. |
| `TOKEN_TTL_SECONDS` | no | `28800` | Token lifetime in seconds (8 hours). |
| `USER_ID_CLAIM` | no | `"user_id"` | Claim name used as user identifier. |

## token generation

`generate_token` validates that the payload contains all configured claims before signing:

```python
from django_auth_external import TokenConfig, generate_token
from django_auth_external.exceptions import MissingClaim

config = TokenConfig(secret_key="secret", claims=["user_id", "email"])

generate_token({"user_id": "abc"}, config)                          # raises MissingClaim: email
generate_token({"user_id": "abc", "email": "x@y.com"}, config)     # ok
```

Extra fields in the payload are included in the token without modification.

## DRF integration

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "django_auth_external.drf.ExternalTokenAuthentication",
    ],
}
```

`request.user` will be the token payload dict. `request.auth` will be the raw token string.

## exceptions

| Exception | When |
|-----------|------|
| `TokenExpired` | Token has passed its expiry time. |
| `TokenInvalid` | Signature is wrong or token is malformed. |
| `MissingClaim` | Payload is missing a required claim during generation. |
| `AccessDenied` | General access refusal (for use in calling code). |

All inherit from `AuthExternalError`.

## license

MIT
