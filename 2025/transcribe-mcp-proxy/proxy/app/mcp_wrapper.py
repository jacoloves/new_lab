"""FastMCP wrapper for handling MCP connections"""

import json
import logging
from re import A
import time
from typing import Dict, Any, Optional
import asyncio
import uuid

import httpx
from httpx_sse import aconnect_sse

from .models import MCPConnector
from .config_loader import get_config_loader

logger = logging.getLogger(__name__)


class MCPConnectionError(Exception):
    """Raised when MCP connection fails"""

    pass


class MCPClient:
    """Client for communicating with MCP servers"""

    def __init__(self, connector: MCPConnector, credentials: Optional[str] = None):
        """
        Initialize MCP client

        Args:
            connector: The MCP connector configuration
            credentials: Optional credentials (API token, etc.) as JSON string
        """
        self.connector = connector
        self.credentials = json.loads(credentials) if credentials else {}
        self.timeout = connector.timeout
        self.session_id: Optional[str] = None
        self.sse_message_endpoint: Optional[str] = None
        self.sse_client: Optional[httpx.AsyncClient] = None

    async def call_method(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a method on the MCP server

        Args:
            method: The method name to call
            params: Parameters for the method

        Returns:
            Response data from the MCP server

        Raises:
            MCPConnectionError: If connection or method call fails
        """
        # For HTTP transport, ensure session is initialized before other methods
        if (
            self.connector.type == "http"
            and method != "initialize"
            and not self.session_id
        ):
            logger.info(
                f"HTTP transport requires session, auto-initializing for connector {self.connector.id}"
            )
            try:
                await self._call_http_method(
                    "initialize",
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "mcp-proxy", "version": "1.0.0"},
                    },
                )
                logger.info(
                    f"Auto-initialization successful, session ID: {self.session_id}"
                )
            except Exception as e:
                logger.error(f"Auto-initialization failed: {e}")
                raise MCPConnectionError(f"Failed to initialize HTTP session: {e}")

        if self.connector.type == "rest":
            return await self._call_rest_method(method, params)
        elif self.connector.type == "stdio":
            return await self._call_stdio_method(method, params)
        elif self.connector.type == "sse":
            return await self._call_sse_method(method, params)
        elif self.connector.type == "http":
            return await self._call_http_method(method, params)
        else:
            raise MCPConnectionError(
                f"Unsupported connector type: {self.connector.type}"
            )

    async def _call_rest_method(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call REST-based MCP server"""
        if not self.connector.endpoint:
            raise MCPConnectionError("REST connector requires an endpoint")

        headers = {"Content-Type": "application/json"}

        # Add authentication if available
        if "api_token" in self.credentials:
            headers["Authorization"] = f"Bearer {self.credentials['api_token']}"

        # Prepare request payload
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(
                    f"Calling REST MCP method {method} at {self.connector.endpoint}"
                )
                response = await client.post(
                    self.connector.endpoint,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                result = response.json()

                # Check for JSON-RPC error
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown error")
                    raise MCPConnectionError(f"MCP method error: {error_msg}")

                return result.get("result", {})

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling MCP method {method}: {e}")
            raise MCPConnectionError(f"HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling MCP method {method}: {e}")
            raise MCPConnectionError(f"Unexpected error: {str(e)}")

    async def _call_stdio_method(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call stdio-based MCP server"""
        # This is a placeholder for stdio implementation
        # In a real implementation, you would spawn a subprocess and communicate via stdin/stdout
        raise MCPConnectionError("stdio connector type is not yet implemented")

    async def _establish_sse_connection(self) -> str:
        """
        Establish SSE connection and get message endpoint URL

        According to MCP 2024-11-05 SSE specification:
        1. Send GET request to SSE endpoint
        2. Receive 'endpoint' event with message URI
        3. Return the message endpoint URL for sending messages

        Returns:
            Message endpoint URL for sending JSON-RPC messages

        Raises:
            MCPConnectionError: If connection fails or endpoint event not received
        """
        if not self.connector.endpoint:
            raise MCPConnectionError("SSE connector requires an endpoint")

        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }

        # Add authentication if available
        if "api_token" in self.credentials:
            headers["Authorization"] = f"Bearer {self.credentials['api_token']}"

        try:
            # Create persistent client for SSE connection
            self.sse_client = httpx.AsyncClient(timeout=self.timeout)

            logger.info(f"Establishing SSE connection to: {self.connector.endpoint}")

            # Connect with GET request (MCP SSE spec requires GET)
            async with aconnect_sse(
                self.sse_client,
                "GET",
                self.connector.endpoint,
                headers=headers,
            ) as event_source:
                logger.info("SSE connection established, waiting for 'endpoint' event")

                # Wait for the 'endpoint' event from server
                async for sse_event in event_source.aiter_sse():
                    logger.debug(f"Received SSE event: {sse_event.event}")

                    if sse_event.event == "endpoint":
                        try:
                            endpoint_data = json.loads(sse_event.data)
                            message_uri = endpoint_data.get("uri")

                            if not message_uri:
                                raise MCPConnectionError(
                                    "'endpoint' event missing 'uri' field"
                                )

                            logger.info(f"Received message endpoint URI: {message_uri}")
                            return message_uri

                        except json.JSONDecodeError as e:
                            raise MCPConnectionError(
                                f"Failed to parse 'endpoint' event data: {e}"
                            )

                    # Continue waiting for endpoint event
                    logger.debug(
                        f"Waiting for 'endpoint' event, got: {sse_event.event}"
                    )

                # If we exit the loop without getting endpoint event
                raise MCPConnectionError(
                    "SSE stream ended without receiving 'endpoint' event"
                )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP {e.response.status_code} error establishing SSE connection: {e}"
            )
            if e.response.status_code == 401:
                raise MCPConnectionError("Authentication failed (401 Unauthorized)")
            elif e.response.status_code == 403:
                raise MCPConnectionError("Access forbidden (403 Forbidden)")
            else:
                raise MCPConnectionError(f"HTTP {e.response.status_code} error")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error establishing SSE connection: {e}")
            raise MCPConnectionError(f"HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Error establishing SSE connection: {e}")
            raise MCPConnectionError(f"Unexpected error: {str(e)}")

    async def _call_sse_method(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call SSE-based MCP server following MCP 2024-11-05 SSE specification

        According to MCP SSE transport spec:
        1. GET request to SSE endpoint to establish connection
        2. Server sends 'endpoint' event with message URI
        3. Client POSTs JSON-RPC messages to that URI
        4. Server sends responses via SSE 'message' events

        Args:
            method: The MCP method to call
            params: Parameters for the method

        Returns:
            Response data from the MCP server

        Raises:
            MCPConnectionError: If connection or method call fails
        """
        if not self.connector.endpoint:
            raise MCPConnectionError("SSE connector requires an endpoint")

        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }

        # Add authentication if available
        if "api_token" in self.credentials:
            headers["Authorization"] = f"Bearer {self.credentials['api_token']}"

        # Prepare JSON-RPC request payload
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as sse_client:
                logger.info(
                    f"Establishing SSE connection to: {self.connector.endpoint}"
                )

                # Step 1: Connect to SSE endpoint with GET request
                async with aconnect_sse(
                    sse_client,
                    "GET",
                    self.connector.endpoint,
                    headers=headers,
                ) as event_source:
                    logger.info("SSE connection established, waiting for events")

                    message_endpoint = None
                    response_result = None
                    response_error = None

                    # Step 2: Wait for 'endpoint' event and get message URI
                    # Store the iterator to ensure proper cleanup
                    sse_iterator = event_source.aiter_sse()
                    try:
                        async for sse_event in sse_iterator:
                            logger.debug(f"Received SSE event: {sse_event.event}")

                            # Handle 'endpoint' event to get message URI
                            if sse_event.event == "endpoint":
                                try:
                                    # Try to parse as JSON first (MCP 2024-11-05 spec format)
                                    try:
                                        endpoint_data = json.loads(sse_event.data)
                                        message_endpoint = endpoint_data.get("uri")
                                    except (json.JSONDecodeError, AttributeError):
                                        # If not JSON, use the data directly as URI (some servers send plain string)
                                        message_endpoint = sse_event.data.strip()

                                    if not message_endpoint:
                                        raise MCPConnectionError(
                                            "'endpoint' event missing URI"
                                        )

                                    # If relative path, make it absolute using the base URL
                                    if message_endpoint.startswith("/"):
                                        from urllib.parse import urlparse

                                        parsed_base = urlparse(self.connector.endpoint)
                                        base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"
                                        message_endpoint = base_url + message_endpoint

                                    logger.info(
                                        f"Received message endpoint URI: {message_endpoint}"
                                    )

                                    # Step 3: Send JSON-RPC message to the message endpoint
                                    async with httpx.AsyncClient(
                                        timeout=self.timeout
                                    ) as post_client:
                                        post_headers = {
                                            "Content-Type": "application/json"
                                        }

                                        # Add authentication for POST request
                                        if "api_token" in self.credentials:
                                            post_headers["Authorization"] = (
                                                f"Bearer {self.credentials['api_token']}"
                                            )

                                        logger.info(
                                            f"Sending JSON-RPC request to: {message_endpoint}"
                                        )
                                        post_response = await post_client.post(
                                            message_endpoint,
                                            headers=post_headers,
                                            json=payload,
                                        )
                                        post_response.raise_for_status()
                                        logger.info(
                                            "JSON-RPC request sent successfully"
                                        )

                                    # Step 4: Continue listening for response via SSE 'message' event
                                    continue

                                except json.JSONDecodeError as e:
                                    response_error = MCPConnectionError(
                                        f"Failed to parse 'endpoint' event: {e}"
                                    )
                                    break
                                except httpx.HTTPError as e:
                                    logger.error(
                                        f"Error sending message to endpoint: {e}"
                                    )
                                    response_error = MCPConnectionError(
                                        f"Failed to send message: {str(e)}"
                                    )
                                    break

                            # Handle 'message' event containing JSON-RPC response
                            elif sse_event.event == "message":
                                try:
                                    event_data = json.loads(sse_event.data)
                                    logger.debug(
                                        f"Received message event: {event_data}"
                                    )

                                    # Check if this is our JSON-RPC response
                                    if (
                                        event_data.get("jsonrpc") == "2.0"
                                        and event_data.get("id") == request_id
                                    ):
                                        # Check for errors
                                        if "error" in event_data:
                                            error_msg = event_data["error"].get(
                                                "messge", "Unknown error"
                                            )
                                            response_error = MCPConnectionError(
                                                f"MCP SSE error: {error_msg}"
                                            )
                                            break

                                        # Store the result and break to properly close SSE connection
                                        logger.info(
                                            f"Received response for request {request_id}"
                                        )
                                        response_result = event_data.get("result", {})
                                        break

                                    # Handle server-initiated notifications
                                    elif (
                                        "method" in event_data
                                        and "id" not in event_data
                                    ):
                                        logger.info(
                                            f"Received server notification: {event_data.get('method')}"
                                        )
                                        continue

                                except json.JSONDecodeError as e:
                                    logger.warning(
                                        f"Failed to parse 'message' event data: {e}"
                                    )
                                    continue
                            # Other event types - log and continue
                            else:
                                logger.debug(
                                    f"Received SSE event type '{sse_event.event}', continuing to wait"
                                )
                                continue

                    finally:
                        # Explicitly close the SSE iterator to clean up background tasks
                        await sse_iterator.aclose()
                # After exiting the async context, check if we got a response or error
                if response_error:
                    raise response_error

                if response_result is not None:
                    return response_result

                # If we exit the loop without getting a response
                raise MCPConnectionError(
                    f"SSE stream ended without receiving response for request {request_id}"
                )

        except MCPConnectionError:
            # Re-raise MCP errors as-is
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code} error: {e}")
            if e.response.status_code == 401:
                raise MCPConnectionError("Authentication failed (401 Unauthorized)")
            elif e.response.status_code == 403:
                raise MCPConnectionError("Access forbidden (403 Forbidden)")
            else:
                raise MCPConnectionError(f"HTTP {e.response.status_code} error")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in SSE connection: {e}")
            raise MCPConnectionError(f"HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in SSE method call: {e}")
            raise MCPConnectionError(f"Unexpected error: {str(e)}")

    async def _call_http_method(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call HTTP-based MCP server using Streamable HTTP Transport

        This implements the MCP Streamable HTTP transport specification:
        https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http

        Key features:
        - Accepts both JSON and SSE responses from server
        - Manages session IDs across requests
        - Supports custom headers (e.g., Authorization)
        - Handles HTTP 202 for notifications

        Args:
            method: The MCP method to call
            params: Parameters for the method

        Returns:
            Response data from the MCP server

        Raises:
            MCPConnectionError: If connection or method call fails
        """
        if not self.connector.endpoint:
            raise MCPConnectionError("HTTP connector requires an endpoint")

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        # Add session ID if we have one (after initialization)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        # Merge custom headers from connector configuration
        if self.connector.headers:
            headers.update(self.connector.headers)

        # Add authentication from credentials if available
        if "api_token" in self.credentials:
            # Don't override if Authorization is already in custom headers
            if "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {self.credentials['api_token']}"

        # Prepare JSON-RPC request payload
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(
                    f"Calling HTTP MCP method {method} at {self.connector.endpoint}"
                )

                response = await client.post(
                    self.connector.endpoint,
                    headers=headers,
                    json=payload,
                )

                # Extract session ID from initialize response
                if method == "initialize" and "Mcp-Session-Id" in response.headers:
                    self.session_id = response.headers["Mcp-Session-Id"]
                    logger.info(f"Received session ID: {self.session_id}")

                # Handle HTTP 202 for notifications (no response expected)
                if response.status_code == 202:
                    logger.info(f"Received HTTP 202 for notification method {method}")
                    return {}

                # Check for other HTTP errors
                response.raise_for_status()

                # Determine response type based on Content-Type
                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    # Simple JSON response
                    logger.debug(f"Received JSON response for method {method}")
                    result = response.json()

                    # Check for JSON-RPC error
                    if "error" in result:
                        error_msg = result["error"].get("message", "Unknown error")
                        raise MCPConnectionError(f"MCP method error: {error_msg}")

                    return result.get("result", {})

                elif "test/event-stream" in content_type:
                    # SSE stream response
                    logger.debug(f"Received SSE stream response for method {method}")

                    # For SSE streaming, we need to reconnect with SSE client
                    # This is a limitation of httpx - we can't parse SSE from existing response
                    # So we make a new request with SSE handling
                    async with aconnect_sse(
                        client,
                        "POST",
                        self.connector.endpoint,
                        headers=headers,
                        json=payload,
                    ) as event_source:
                        logger.info(f"Processing SSE stream for method {method}")

                        async for sse_event in event_source.aiter_sse():
                            logger.debug(
                                f"Received SSE event: {sse_event.event}, data: {sse_event.data[:100]}"
                            )

                            try:
                                event_data = json.loads(sse_event.data)

                                # Check if this is our response
                                if event_data.get("id") == request_id:
                                    # Check for errors
                                    if "error" in event_data:
                                        error_msg = event_data["error"].get(
                                            "message", "Unknown error"
                                        )
                                        raise MCPConnectionError(
                                            f"MCP HTTP SSE error: {error_msg}"
                                        )

                                    # Return the result
                                    return event_data.get("result", {})

                                # Handle server-initiated events (notifications)
                                elif "method" in event_data:
                                    logger.info(
                                        f"Received server notification: {event_data.get('method')}"
                                    )
                                    continue

                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE event data: {e}")
                                continue

                        # If we exit the loop without getting a response
                        raise MCPConnectionError(
                            f"SSE stream ended without receiving response for request {request_id}"
                        )
                else:
                    # Unexpected content type
                    raise MCPConnectionError(
                        f"Unexpected Content-Type: {content_type}. Expected application/json or text/event-stream"
                    )
        except MCPConnectionError:
            # Re-raise MCP errors as-is
            raise
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (401, 403, 404, etc.)
            logger.error(f"HTTP {e.response.status_code} error from HTTP endpoint: {e}")

            # Handle session expiry (404)
            if e.response.status_code == 404:
                logger.warning("Session may have expired (404), clearing session ID")
                self.session_id = None

            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = f": {error_body}"
            except:
                error_detail = f": {e.response.text[:200]}"

            if e.response.status_code == 401:
                raise MCPConnectionError(
                    f"Authentication failed (401 Unauthorized){error_detail}"
                )
            elif e.response.status_code == 403:
                raise MCPConnectionError(
                    f"Access forbidden (403 Forbidden){error_detail}"
                )
            elif e.response.status_code == 404:
                raise MCPConnectionError(
                    f"Session not found or expired (404 Not Found){error_detail}"
                )
            else:
                raise MCPConnectionError(
                    f"HTTP {e.response.status_code} error{error_detail}"
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling HTTP MCP method {method}: {e}")
            raise MCPConnectionError(f"HTTP error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling HTTP MCP method {method}: {e}")
            raise MCPConnectionError(f"Unexpected error: {str(e)}")


class MCPClientManager:
    """Manages MCP client connections"""

    def __init__(self):
        """Initialize the client manager"""
        self._clients: Dict[str, tuple[MCPClient, float]] = {}
        self._config_loader = get_config_loader()
        self._last_config_version: int = 0
        self._client_ttl: int = 300

    def _get_or_create_client(self, connector_id: str) -> MCPClient:
        """
        Get or create an MCP client for the given connector

        Args:
            connector_id: The connector ID

        Returns:
            MCPClient instance

        Raises:
            MCPConnectionError: If connector not found or client creation fails
        """
        # Check if configuration has changed and invalidate cache if needed
        current_config_version = self._config_loader.get_config_version()
        if current_config_version != self._last_config_version:
            logger.info(
                f"Configuration version changed from {self._last_config_version} to {current_config_version},"
                "clearing client cache"
            )
            self.clear_clients()
            self._last_config_version = current_config_version

        # Check if client already exists and is still valid
        current_time = time.time()
        if connector_id in self._clients:
            cached_client, cached_time = self._clients[connector_id]
            if (current_time - cached_time) < self._client_ttl:
                logger.debug(f"Using cached MCP client for connector {connector_id}")
                return cached_client
            else:
                logger.info(
                    f"Cached MCP client for connector {connector_id} expired, recreating"
                )
                del self._clients[connector_id]

        # Get connector configuration
        connector = self._config_loader.get_connector(connector_id)
        if not connector:
            raise MCPConnectionError(f"Connector not found: {connector_id}")

        # Get credentials if secret_arn is specified
        credentials = None
        if connector.secret_arn:
            logger.info(f"Fetching credentials for connector {connector_id}")
            credentials = self._config_loader.get_secret(connector.secret_arn)

        # Create and cache client with timestamp
        client = MCPClient(connector, credentials)
        self._clients[connector_id] = (client, current_time)

        logger.info(f"Created MCP client for connector {connector_id}")
        return client

    async def call_connector(
        self, connector_id: str, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a method on an MCP connector

        Args:
            connector_id: The connector ID to use
            method: The method to call
            params: Parameters for the method

        Returns:
            Response data from the MCP server

        Raises:
            MCPConnectionError: If the call fails
        """
        client = self._get_or_create_client(connector_id)
        return await client.call_method(method, params)

    def clear_clients(self):
        """Clear all cached clients (useful for config refresh)"""
        self._clients.clear()
        logger.info("Cleared all MCP client cache")


# Global client manager instance
_client_manager: Optional[MCPClientManager] = None


def get_client_manager() -> MCPClientManager:
    """Get the global client manager instance"""
    global _client_manager
    if _client_manager is None:
        _client_manager = MCPClientManager()
    return _client_manager
