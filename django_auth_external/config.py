from dataclasses import dataclass


@dataclass
class TokenConfig:
    secret_key: str
    claims: list[str]
    subject_claim: str
    token_ttl_seconds: int
    algorithm: str = "HS256"
