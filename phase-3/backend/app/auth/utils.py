"""
JWT verification utilities.
Handles JWT token decoding and validation.
"""

import jwt
from datetime import datetime
from typing import Dict, Any
from app.config import BETTER_AUTH_SECRET, JWT_ALGORITHM


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and verify JWT token.

    Args:
        token: JWT token string

    Returns:
        Dict containing decoded token payload with user claims

    Raises:
        jwt.InvalidSignatureError: If token signature is invalid
        jwt.ExpiredSignatureError: If token has expired
        jwt.DecodeError: If token cannot be decoded
        jwt.InvalidTokenError: For other token validation errors
    """
    try:
        # Decode and verify token signature
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        # Validate expiration (exp claim)
        exp = payload.get("exp")
        if not exp:
            raise jwt.InvalidTokenError("Token missing expiration claim")

        if datetime.fromtimestamp(exp) < datetime.now():
            raise jwt.ExpiredSignatureError("Token has expired")

        # Validate issued-at (iat claim)
        iat = payload.get("iat")
        if not iat:
            raise jwt.InvalidTokenError("Token missing issued-at claim")

        if datetime.fromtimestamp(iat) > datetime.now():
            raise jwt.InvalidTokenError("Token issued in the future")

        # Validate required claims
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id:
            raise jwt.InvalidTokenError("Token missing user_id claim")
        if not email:
            raise jwt.InvalidTokenError("Token missing email claim")

        return payload

    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidSignatureError:
        raise
    except jwt.DecodeError:
        raise
    except jwt.InvalidTokenError:
        raise
    except Exception as e:
        raise jwt.InvalidTokenError(f"Token validation failed: {str(e)}")


def extract_user_claims(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user claims from decoded JWT payload.

    Args:
        payload: Decoded JWT payload

    Returns:
        Dict containing user_id, email, and name
    """
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }
