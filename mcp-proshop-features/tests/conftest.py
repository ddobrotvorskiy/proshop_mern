"""
Test fixtures for ProShop Feature Flags MCP Server tests.

Provides mock HTTP client, sample feature objects, and auth mocking.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import httpx

# Add parent directory to path so we can import mcp modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from auth import AuthManager
from client import ProShopClient


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def config() -> Config:
    """Provide a test configuration."""
    return Config(
        api_url="http://localhost:5000",
        admin_email="admin@test.com",
        admin_password="testpass",
    )


# ============================================================================
# Sample Feature Objects
# ============================================================================


@pytest.fixture
def feature_search_v2() -> dict:
    """Sample feature: search_v2 (Testing)."""
    return {
        "feature_id": "search_v2",
        "name": "New Search Algorithm",
        "description": "Replaces legacy regex-based keyword matching with BM25 + TF-IDF.",
        "status": "Testing",
        "traffic_percentage": 15,
        "last_modified": "2026-03-10",
        "targeted_segments": ["beta_users", "internal"],
        "rollout_strategy": "canary",
    }


@pytest.fixture
def feature_dark_mode() -> dict:
    """Sample feature: dark_mode (Testing)."""
    return {
        "feature_id": "dark_mode",
        "name": "Dark Mode Theme",
        "description": "Adds a theme toggle to the Header component.",
        "status": "Testing",
        "traffic_percentage": 20,
        "last_modified": "2026-04-20",
        "targeted_segments": ["all"],
        "rollout_strategy": "ab_test",
    }


@pytest.fixture
def feature_semantic_search() -> dict:
    """Sample feature: semantic_search (Disabled with dependency)."""
    return {
        "feature_id": "semantic_search",
        "name": "Semantic Vector Search",
        "description": "Augments keyword search with embedding-based semantic similarity.",
        "status": "Disabled",
        "traffic_percentage": 0,
        "last_modified": "2026-02-14",
        "targeted_segments": ["internal"],
        "rollout_strategy": "canary",
        "dependencies": ["search_v2"],
    }


@pytest.fixture
def feature_paypal_enabled() -> dict:
    """Sample feature: paypal_express_buttons (Enabled)."""
    return {
        "feature_id": "paypal_express_buttons",
        "name": "PayPal Express Checkout Buttons",
        "description": "Surfaces PayPal Smart Payment Buttons on cart and product pages.",
        "status": "Enabled",
        "traffic_percentage": 100,
        "last_modified": "2026-01-08",
        "targeted_segments": ["all"],
        "rollout_strategy": "full_release",
    }


# ============================================================================
# Mock HTTP Client
# ============================================================================


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Provide a mocked httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def mock_response_success(feature_search_v2: dict) -> AsyncMock:
    """Provide a successful mock response."""
    response = AsyncMock()
    response.status_code = 200
    response.json = MagicMock(return_value=feature_search_v2)
    return response


@pytest.fixture
def mock_response_not_found() -> AsyncMock:
    """Provide a 404 error response."""
    response = AsyncMock()
    response.status_code = 404
    response.json = MagicMock(return_value={
        "error": "FEATURE_NOT_FOUND",
        "message": "No feature with ID 'unknown_feature' exists in features.json.",
        "feature_id": "unknown_feature",
    })
    return response


@pytest.fixture
def mock_response_invalid_state() -> AsyncMock:
    """Provide a 400 error response for invalid state."""
    response = AsyncMock()
    response.status_code = 400
    response.json = MagicMock(return_value={
        "error": "INVALID_STATE",
        "message": "State 'Invalid' is not valid. Must be one of: Disabled, Testing, Enabled (case-sensitive).",
        "feature_id": "test_feature",
    })
    return response


@pytest.fixture
def mock_response_wrong_status() -> AsyncMock:
    """Provide a 400 error for wrong status for rollout adjustment."""
    response = AsyncMock()
    response.status_code = 400
    response.json = MagicMock(return_value={
        "error": "WRONG_STATUS_FOR_ROLLOUT",
        "message": "adjust_traffic_rollout can only be called on features with status 'Testing'.",
        "feature_id": "paypal_express_buttons",
    })
    return response


@pytest.fixture
def mock_response_login_success() -> AsyncMock:
    """Provide a successful login response."""
    response = AsyncMock()
    response.status_code = 200
    response.json = MagicMock(return_value={"token": "test_jwt_token_12345"})
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def mock_response_unauthorized() -> AsyncMock:
    """Provide a 401 unauthorized response."""
    response = AsyncMock()
    response.status_code = 401
    response.text = "Unauthorized"
    return response


# ============================================================================
# Client Fixtures
# ============================================================================


@pytest.fixture
def proshop_client(config: Config, mock_http_client: AsyncMock) -> ProShopClient:
    """Provide a ProShopClient with mocked HTTP client."""
    return ProShopClient(config, mock_http_client)


@pytest.fixture
def auth_manager_initialized(config: Config, mock_http_client: AsyncMock) -> None:
    """Setup AuthManager with mocked login for use in tests."""
    # Mock the login response
    login_response = AsyncMock()
    login_response.status_code = 200
    login_response.json.return_value = {"token": "test_jwt_token"}
    login_response.raise_for_status = MagicMock()
    
    mock_http_client.post.return_value = login_response
    
    # Note: actual initialization happens in tests via await
    # This fixture just sets up mocks


# ============================================================================
# Pytest Configuration
# ============================================================================


@pytest.fixture(autouse=True)
def reset_auth_manager() -> None:
    """Reset AuthManager state before each test."""
    AuthManager._token = None
    AuthManager._config = None
    AuthManager._client = None
    yield
    AuthManager._token = None
    AuthManager._config = None
    AuthManager._client = None
