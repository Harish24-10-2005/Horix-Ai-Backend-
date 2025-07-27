import logging
import os
from importlib.metadata import version
from typing import Optional, Dict, Any

import pagerduty
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

logger = logging.getLogger(__name__)


class PagerDutyClient:
    _env_client: Optional[pagerduty.RestApiV2Client] = None

    @staticmethod
    def _get_header_token() -> Optional[str]:
        """Try to get auth token from HTTP headers.

        Returns:
            Optional[str]: The token if found in headers, None otherwise
        """
        try:
            request: Request = get_http_request()
            return request.headers.get("X-Goose-Token")
        except RuntimeError:
            return None

    @staticmethod
    def _get_env_token() -> Optional[str]:
        """Try to get auth token from environment variable.

        Returns:
            Optional[str]: The token if found in environment, None otherwise
        """
        return os.environ.get("PAGERDUTY_API_TOKEN")

    @staticmethod
    def _get_credentials_token(credentials: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Try to get auth token from passed credentials.

        Args:
            credentials: Dictionary containing credentials

        Returns:
            Optional[str]: The token if found in credentials, None otherwise
        """
        if not credentials:
            return None
        
        # Try different possible credential key names
        for key in ["PAGERDUTY_API_TOKEN", "api_token", "token", "access_token"]:
            if key in credentials:
                return credentials[key]
        
        return None

    @staticmethod
    def _create_client_with_token(token: str) -> pagerduty.RestApiV2Client:
        """Create a new PagerDuty client with the given token.

        Args:
            token: The authentication token to use

        Returns:
            pagerduty.RestApiV2Client: A configured client
        """
        client = pagerduty.RestApiV2Client(token)
        client.headers["User-Agent"] = (
            f"pagerduty_mcp_server/{version('pagerduty_mcp_server')}"
        )
        return client

    def get_client(self, credentials: Optional[Dict[str, Any]] = None) -> pagerduty.RestApiV2Client:
        """Get a PagerDuty API client.

        Priority order:
        1. Credentials passed as parameter
        2. Goose token from request headers
        3. Environment variable token

        Args:
            credentials: Optional dictionary containing API credentials

        Returns:
            pagerduty.RestApiV2Client: A configured PagerDuty API client

        Raises:
            Exception: If no valid auth token is found
        """
        # Try credentials parameter first
        if token := self._get_credentials_token(credentials):
            return self._create_client_with_token(token)

        # Try header token second
        if token := self._get_header_token():
            return self._create_client_with_token(token)

        # Use existing env client if we have one
        if self._env_client is not None:
            return self._env_client

        # Try to create env client if we don't have one
        if token := self._get_env_token():
            self._env_client = self._create_client_with_token(token)
            return self._env_client

        # No valid token found
        logger.error("No auth token found in credentials, headers, or environment variables")
        raise Exception("No auth token found in credentials, headers, or environment variables")


# Singleton instance
client = PagerDutyClient()


def create_client(credentials: Optional[Dict[str, Any]] = None) -> pagerduty.RestApiV2Client:
    """Get a PagerDuty API client.

    Creates a new client with credentials passed as parameter, or falls back to
    headers/environment variables.

    Args:
        credentials: Optional dictionary containing API credentials

    Returns:
        pagerduty.RestApiV2Client: A configured PagerDuty API client

    Raises:
        Exception: If no valid auth token is found
    """
    return client.get_client(credentials)