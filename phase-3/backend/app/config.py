"""
Configuration module for backend application.
Loads and validates environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "Please set it in your .env file. "
        "Generate one using: node -e \"console.log(require('crypto').randomBytes(32).toString('hex'))\""
    )

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters long for security. "
        f"Current length: {len(BETTER_AUTH_SECRET)}"
    )

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file with your PostgreSQL connection string."
    )

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Additional allowed origins for CORS (comma-separated)
# This allows multiple frontend URLs for different environments
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []

# Combine FRONTEND_URL with additional origins
ALL_ALLOWED_ORIGINS = [FRONTEND_URL] + [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Phase-3 Chat API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY environment variable is not set. "
        "Please set it in your .env file. "
        "Get your API key from: https://openrouter.ai/keys"
    )

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Use GPT-4 for better multi-step function calling with natural language
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4-turbo")
