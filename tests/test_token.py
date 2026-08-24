import pytest

from django_auth_external import TokenConfig, generate_token, validate_token
from django_auth_external.exceptions import MissingClaim, TokenExpired, TokenInvalid


CONFIG = TokenConfig(
    secret_key="test-secret",
    claims=["user_id", "email"],
    subject_claim="user_id",
    token_ttl_seconds=3600,
)


def test_generate_token_returns_string():
    token = generate_token({"user_id": "abc", "email": "x@y.com"}, CONFIG)
    assert isinstance(token, str)


def test_validate_token_returns_payload():
    token = generate_token({"user_id": "abc", "email": "x@y.com"}, CONFIG)
    payload = validate_token(token, CONFIG)
    assert payload["user_id"] == "abc"
    assert payload["email"] == "x@y.com"


def test_generate_token_raises_on_missing_claim():
    with pytest.raises(MissingClaim):
        generate_token({"user_id": "abc"}, CONFIG)


def test_validate_token_raises_on_invalid_signature():
    token = generate_token({"user_id": "abc", "email": "x@y.com"}, CONFIG)
    bad_config = TokenConfig(
        secret_key="wrong-secret",
        claims=["user_id", "email"],
        subject_claim="user_id",
        token_ttl_seconds=3600,
    )
    with pytest.raises(TokenInvalid):
        validate_token(token, bad_config)


def test_validate_token_raises_on_expired():
    expired_config = TokenConfig(
        secret_key="test-secret",
        claims=["user_id", "email"],
        subject_claim="user_id",
        token_ttl_seconds=-1,
    )
    token = generate_token({"user_id": "abc", "email": "x@y.com"}, expired_config)
    with pytest.raises(TokenExpired):
        validate_token(token, CONFIG)
