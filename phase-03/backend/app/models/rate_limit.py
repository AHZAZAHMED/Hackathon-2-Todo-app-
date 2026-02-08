"""
Rate Limit model for tracking failed authentication attempts.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class RateLimit(SQLModel, table=True):
    """
    Rate Limit Tracker entity for preventing brute-force attacks.

    Tracks failed login attempts per email address.
    Enforces maximum 5 failed attempts per email per 15 minutes.
    """
    __tablename__ = "rate_limits"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, nullable=False, index=True)
    failed_attempts: int = Field(default=0, nullable=False)
    last_attempt: datetime = Field(nullable=False)
    locked_until: Optional[datetime] = Field(default=None, nullable=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "failed_attempts": 3,
                "last_attempt": "2026-02-05T12:00:00Z",
                "locked_until": None,
                "created_at": "2026-02-05T11:45:00Z"
            }
        }
