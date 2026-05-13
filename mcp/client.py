"""
HTTP client for ProShop Feature Flags API.

Handles API calls with authentication, error handling, and automatic
reauthentication on 401.
"""

import httpx
from auth import AuthManager
from config import Config


class ProShopClient:
    """Client for ProShop Feature Flags API endpoints."""

    def __init__(self, config: Config, http_client: httpx.AsyncClient):
        """
        Initialize ProShop API client.
        
        Args:
            config: Configuration with API URL and credentials.
            http_client: httpx.AsyncClient instance for requests.
        """
        self.config = config
        self.http_client = http_client

    async def get_feature(self, feature_id: str) -> dict:
        """
        Get feature information.
        
        Calls: GET /api/features/:featureId
        
        Args:
            feature_id: The feature ID to retrieve.
            
        Returns:
            dict: Feature object or error object from backend.
        """
        return await self._request(
            "GET",
            f"/api/features/{feature_id}",
        )

    async def set_feature_state(self, feature_id: str, state: str) -> dict:
        """
        Set feature state (Disabled, Testing, Enabled).
        
        Calls: PATCH /api/features/:featureId/state
        
        Args:
            feature_id: The feature ID to update.
            state: Target state ("Disabled", "Testing", or "Enabled").
            
        Returns:
            dict: Updated feature object or error object from backend.
        """
        return await self._request(
            "PATCH",
            f"/api/features/{feature_id}/state",
            json={"state": state},
        )

    async def adjust_traffic_rollout(self, feature_id: str, percentage: int) -> dict:
        """
        Adjust traffic percentage for a Testing feature.
        
        Calls: PATCH /api/features/:featureId/traffic
        
        Args:
            feature_id: The feature ID to update.
            percentage: Target traffic percentage (0-100).
            
        Returns:
            dict: Updated feature object or error object from backend.
        """
        return await self._request(
            "PATCH",
            f"/api/features/{feature_id}/traffic",
            json={"percentage": percentage},
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
        retry_on_401: bool = True,
    ) -> dict:
        """
        Execute authenticated HTTP request.
        
        Args:
            method: HTTP method (GET, PATCH, etc).
            endpoint: API endpoint path (e.g., "/api/features/search_v2").
            json: Optional request body.
            retry_on_401: Whether to retry on 401 after reauthenticating.
            
        Returns:
            dict: Response body (success or error object).
        """
        # Get fresh token
        token = await AuthManager.ensure_authenticated()

        url = f"{self.config.api_url}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = await self.http_client.request(
                method,
                url,
                headers=headers,
                json=json,
            )

            # If 401, try reauthenticating and retry once
            if response.status_code == 401 and retry_on_401:
                await AuthManager.reset_token()
                return await self._request(
                    method,
                    endpoint,
                    json=json,
                    retry_on_401=False,  # Don't retry twice
                )

            # Return response body regardless of status code
            # Backend returns proper error objects in all cases
            try:
                return response.json()
            except Exception:
                # Fallback if response is not JSON
                return {
                    "error": "INVALID_RESPONSE",
                    "message": f"Backend returned non-JSON response: {response.text}",
                }

        except httpx.ConnectError as e:
            return {
                "error": "BACKEND_UNREACHABLE",
                "message": f"Backend is not reachable at {self.config.api_url}: {e}",
            }
        except httpx.RequestError as e:
            return {
                "error": "REQUEST_FAILED",
                "message": f"Request failed: {e}",
            }
