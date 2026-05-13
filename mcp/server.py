#!/usr/bin/env python3
"""
ProShop Feature Flags MCP Server.

Exposes three tools for managing feature flags via the ProShop API:
- get_feature_info: Retrieve feature state
- set_feature_state: Change feature status (Disabled/Testing/Enabled)
- adjust_traffic_rollout: Modify traffic percentage for Testing features

Transport: stdio (for use with Claude Desktop or MCP CLI)
"""

import asyncio
import httpx
import anyio
from fastmcp import FastMCP

from config import Config
from auth import AuthManager
from client import ProShopClient


# Initialize FastMCP server
mcp = FastMCP("proshop-feature-flags")

# Global client instance
_client: ProShopClient | None = None


async def _get_client() -> ProShopClient:
    """Get or initialize the API client."""
    global _client
    if _client is None:
        raise RuntimeError("Client not initialized. Server startup failed.")
    return _client


@mcp.tool()
async def get_feature_info(feature_id: str) -> dict:
    """
    Retrieve the complete current state of a single feature flag.
    
    Args:
        feature_id: The snake_case key of the feature (e.g., "search_v2")
        
    Returns:
        Feature object with all fields, or error object if not found.
        
    Example:
        >>> await get_feature_info("dark_mode")
        {
            "feature_id": "dark_mode",
            "name": "Dark Mode Theme",
            "status": "Testing",
            "traffic_percentage": 20,
            "last_modified": "2026-04-20",
            ...
        }
    """
    client = await _get_client()
    return await client.get_feature(feature_id)


@mcp.tool()
async def set_feature_state(feature_id: str, state: str) -> dict:
    """
    Change the status of a feature flag.
    
    Automatically adjusts traffic_percentage to the canonical value for the new state:
    - Disabled: traffic_percentage → 0
    - Testing: traffic_percentage → unchanged if 1-99, else 10
    - Enabled: traffic_percentage → 100
    
    Also updates last_modified to today's date.
    Checks dependencies and includes warnings if any are not Enabled.
    
    Args:
        feature_id: The snake_case key of the feature
        state: Target state - must be exactly "Disabled", "Testing", or "Enabled"
        
    Returns:
        Updated feature object with warnings array if applicable, or error object.
        
    Raises:
        ValueError: If state is not one of the three valid values (validated before API call).
        
    Example:
        >>> await set_feature_state("dark_mode", "Enabled")
        {
            "feature_id": "dark_mode",
            "status": "Enabled",
            "traffic_percentage": 100,
            "last_modified": "2026-04-27",
            ...
        }
    """
    # Validate state before making API call
    valid_states = {"Disabled", "Testing", "Enabled"}
    if state not in valid_states:
        return {
            "error": "INVALID_STATE",
            "message": f"State '{state}' is not valid. Must be one of: Disabled, Testing, Enabled (case-sensitive).",
            "feature_id": feature_id,
        }
    
    client = await _get_client()
    return await client.set_feature_state(feature_id, state)


@mcp.tool()
async def adjust_traffic_rollout(feature_id: str, percentage: int) -> dict:
    """
    Change the traffic_percentage of a feature that is currently in Testing state.
    
    Does not change the status. Only works if status is "Testing".
    Updates last_modified to today's date.
    
    Validation rules:
    - percentage must be an integer (no decimals)
    - percentage must be in range 0-100
    - feature must have status "Testing" (validated before API call)
    
    Side effects:
    - If percentage is 0, response includes hint to use set_feature_state instead
    - If percentage is 100, response includes hint to promote to Enabled
    
    Args:
        feature_id: The snake_case key of the feature
        percentage: Target traffic percentage as integer (0-100)
        
    Returns:
        Updated feature object with hint if applicable, or error object.
        
    Raises:
        ValueError: If percentage is not a valid integer in 0-100 range.
        
    Example:
        >>> await adjust_traffic_rollout("search_v2", 50)
        {
            "feature_id": "search_v2",
            "status": "Testing",
            "traffic_percentage": 50,
            "last_modified": "2026-04-27",
            "hint": null
        }
    """
    # Validate percentage before making API call
    if not isinstance(percentage, int) or percentage < 0 or percentage > 100:
        return {
            "error": "INVALID_PERCENTAGE",
            "message": f"percentage must be an integer from 0 to 100, got {percentage}",
            "feature_id": feature_id,
        }
    
    client = await _get_client()
    return await client.adjust_traffic_rollout(feature_id, percentage)


async def _initialize_and_run() -> None:
    """Initialize client and run MCP server."""
    global _client
    
    config = Config.from_env()
    
    async with httpx.AsyncClient() as http_client:
        await AuthManager.initialize(config, http_client)
        _client = ProShopClient(config, http_client)
        
        # Run MCP server using anyio to avoid event loop conflicts
        def sync_run():
            mcp.run()
        
        await anyio.to_thread.run_sync(sync_run)


def main() -> None:
    """Initialize server and start listening."""
    try:
        anyio.run(_initialize_and_run)
    except RuntimeError as e:
        print(f"Startup failed: {e}", flush=True)
        raise
    except KeyboardInterrupt:
        print("Shutting down...", flush=True)


if __name__ == "__main__":
    main()
