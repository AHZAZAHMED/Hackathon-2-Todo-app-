"""
Rate limiting routes for authentication.
Handles failed login attempt tracking and rate limit enforcement.
"""

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from app.models.rate_limit import RateLimit
from app.database import get_session


def check_rate_limit(email: str, session: Session = Depends(get_session)) -> None:
    """
    Check if the email address is rate limited.

    Enforces maximum 5 failed login attempts per email per 15 minutes.

    Args:
        email: Email address to check
        session: Database session

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    # Normalize email to lowercase
    email = email.lower()

    # Get rate limit record for this email
    statement = select(RateLimit).where(RateLimit.email == email)
    rate_limit = session.exec(statement).first()

    if rate_limit:
        # Check if currently locked
        if rate_limit.locked_until and rate_limit.locked_until > datetime.utcnow():
            # Calculate remaining lock time
            remaining_seconds = int((rate_limit.locked_until - datetime.utcnow()).total_seconds())
            remaining_minutes = max(1, (remaining_seconds + 59) // 60)  # Round up

            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Too many failed login attempts. Please try again in {remaining_minutes} minute{'s' if remaining_minutes > 1 else ''}.",
                        "retryAfter": remaining_seconds
                    }
                }
            )


def increment_failed_attempts(email: str, session: Session = Depends(get_session)) -> None:
    """
    Increment failed login attempts for an email address.

    After 5 failed attempts, locks the account for 15 minutes.

    Args:
        email: Email address
        session: Database session
    """
    # Normalize email to lowercase
    email = email.lower()

    # Get or create rate limit record
    statement = select(RateLimit).where(RateLimit.email == email)
    rate_limit = session.exec(statement).first()

    if rate_limit:
        # Increment failed attempts
        rate_limit.failed_attempts += 1
        rate_limit.last_attempt = datetime.utcnow()

        # Lock if 5 or more failed attempts
        if rate_limit.failed_attempts >= 5:
            rate_limit.locked_until = datetime.utcnow() + timedelta(minutes=15)
    else:
        # Create new rate limit record
        rate_limit = RateLimit(
            email=email,
            failed_attempts=1,
            last_attempt=datetime.utcnow(),
            locked_until=None
        )
        session.add(rate_limit)

    session.commit()


def reset_failed_attempts(email: str, session: Session = Depends(get_session)) -> None:
    """
    Reset failed login attempts for an email address.

    Called after successful login.

    Args:
        email: Email address
        session: Database session
    """
    # Normalize email to lowercase
    email = email.lower()

    # Delete rate limit record
    statement = select(RateLimit).where(RateLimit.email == email)
    rate_limit = session.exec(statement).first()

    if rate_limit:
        session.delete(rate_limit)
        session.commit()


def cleanup_expired_rate_limits(session: Session = Depends(get_session)) -> int:
    """
    Clean up expired rate limit records.

    Removes records where locked_until is more than 1 hour in the past.

    Args:
        session: Database session

    Returns:
        Number of records deleted
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=1)

    statement = select(RateLimit).where(
        RateLimit.locked_until < cutoff_time
    )
    expired_records = session.exec(statement).all()

    count = len(expired_records)
    for record in expired_records:
        session.delete(record)

    session.commit()
    return count
