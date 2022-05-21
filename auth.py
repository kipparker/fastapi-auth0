from typing import Any
import os

import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException

security = HTTPBearer()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")


def verify_token(token: str, domain: str, audience: str) -> dict[str, Any]:
    """
    Use the pyjwt jwkclient to get a signing key, then decode the supplied token
    """
    jwks_client = jwt.PyJWKClient(f"https://{domain}/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=audience,
        issuer=f"https://{domain}/",
    )


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Function that is used to validate the token in the case that it requires it
    """
    try:
        verify_token(credentials.credentials, AUTH0_DOMAIN, AUTH0_AUDIENCE)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=str(e))
