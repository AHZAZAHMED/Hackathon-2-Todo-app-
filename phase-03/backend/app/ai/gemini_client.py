"""Gemini client configuration for OpenAI Agents SDK."""
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_gemini_client() -> AsyncOpenAI:
    """
    Create and configure AsyncOpenAI client for Gemini API via OpenRouter.

    Uses Google's Gemini 2.0 Flash model via OpenRouter's OpenAI-compatible endpoint.
    Requires GEMINI_API_KEY environment variable (OpenRouter API key).

    Returns:
        AsyncOpenAI: Configured client for Gemini API via OpenRouter

    Raises:
        ValueError: If GEMINI_API_KEY is not set
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get your API key from: https://openrouter.ai/keys"
        )

    # Configure AsyncOpenAI client with OpenRouter endpoint
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    return client


# Singleton client instance
_gemini_client = None


def get_client() -> AsyncOpenAI:
    """
    Get or create singleton Gemini client instance.

    Returns:
        AsyncOpenAI: Configured Gemini client
    """
    global _gemini_client

    if _gemini_client is None:
        _gemini_client = get_gemini_client()

    return _gemini_client
