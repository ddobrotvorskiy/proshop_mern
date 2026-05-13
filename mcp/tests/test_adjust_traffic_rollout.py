"""
Tests for adjust_traffic_rollout tool.

Tests traffic percentage adjustments, validation, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from client import ProShopClient
from auth import AuthManager


def setup_mocks(mock_http_client, request_data=None):
    """Helper to setup mocks."""
    request_data = request_data or {}
    
    login_response = AsyncMock()
    login_response.status_code = 200
    login_response.json = MagicMock(return_value={"token": "test_token"})
    login_response.raise_for_status = MagicMock()
    
    request_response = AsyncMock()
    request_response.status_code = request_data.get("status", 200)
    request_response.json = MagicMock(return_value=request_data.get("body", {}))
    
    mock_http_client.post.return_value = login_response
    mock_http_client.request.return_value = request_response


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_success(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test successful traffic percentage adjustment."""
    updated = {**feature_search_v2, "traffic_percentage": 50}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("search_v2", 50)
    
    assert result["traffic_percentage"] == 50
    assert result["status"] == "Testing"


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_to_zero(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test adjusting traffic to 0%."""
    updated = {
        **feature_search_v2,
        "traffic_percentage": 0,
        "hint": "Traffic is now 0%. Consider using set_feature_state.",
    }
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("search_v2", 0)
    
    assert result["traffic_percentage"] == 0
    assert "hint" in result


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_to_100(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test adjusting traffic to 100%."""
    updated = {
        **feature_search_v2,
        "traffic_percentage": 100,
        "hint": "Traffic is now 100%. Consider using set_feature_state.",
    }
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("search_v2", 100)
    
    assert result["traffic_percentage"] == 100
    assert "hint" in result


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_wrong_status(
    config,
    mock_http_client: AsyncMock,
    feature_paypal_enabled: dict,
) -> None:
    """Test error for non-Testing feature."""
    error = {
        "error": "WRONG_STATUS_FOR_ROLLOUT",
        "message": "Feature is currently 'Enabled'.",
        "feature_id": "paypal_express_buttons",
    }
    setup_mocks(mock_http_client, request_data={"status": 400, "body": error})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("paypal_express_buttons", 50)
    
    assert result["error"] == "WRONG_STATUS_FOR_ROLLOUT"


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_feature_not_found(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test error when feature does not exist."""
    error = {
        "error": "FEATURE_NOT_FOUND",
        "message": "No feature with ID 'nonexistent' exists.",
        "feature_id": "nonexistent",
    }
    setup_mocks(mock_http_client, request_data={"status": 404, "body": error})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("nonexistent", 50)
    
    assert result["error"] == "FEATURE_NOT_FOUND"


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_percentage_range(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test various valid percentage values."""
    setup_mocks(mock_http_client, request_data={"body": feature_search_v2})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    
    for percentage in [0, 1, 25, 50, 75, 99, 100]:
        mock_http_client.request.reset_mock()
        await client.adjust_traffic_rollout("search_v2", percentage)
        
        call_args = mock_http_client.request.call_args
        assert call_args[1]["json"]["percentage"] == percentage


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_correct_endpoint(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that correct endpoint is called (/traffic)."""
    setup_mocks(mock_http_client, request_data={"body": feature_search_v2})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    await client.adjust_traffic_rollout("search_v2", 50)
    
    call_args = mock_http_client.request.call_args
    url = call_args[0][1]
    assert "/traffic" in url
    assert "/state" not in url


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_updates_last_modified(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that last_modified is updated."""
    updated = {**feature_search_v2, "traffic_percentage": 75, "last_modified": "2026-04-27"}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("search_v2", 75)
    
    assert "last_modified" in result
    assert len(result["last_modified"]) == 10


@pytest.mark.asyncio
async def test_adjust_traffic_rollout_preserves_other_fields(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that adjusting traffic preserves other fields."""
    updated = {**feature_search_v2, "traffic_percentage": 30}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.adjust_traffic_rollout("search_v2", 30)
    
    assert result["status"] == "Testing"
    assert result["traffic_percentage"] == 30
    assert result["name"] == feature_search_v2["name"]
