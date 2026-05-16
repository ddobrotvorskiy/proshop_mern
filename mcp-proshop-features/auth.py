"""
Authentication module for ProShop Feature Flags MCP Server.

Handles login, JWT token caching, and reauthentication on 401.
"""

import httpx
from config import Config


class AuthManager:
    """Manages authentication with ProShop backend."""

    _token: str | None = None
    _config: Config | None = None
    _client: httpx.AsyncClient | None = None

    @classmethod
    async def initialize(cls, config: Config, client: httpx.AsyncClient) -> None:
        """Initialize AuthManager with config and HTTP client."""
        cls._config = config
        cls._client = client
        # Pre-login on startup to fail fast if credentials are wrong
        await cls._login()

    @classmethod
    async def get_token(cls) -> str:
        """
        Get cached JWT token or login to fetch a new one.
        
        Returns:
            str: JWT token for Authorization header.
            
        Raises:
            RuntimeError: If login fails.
        """
        if cls._token:
            return cls._token
        return await cls._login()

    @classmethod
    async def _login(cls) -> str:
        """
        Login to ProShop backend and cache the JWT token.
        
        Returns:
            str: JWT token.
            
        Raises:
            RuntimeError: If login fails.
        """
        if not cls._config or not cls._client:
            raise RuntimeError("AuthManager not initialized")

        try:
            response = await cls._client.post(
                f"{cls._config.api_url}/api/users/login",
                json={
                    "email": cls._config.admin_email,
                    "password": cls._config.admin_password,
                },
            )
            response.raise_for_status()
            data = response.json()
            token = data.get("token")
            if not token:
                raise RuntimeError("Login response missing 'token' field")
            cls._token = token
            return token
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Login failed with status {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Login request failed: {e}")

    @classmethod
    async def reset_token(cls) -> None:
        """Reset cached token (used when 401 is received)."""
        cls._token = None

    @classmethod
    async def ensure_authenticated(cls) -> str:
        """
        Ensure we have a valid token, reauthenticating if needed.
        
        Returns:
            str: JWT token.
        """
        # If no token cached, get one (will login)
        if not cls._token:
            return await cls.get_token()
        return cls._token
