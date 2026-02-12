"""
Vercel entry point for FastAPI application.
This file is required for Vercel serverless deployment.
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import app module
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

# Vercel requires the app to be exported at module level
# This allows Vercel to import and run the FastAPI application
__all__ = ["app"]
