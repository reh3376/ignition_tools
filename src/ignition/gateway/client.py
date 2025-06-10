"""Ignition Gateway HTTP Client.

Provides HTTP/HTTPS communication with Ignition Gateway instances,
including authentication, health checks, and API operations.
"""

import json
import logging
import time
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.util.retry import Retry

from .config import GatewayConfig, GatewayConfigManager

logger = logging.getLogger(__name__)


class IgnitionGatewayClient:
    """HTTP client for connecting to Ignition Gateway instances."""

    def __init__(
        self, config: Optional[GatewayConfig] = None, config_name: Optional[str] = None
    ):
        """Initialize the gateway client.

        Args:
            config: Direct GatewayConfig instance
            config_name: Name of config to load from GatewayConfigManager
        """
        if config:
            self.config = config
        elif config_name:
            manager = GatewayConfigManager()
            self.config = manager.get_config(config_name)
            if not self.config:
                raise ValueError(f"No configuration found for gateway: {config_name}")
        else:
            raise ValueError("Either config or config_name must be provided")

        self.session = requests.Session()
        self._setup_session()
        self._authenticated = False
        self._last_health_check = None

    def _setup_session(self):
        """Configure the HTTP session with timeouts, retries, and SSL settings."""
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set timeout
        self.session.timeout = self.config.timeout

        # SSL verification
        self.session.verify = self.config.verify_ssl
        if not self.config.verify_ssl:
            # Disable SSL warnings for development
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Set default headers
        self.session.headers.update(
            {
                "User-Agent": "IGN-Scripts-Client/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        logger.debug(
            f"Configured session for {self.config.name}: timeout={self.config.timeout}, verify_ssl={self.config.verify_ssl}"
        )

    def connect(self) -> bool:
        """Establish connection and authenticate with the gateway.

        Returns:
            True if connection and authentication successful
        """
        try:
            logger.info(
                f"Connecting to gateway {self.config.name} at {self.config.base_url}"
            )

            # Setup authentication
            if not self._setup_authentication():
                return False

            # Test connection with a simple endpoint
            if not self._test_connection():
                return False

            self._authenticated = True
            logger.info(f"Successfully connected to gateway {self.config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to gateway {self.config.name}: {e}")
            return False

    def _setup_authentication(self) -> bool:
        """Setup authentication for the session."""
        try:
            if self.config.auth_type == "basic":
                if not self.config.username or not self.config.password:
                    logger.error(
                        "Username and password required for basic authentication"
                    )
                    return False

                self.session.auth = HTTPBasicAuth(
                    self.config.username, self.config.password
                )
                logger.debug("Configured basic authentication")

            elif self.config.auth_type == "token":
                if not self.config.token:
                    logger.error("Token required for token authentication")
                    return False

                self.session.headers.update(
                    {"Authorization": f"Bearer {self.config.token}"}
                )
                logger.debug("Configured token authentication")

            elif self.config.auth_type == "ntlm":
                try:
                    from requests_ntlm import HttpNtlmAuth

                    if not self.config.username or not self.config.password:
                        logger.error(
                            "Username and password required for NTLM authentication"
                        )
                        return False

                    self.session.auth = HttpNtlmAuth(
                        self.config.username, self.config.password
                    )
                    logger.debug("Configured NTLM authentication")
                except ImportError:
                    logger.error(
                        "requests-ntlm package required for NTLM authentication"
                    )
                    return False

            else:
                logger.error(
                    f"Unsupported authentication type: {self.config.auth_type}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to setup authentication: {e}")
            return False

    def _test_connection(self) -> bool:
        """Test connection with a simple API call."""
        try:
            # Use root endpoint for connection test - works with all Ignition versions
            response = self.session.get(self.config.base_url, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[dict[str, Any]]:
        """Make an HTTP request to the gateway.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dictionary, or None if request failed
        """
        try:
            url = urljoin(self.config.base_url, endpoint)

            logger.debug(f"Making {method} request to {url}")

            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            # Try to parse JSON response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"status": "success", "data": response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None

    def health_check(self) -> dict[str, Any]:
        """Perform a comprehensive health check on the gateway.

        Returns:
            Health check results including connectivity, authentication, and API status
        """
        health_result = {
            "gateway_name": self.config.name,
            "gateway_url": self.config.base_url,
            "timestamp": time.time(),
            "overall_status": "unknown",
            "checks": {
                "connectivity": {"status": "unknown", "details": ""},
                "authentication": {"status": "unknown", "details": ""},
                "api_access": {"status": "unknown", "details": ""},
                "response_time": {"status": "unknown", "value_ms": 0},
            },
        }

        start_time = time.time()

        try:
            # Test basic connectivity
            logger.debug("Testing basic connectivity...")
            try:
                response = self.session.get(self.config.base_url, timeout=10)
                health_result["checks"]["connectivity"]["status"] = "healthy"
                health_result["checks"]["connectivity"][
                    "details"
                ] = f"HTTP {response.status_code}"
            except Exception as e:
                health_result["checks"]["connectivity"]["status"] = "unhealthy"
                health_result["checks"]["connectivity"]["details"] = str(e)
                health_result["overall_status"] = "unhealthy"
                return health_result

            # Test authentication
            logger.debug("Testing authentication...")
            if self._authenticated or self.connect():
                health_result["checks"]["authentication"]["status"] = "healthy"
                health_result["checks"]["authentication"][
                    "details"
                ] = f"Auth type: {self.config.auth_type}"
            else:
                health_result["checks"]["authentication"]["status"] = "unhealthy"
                health_result["checks"]["authentication"][
                    "details"
                ] = "Authentication failed"
                health_result["overall_status"] = "unhealthy"
                return health_result

            # Test API access using known working endpoints
            logger.debug("Testing API access...")
            try:
                # Test gateway info endpoint
                gwinfo_response = self.session.get(
                    f"{self.config.base_url}/system/gwinfo", timeout=10
                )
                if gwinfo_response.status_code == 200:
                    health_result["checks"]["api_access"]["status"] = "healthy"
                    health_result["checks"]["api_access"][
                        "details"
                    ] = "Gateway info accessible"
                else:
                    health_result["checks"]["api_access"]["status"] = "warning"
                    health_result["checks"]["api_access"][
                        "details"
                    ] = "Limited API access"
            except Exception:
                health_result["checks"]["api_access"]["status"] = "warning"
                health_result["checks"]["api_access"][
                    "details"
                ] = "API access test failed"

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            health_result["checks"]["response_time"]["value_ms"] = round(
                response_time_ms, 2
            )

            if response_time_ms < 1000:
                health_result["checks"]["response_time"]["status"] = "healthy"
            elif response_time_ms < 5000:
                health_result["checks"]["response_time"]["status"] = "warning"
            else:
                health_result["checks"]["response_time"]["status"] = "unhealthy"

            # Determine overall status
            statuses = [check["status"] for check in health_result["checks"].values()]
            if all(status == "healthy" for status in statuses):
                health_result["overall_status"] = "healthy"
            elif any(status == "unhealthy" for status in statuses):
                health_result["overall_status"] = "unhealthy"
            else:
                health_result["overall_status"] = "warning"

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_result["overall_status"] = "error"
            health_result["error"] = str(e)

        self._last_health_check = health_result
        return health_result

    def get_gateway_info(self) -> Optional[dict[str, Any]]:
        """Get basic gateway information.

        Returns:
            Gateway information including version, status, etc.
        """
        if not self._authenticated and not self.connect():
            return None

        try:
            # Try to get gateway status/info
            info = {}

            # Try gateway info endpoint (/system/gwinfo - confirmed working)
            try:
                gwinfo_response = self.session.get(
                    f"{self.config.base_url}/system/gwinfo", timeout=10
                )
                if gwinfo_response.status_code == 200:
                    info["gateway_info_raw"] = gwinfo_response.text.strip()

                    # Try to parse as JSON if possible
                    try:
                        info["gateway_info"] = gwinfo_response.json()
                    except json.JSONDecodeError:
                        # Keep as text if not JSON
                        info["gateway_info"] = gwinfo_response.text.strip()
            except Exception as e:
                logger.debug(f"Could not fetch gateway info: {e}")

            # Try status connections endpoint (/main/web/status/connections - confirmed working)
            try:
                conn_response = self.session.get(
                    f"{self.config.base_url}/main/web/status/connections", timeout=10
                )
                if conn_response.status_code == 200:
                    info["connections_available"] = True
                    info["connections_page_size"] = len(conn_response.content)
            except Exception as e:
                logger.debug(f"Could not fetch connections info: {e}")

            # Add configuration info
            info.update(
                {
                    "config_name": self.config.name,
                    "configured_host": self.config.host,
                    "configured_port": self.config.port,
                    "uses_https": self.config.use_https,
                    "project_name": self.config.project_name,
                    "connection_url": self.config.base_url,
                    "auth_type": self.config.auth_type,
                    "username": self.config.username,
                }
            )

            return info

        except Exception as e:
            logger.error(f"Failed to get gateway info: {e}")
            return None

    def test_tag_read(self, tag_path: str) -> Optional[dict[str, Any]]:
        """Test reading a tag value from the gateway.

        Args:
            tag_path: Full path to the tag

        Returns:
            Tag read result with value and quality
        """
        if not self._authenticated and not self.connect():
            return None

        try:
            # This is a placeholder - actual Ignition tag API endpoints would be used
            # For now, we'll simulate a tag read test
            logger.info(f"Testing tag read for: {tag_path}")

            # In a real implementation, this would use Ignition's REST API
            # or WebDev endpoints for tag operations
            return {
                "tag_path": tag_path,
                "status": "test_mode",
                "message": "Tag read functionality requires specific Ignition API endpoints",
            }

        except Exception as e:
            logger.error(f"Tag read test failed: {e}")
            return None

    def disconnect(self):
        """Close the connection to the gateway."""
        if self.session:
            self.session.close()
        self._authenticated = False
        logger.info(f"Disconnected from gateway {self.config.name}")

    def is_connected(self) -> bool:
        """Check if currently connected and authenticated."""
        return self._authenticated

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class GatewayConnectionPool:
    """Manages multiple gateway connections."""

    def __init__(self):
        """Initialize the connection pool."""
        self.clients: dict[str, IgnitionGatewayClient] = {}
        self.config_manager = GatewayConfigManager()

    def add_client(self, config_name: str) -> bool:
        """Add a client to the pool.

        Args:
            config_name: Name of the gateway configuration

        Returns:
            True if client was added successfully
        """
        try:
            if config_name in self.clients:
                logger.warning(f"Client for {config_name} already exists")
                return True

            client = IgnitionGatewayClient(config_name=config_name)
            self.clients[config_name] = client
            logger.info(f"Added client for gateway: {config_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add client for {config_name}: {e}")
            return False

    def get_client(self, config_name: str) -> Optional[IgnitionGatewayClient]:
        """Get a client from the pool.

        Args:
            config_name: Name of the gateway configuration

        Returns:
            Gateway client or None if not found
        """
        return self.clients.get(config_name)

    def connect_all(self) -> dict[str, bool]:
        """Connect all clients in the pool.

        Returns:
            Dictionary mapping client names to connection success status
        """
        results = {}
        for name, client in self.clients.items():
            try:
                results[name] = client.connect()
            except Exception as e:
                logger.error(f"Failed to connect client {name}: {e}")
                results[name] = False

        return results

    def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Perform health checks on all clients.

        Returns:
            Dictionary mapping client names to health check results
        """
        results = {}
        for name, client in self.clients.items():
            try:
                results[name] = client.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = {"overall_status": "error", "error": str(e)}

        return results

    def disconnect_all(self):
        """Disconnect all clients in the pool."""
        for name, client in self.clients.items():
            try:
                client.disconnect()
                logger.info(f"Disconnected client: {name}")
            except Exception as e:
                logger.error(f"Failed to disconnect client {name}: {e}")

    def remove_client(self, config_name: str) -> bool:
        """Remove a client from the pool.

        Args:
            config_name: Name of the gateway configuration

        Returns:
            True if client was removed successfully
        """
        if config_name in self.clients:
            try:
                self.clients[config_name].disconnect()
                del self.clients[config_name]
                logger.info(f"Removed client for gateway: {config_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to remove client {config_name}: {e}")
                return False

        return False
