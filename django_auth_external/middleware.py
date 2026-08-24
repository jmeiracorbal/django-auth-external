from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from .config import TokenConfig
from .exceptions import AuthExternalError
from .token import validate_token


def _build_config() -> TokenConfig:
    cfg = getattr(django_settings, "AUTH_EXTERNAL", {})
    missing = [k for k in ("SECRET_KEY", "SUBJECT_CLAIM", "TOKEN_TTL_SECONDS") if k not in cfg]
    if missing:
        raise ImproperlyConfigured(
            f"AUTH_EXTERNAL is missing required keys: {', '.join(missing)}"
        )
    return TokenConfig(
        secret_key=cfg["SECRET_KEY"],
        subject_claim=cfg["SUBJECT_CLAIM"],
        token_ttl_seconds=cfg["TOKEN_TTL_SECONDS"],
        claims=cfg.get("CLAIMS", []),
        algorithm=cfg.get("ALGORITHM", "HS256"),
    )


class AuthExternalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.config = _build_config()

    def __call__(self, request):
        request.auth_payload = None
        token = self._extract_token(request)
        if token:
            try:
                request.auth_payload = validate_token(token, self.config)
            except AuthExternalError:
                pass
        return self.get_response(request)

    def _extract_token(self, request) -> str | None:
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if header.startswith("Bearer "):
            return header[7:]
        return None
