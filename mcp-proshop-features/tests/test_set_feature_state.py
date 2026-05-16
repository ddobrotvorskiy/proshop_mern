"""
Tests for set_feature_state tool.

Tests state transitions, dependency checking, and error handling.
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
async def test_set_feature_state_to_enabled(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test transitioning feature to Enabled."""
    updated = {**feature_search_v2, "status": "Enabled", "traffic_percentage": 100}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("search_v2", "Enabled")
    
    assert result["status"] == "Enabled"
    assert result["traffic_percentage"] == 100


@pytest.mark.asyncio
async def test_set_feature_state_to_disabled(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test transitioning feature to Disabled."""
    updated = {**feature_search_v2, "status": "Disabled", "traffic_percentage": 0}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("search_v2", "Disabled")
    
    assert result["status"] == "Disabled"
    assert result["traffic_percentage"] == 0


@pytest.mark.asyncio
async def test_set_feature_state_to_testing(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test transitioning feature to Testing."""
    updated = {**feature_search_v2, "status": "Testing"}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("search_v2", "Testing")
    
    assert result["status"] == "Testing"


@pytest.mark.asyncio
async def test_set_feature_state_with_dependency_warning(
    config,
    mock_http_client: AsyncMock,
    feature_semantic_search: dict,
) -> None:
    """Test that enabling a feature with disabled dependencies returns warnings."""
    warning_response = {
        **feature_semantic_search,
        "status": "Enabled",
        "traffic_percentage": 100,
        "warnings": ["Dependency 'search_v2' is in status 'Testing', not 'Enabled'."],
    }
    setup_mocks(mock_http_client, request_data={"body": warning_response})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("semantic_search", "Enabled")
    
    assert result["status"] == "Enabled"
    assert "warnings" in result
    assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_set_feature_state_invalid_state(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test invalid state value error."""
    error = {
        "error": "INVALID_STATE",
        "message": "State 'InValid' is not valid.",
        "feature_id": "search_v2",
    }
    setup_mocks(mock_http_client, request_data={"status": 400, "body": error})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("search_v2", "InValid")
    
    assert result["error"] == "INVALID_STATE"


@pytest.mark.asyncio
async def test_set_feature_state_feature_not_found(
    config,
    mock_http_client: AsyncMock,
) -> None:
    """Test feature not found error."""
    error = {
        "error": "FEATURE_NOT_FOUND",
        "message": "No feature with ID 'nonexistent' exists.",
        "feature_id": "nonexistent",
    }
    setup_mocks(mock_http_client, request_data={"status": 404, "body": error})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("nonexistent", "Enabled")
    
    assert result["error"] == "FEATURE_NOT_FOUND"


@pytest.mark.asyncio
async def test_set_feature_state_updates_last_modified(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that last_modified is updated."""
    updated = {**feature_search_v2, "status": "Enabled", "last_modified": "2026-04-27"}
    setup_mocks(mock_http_client, request_data={"body": updated})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    result = await client.set_feature_state("search_v2", "Enabled")
    
    assert "last_modified" in result
    assert len(result["last_modified"]) == 10


@pytest.mark.asyncio
async def test_set_feature_state_correct_endpoint(
    config,
    mock_http_client: AsyncMock,
    feature_search_v2: dict,
) -> None:
    """Test that correct endpoint is called (/state)."""
    setup_mocks(mock_http_client, request_data={"body": feature_search_v2})
    
    await AuthManager.initialize(config, mock_http_client)
    client = ProShopClient(config, mock_http_client)
    await client.set_feature_state("search_v2", "Testing")
    
    call_args = mock_http_client.request.call_args
    url = call_args[0][1]
    assert "/state" in url
    assert "/traffic" not in url
