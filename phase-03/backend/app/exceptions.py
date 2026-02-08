"""Custom exception classes for the application."""


class GeminiAPIError(Exception):
    """Exception raised when Gemini API calls fail."""
    pass


class MCPToolError(Exception):
    """Exception raised when MCP tool execution fails."""
    pass


class ValidationError(Exception):
    """Exception raised when request validation fails."""
    pass
