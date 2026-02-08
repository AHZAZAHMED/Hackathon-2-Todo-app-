"""
JWT verification middleware for FastAPI.
Handles authentication for protected routes.
"""

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from app.auth.utils import decode_jwt, extract_user_claims

# HTTPBearer security scheme with auto_error=False to handle missing tokens manually
security = HTTPBearer(auto_error=False)


def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and extract user claims.

    This function is used as a FastAPI dependency to protect routes.
    It extracts the JWT token from the Authorization header, verifies it,
    and returns the user claims.

    Args:
        credentials: HTTPAuthorizationCredentials from HTTPBearer security

    Returns:
        Dict containing user_id, email, and name

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    # Check if credentials are provided
    if not credentials:
        print("[AUTH] Authentication failed: Missing or invalid token")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing token"
                }
            }
        )

    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = decode_jwt(token)

        # Extract user claims
        user_claims = extract_user_claims(payload)

        return user_claims

    except jwt.ExpiredSignatureError:
        print("[AUTH] Authentication failed: Token expired")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "TOKEN_EXPIRED",
                    "message": "Token has expired. Please log in again."
                }
            }
        )
    except jwt.InvalidSignatureError:
        print("[AUTH] Authentication failed: Invalid token signature")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token signature."
                }
            }
        )
    except jwt.DecodeError:
        print("[AUTH] Authentication failed: Token decode error")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Token decode error."
                }
            }
        )
    except jwt.InvalidTokenError as e:
        print(f"[AUTH] Authentication failed: Invalid token - {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        print(f"[AUTH] Authentication failed: Token validation error - {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": f"Token validation failed: {str(e)}"
                }
            }
        )
