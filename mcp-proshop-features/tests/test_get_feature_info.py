"""
Tests for get_feature_info tool.

Tests the happy path and error scenarios for retrieving feature information.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

from client import ProShopClient
from auth import AuthManager


def setup_mocks(mock_http_client, login_data=None, request_data=None):
    """Helper to setup mocks."""
    login_data = login_data or {"token": "test_token"}
    request_data = request_data or {}
    
    login_response = AsyncMock()
    login_response.status_code = 200
    login_response.json = MagicMock(return_value=login_data)
    login_response.raise_for_status = MagicMock()
    
    request_response = AsyncMock()
    request_response.status_code = request_data.get("status", 200)
    request_response.json = MagicMock(return_value=request_data.get("body", {}))
    request_response.text = request_data.get("text", "")
    
    mock_http_client.post.return_value = login_response
    mock_http_client.request.return_value = request_response


@pytest.mark.asyncio
async def test_get_feature_info_success(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test successful feature retrieval."""
    setup_mocks(mock_http_client, request_data={"body": feature_search_v2})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.get_feature("search_v2")
    
    assert result == feature_search_v2
    assert result["status"] == "Testing"


@pytest.mark.asyncio
async def test_get_feature_info_not_found(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test feature not found error."""
    error_body = {
        "error": "FEATURE_NOT_FOUND",
        "message": "No feature with ID 'unknown' exists in features.json.",
        "feature_id": "unknown",
    }
    setup_mocks(mock_http_client, request_data={"status": 404, "body": error_body})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.get_feature("unknown")
    
    assert result["error"] == "FEATURE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_feature_info_backend_unreachable(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test backend connection error."""
    setup_mocks(mock_http_client)
    mock_http_client.request.side_effect = httpx.ConnectError("Connection refused")
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.get_feature("search_v2")
    
    assert result["error"] == "BACKEND_UNREACHABLE"
    assert "not reachable" in result["message"]


@pytest.mark.asyncio
async def test_get_feature_info_invalid_json_response(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test handling of invalid JSON response."""
    setup_mocks(mock_http_client)
    
    response = AsyncMock()
    response.status_code = 200
    response.json = MagicMock(side_effect=ValueError("Invalid JSON"))
    response.text = "Not JSON"
    mock_http_client.request.return_value = response
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.get_feature("search_v2")
    
    assert result["error"] == "INVALID_RESPONSE"
    assert "non-JSON" in result["message"]


@pytest.mark.asyncio
async def test_get_feature_info_authorization_header(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that Authorization header is included."""
    setup_mocks(mock_http_client, request_data={"body": feature_search_v2})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    await client.get_feature("search_v2")
    
    call_kwargs = mock_http_client.request.call_args[1]
    headers = call_kwargs.get("headers", {})
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")


@pytest.mark.asyncio
async def test_get_feature_info_reauthenticate_on_401(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test reauthentication on 401 response."""
    login_response = AsyncMock()
    login_response.status_code = 200
    login_response.json = MagicMock(return_value={"token": "test_token"})
    login_response.raise_for_status = MagicMock()
    
    unauthorized = AsyncMock()
    unauthorized.status_code = 401
    
    success = AsyncMock()
    success.status_code = 200
    success.json = MagicMock(return_value=feature_search_v2)
    
    mock_http_client.post.return_value = login_response
    mock_http_client.request.side_effect = [unauthorized, success]
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.get_feature("search_v2")
    
    assert result == feature_search_v2
    assert mock_http_client.request.call_count == 2
