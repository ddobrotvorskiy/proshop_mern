"""
Configuration module for ProShop Feature Flags MCP Server.

Reads settings from environment variables with sensible defaults.
Validates required settings at startup.
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for ProShop API client and MCP server."""

    # ProShop API base URL
    api_url: str
    
    # Admin credentials for authentication
    admin_email: str
    admin_password: str

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.
        
        Raises:
            RuntimeError: If required environment variables are missing.
        """
        api_url = os.environ.get("PROSHOP_API_URL", "http://localhost:5000")
        admin_email = os.environ.get("PROSHOP_ADMIN_EMAIL")
        admin_password = os.environ.get("PROSHOP_ADMIN_PASSWORD")

        if not admin_email:
            raise RuntimeError(
                "PROSHOP_ADMIN_EMAIL environment variable is required but not set."
            )

        if not admin_password:
            raise RuntimeError(
                "PROSHOP_ADMIN_PASSWORD environment variable is required but not set."
            )

        return cls(
            api_url=api_url,
            admin_email=admin_email,
            admin_password=admin_password,
        )
