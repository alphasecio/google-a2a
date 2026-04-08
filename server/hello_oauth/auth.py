"""
JWT validation via OIDC discovery.
Initialised once at import time — fails fast if env vars are missing.
"""
import contextvars
import json
import os
import urllib.request

import jwt
from jwt import PyJWKClient

OAUTH_AUDIENCE: str = os.environ.get("OAUTH_AUDIENCE", "")
OAUTH_ISSUER: str = os.environ.get("OAUTH_ISSUER", "")

if not OAUTH_AUDIENCE or not OAUTH_ISSUER:
    raise RuntimeError(
        "OAUTH_AUDIENCE and OAUTH_ISSUER environment variables must be set."
    )

def _build_jwks_client() -> PyJWKClient:
    issuer = OAUTH_ISSUER.rstrip("/")
    try:
        with urllib.request.urlopen(f"{issuer}/.well-known/openid-configuration") as r:
            jwks_uri = json.loads(r.read()).get("jwks_uri")
        if not jwks_uri:
            raise ValueError("jwks_uri missing from OIDC discovery document")
    except Exception:
        # Fallback for providers that skip discovery (e.g. non-standard issuers)
        jwks_uri = f"{issuer}/.well-known/jwks.json"
    return PyJWKClient(jwks_uri)


_jwks_client: PyJWKClient = _build_jwks_client()

auth_token_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "auth_token", default=""
)

def validate_jwt(token: str) -> dict:
    """Validates a Bearer JWT. Raises jwt.PyJWTError on any failure."""
    signing_key = _jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=OAUTH_AUDIENCE,
        issuer=OAUTH_ISSUER,
    )
