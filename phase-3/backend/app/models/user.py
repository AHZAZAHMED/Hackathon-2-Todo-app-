"""
User model for authentication system.
Managed by Better Auth on the frontend.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User entity representing an authenticated user account.

    This table is managed by Better Auth on the frontend.
    Backend only reads from this table for JWT verification.

    Schema matches Better Auth's actual database schema.
    """
    __tablename__ = "user"  # Better Auth uses singular "user" table name

    # Better Auth uses TEXT for id, not integer
    id: str = Field(primary_key=True)
    email: str = Field(nullable=False, index=True)
    emailVerified: bool = Field(default=False, nullable=False)
    name: str = Field(nullable=False)
    createdAt: datetime = Field(nullable=False)
    updatedAt: datetime = Field(nullable=False)
    image: Optional[str] = Field(default=None, nullable=True)
    banned: bool = Field(default=False, nullable=False)
    banReason: Optional[str] = Field(default=None, nullable=True)
    banExpires: Optional[int] = Field(default=None, nullable=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "clx1234567890",
                "name": "John Doe",
                "email": "john@example.com",
                "emailVerified": False,
                "createdAt": "2026-02-05T00:00:00Z",
                "updatedAt": "2026-02-05T00:00:00Z",
                "image": None,
                "banned": False,
                "banReason": None,
                "banExpires": None
            }
        }
