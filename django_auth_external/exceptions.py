class AuthExternalError(Exception):
    pass


class TokenExpired(AuthExternalError):
    pass


class TokenInvalid(AuthExternalError):
    pass


class TokenInvalidated(AuthExternalError):
    pass


class MissingClaim(AuthExternalError):
    pass


class AccessDenied(AuthExternalError):
    pass
