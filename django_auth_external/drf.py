from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .exceptions import TokenExpired, TokenInvalid
from .middleware import _build_config
from .token import validate_token


class ExternalTokenAuthentication(BaseAuthentication):
    def __init__(self):
        self.config = _build_config()

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:]
        try:
            payload = validate_token(token, self.config)
        except TokenExpired:
            raise AuthenticationFailed("Token expired")
        except TokenInvalid:
            raise AuthenticationFailed("Invalid token")
        return (payload, token)

    def authenticate_header(self, request):
        return "Bearer"
