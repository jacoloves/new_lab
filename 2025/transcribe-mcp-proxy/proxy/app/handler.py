"""AWS Lambda handler for MCP Proxy (JSON-RPC 2.0 / MCP Protocol compliant)"""

import json
import logging
import traceback
import asyncio
from typing import Dict, Any, Optional

from httpx import request

from .config_loader import get_config_loader
from .mcp_wrapper import MCPConnectionError
from .mcp_aggregator import get_aggregator
from .models import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    InitializeResult,
    ServerInfo,
    ServerCaapabilities,
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Server metadata
SERVER_NAME = "MCP Proxy Lambda"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"


def create_http_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an API Gateway HTTP response

    Args:
        status_code: HTTP status code
        body: Response body as dictionary

    Returns:
        Lambda response object for API Gateway
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    }


def create_jsonrpc_response(
    request_id: Optional[Any], result: Any = None, error: Optional[JSONRPCError] = None
) -> JSONRPCResponse:
    """
    Create a JSON-RPC 2.0 response

    Args:
        request_id: The request ID
        result: The result (if success)
        error: The error (if failure)

    Returns:
        JSONRPCResponse object
    """
    return JSONRPCResponse(jsonrpc="2.0", id=request_id, result=result, error=error)


def create_jsonrpc_error(code: int, message: str, data: Any = None) -> JSONRPCError:
    """
    Create a JSON-RPC 2.0 error object

    Args:
        code: Error code
        message: Error message
        data: Additional error data

    Returns:
        JSONRPCError object
    """
    return JSONRPCError(code=code, message=message, data=data)


async def handle_initialize(params: Optional[Dict[str, Any]]) -> InitializeResult:
    """
    Handle the 'initialize' method

    Args:
        params: Initialize parameters

    Returns:
        InitializeResult with server capabilities
    """
    logger.info("Handling initialize request")

    # Load connectors to ensure they're available
    config_loader = get_config_loader()
    connectors = config_loader.load_connectors()

    logger.info(f"Initialized with {len(connectors)} backend connectors")

    # Return server capabilities
    capabilities = ServerCaapabilities(
        tools={},
        resources={},
        prompts={},
    )

    server_info = ServerInfo(name=SERVER_NAME, version=SERVER_VERSION)

    return InitializeResult(
        protocolVersion=PROTOCOL_VERSION,
        capabilities=capabilities,
        serverInfo=server_info,
    )


async def handle_tools_list(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'tools/list' method - aggregate tools from all backend servers

    Args:
        params: Method parameters

    Returns:
        Aggregated list of tools
    """
    logger.info("Handling tools/list request")

    aggregator = get_aggregator()
    tools = await aggregator.list_all_tools()

    return {"tools": tools}


async def handle_tools_call(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'tools/call' method - route to appropriate backend server

    Args:
        params: Method parameters (name, arguments)

    Returns:
        Tool execution result
    """
    if not params:
        raise ValueError("Missing parameters for tools/call")

    # Validate that params is a dict (named parameters), not an array (positional)
    if not isinstance(params, dict):
        raise ValueError(
            "tools/call requires named parameters (object), not positional parameters (array)"
        )

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        raise ValueError("Missing 'name' parameter for tools/call")

    logger.info(f"Handling tools/call request for tool: {tool_name}")

    aggregator = get_aggregator()
    result = await aggregator.call_tool(tool_name, arguments)

    return result


async def handle_resources_list(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'resources/list' method - aggregate resources from all backend servers

    Args:
        params: Method parameters

    Returns:
        Aggregated list of resources
    """
    logger.info("Handling resources/list request")

    aggregator = get_aggregator()
    resources = await aggregator.list_all_resources()

    return {"resources": resources}


async def handle_resources_read(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'resources/read' method - route to appropriate backend server

    Args:
        params: Method parameters (uri)

    Returns:
        Resource content
    """
    if not params:
        raise ValueError("Missing parameters for resources/read")

    # Validate that params is a dict (named parameters), not an array (positional)
    if not isinstance(params, dict):
        raise ValueError(
            "resources/read requires named parameters (object), not positional parameters (array)"
        )

    uri = params.get("uri")
    if not uri:
        raise ValueError("Missing 'uri' parameter for resources/read")

    logger.info(f"Handling resources/read request for URI: {uri}")

    aggregator = get_aggregator()
    result = await aggregator.read_resource(uri)

    return result


async def handle_prompts_list(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'prompts/list' method - aggregate prompts from all backend servers

    Args:
        params: Method parameters

    Returns:
        Aggregated list of prompts
    """
    logger.info("Handling prompts/list request")

    aggregator = get_aggregator()
    prompts = await aggregator.list_all_prompts()

    return {"prompts": prompts}


async def handle_promopts_get(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Handle the 'prompts/get' method - route to appropriate backend server

    Args:
        params: Method parameters (name, arguments)

    Returns:
        Prompt content
    """
    if not params:
        raise ValueError("Missing parameters for prompts/get")

    # Validate that params is a dict (named parameters), not an array (positional)
    if not isinstance(params, dict):
        raise ValueError(
            "prompts/get requires named parameters (object), not positional parameters (array)"
        )

    prompt_name = params.get("name")
    arguments = params.get("arguments")

    if not prompt_name:
        raise ValueError("Missing 'name' parameter for prompts/get")

    logger.info(f"Handling prompts/get request for prompt: {prompt_name}")

    aggregator = get_aggregator()
    result = await aggregator.get_prompt(prompt_name, arguments)

    return result


async def handle_jsonrpc_request(
    request: JSONRPCRequest, is_notification: bool = False
) -> Optional[JSONRPCResponse]:
    """
    Handle a JSON-RPC 2.0 request

    Args:
        request: The JSON-RPC request
        is_notification: True if the request is a notification (id member is absent)

    Returns:
        JSONRPCResponse object, or None for notifications
    """
    method = request.method
    params = request.params
    request_id = request.id

    logger.info(f"Handling JSON-RPC method: {method} (notification: {is_notification})")

    try:
        # Route to appropriate handler based on method
        if method == "initialize":
            result = await handle_initialize(params)
            # Notifications should not get responses
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result.model_dump())

        elif method == "initialized":
            # This is typically a notification, no response needed
            logger.info("Received 'initialized' notification")
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result={})

        elif method == "tools/list":
            result = await handle_tools_list(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        elif method == "tools/call":
            result = await handle_tools_call(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        elif method == "resources/list":
            result = await handle_resources_list(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        elif method == "resources/read":
            result = await handle_resources_read(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        elif method == "prompts/list":
            result = await handle_prompts_list(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        elif method == "prompts/get":
            result = await handle_prompts_get(params)
            if is_notification:
                return None
            return create_jsonrpc_response(request_id, result=result)

        else:
            # Method not found
            # Even for errors, notifications should not get responses
            if is_notification:
                logger.warning(f"Notification for unknown method: {method}")
                return None
            error = create_jsonrpc_error(-32601, f"Method not found: {method}")
            return create_jsonrpc_response(request_id, error=error)

    except ValueError as e:
        # Invalid params
        logger.error(f"Invalid params for method {method}: {e}")
        if is_notification:
            return None
        error = create_jsonrpc_error(-32602, f"Invalid params: {str(e)}")
        return create_jsonrpc_response(request_id, error=error)

    except MCPConnectionError as e:
        # MCP backend error
        logger.error(f"MCP connection error: {e}")
        if is_notification:
            return None
        error = create_jsonrpc_error(-32000, f"Backend MCP error: {str(e)}")
        return create_jsonrpc_response(request_id, error=error)

    except Exception as e:
        # Internal error
        logger.error(f"Internal error handling method {method}: {e}")
        logger.error(traceback.format_exc())
        if is_notification:
            return None
        error = create_jsonrpc_error(-32603, f"Internale error: {str(e)}")
        return create_jsonrpc_response(request_id, error=error)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function (JSON-RPC 2.0 / MCP Protocol compliant)

    Args:
        event: Lambda event object (from API Gateway)
        context: Lambda context object

    Returns:
        Lambda response object for API Gateway
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Handle OPTIONS request for CORS
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return create_http_response(200, {"message": "OK"})

    try:
        # Parse request body
        body_str = event.get("body", "{}")
        if event.get("isBase64Encoded", False):
            import base64

            body_str = base64.b64decode(body_str).decode("utf-8")

        body = json.loads(body_str)

        # JSON-RPC 2.0: Check if body is a dict (single request) or list (batch request)
        if isinstance(body, list):
            # Batch requests are not currently supported
            error_response = create_jsonrpc_response(
                None,
                error=create_jsonrpc_error(
                    -32600, "Invalid Request: request body must be a JSON object"
                ),
            )
            return create_http_response(200, error_response.to_json_dict())

        # Check for legacy REST payload format and convert to JSON-RPC 2.0
        # cy format: {"mcp_target": "github", "method": "tools/list", "params": {}}
        if "mcp_target" in body and "jsonrpc" not in body:
            logger.info("Converting legacy REST payload to JSON-RPC 2.0 format")
            # Convert to JSON-RPC format
            mcp_target = body.get("mcp_target")
            method = body.get("method")
            params = body.get("params", {})

            # Create JSON-RPC request with tool name prefix
            if method and mcp_target:
                # For methods like "tools/list", prefix the tool name with connector ID
                body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
                # Note: The tool name prefixing will be handled by the aggregator

        # Detect if this is a notification BEFORE validation
        # JSON-RPC 2.0: A notification is a request WITHOUT an 'id' member
        # Even invalid notifications must not receive a response
        is_notification = "id" not in body

        # Extract and validate the id field
        # JSON-RPC 2.0: id must be a string, number, or null
        # If invalid type, use None in error response
        request_id = body.get("id")
        if request_id is not None and not isinstance(request_id, (str, int, float)):
            # Invalid id type - use None in error response
            request_id = None

        # Validate JSON-RPC 2.0 format
        if "jsonrpc" not in body or body["jsonrpc"] != "2.0":
            # Don't respond to invalid notifications
            if is_notification:
                logger.info("Ignoring invalid notification (missing/invalid jsonrpc)")
                return create_http_response(204, {})
            error_response = create_jsonrpc_response(
                request_id,
                error=create_jsonrpc_error(
                    -32600, "Invalid Request: missing or invalid 'jsonrpc' field"
                ),
            )
            return create_http_response(200, error_response.to_json_dict())

        if "method" not in body:
            # Don't respond to invalid notifications
            if is_notification:
                logger.info("Ignoring invalid notification (missing method)")
                return create_http_response(204, {})
            error_response = create_jsonrpc_response(
                request_id,
                error=create_jsonrpc_error(
                    -32600, "Invalid Request: missing 'method' field"
                ),
            )
            return create_http_response(200, error_response.to_json_dict())

        # Parse JSON-RPC request
        try:
            jsonrpc_request = JSONRPCRequest(**body)
        except Exception as e:
            logger.error(f"Invalid JSON-RPC request format: {e}")
            # Don't respond to invalid notifications
            if is_notification:
                logger.info("Ignoring invalid notification (validation error)")
                return create_http_response(204, {})
            error_response = create_jsonrpc_response(
                request_id,
                error=create_jsonrpc_error(-32600, f"Invalid Request: {str(e)}"),
            )
            return create_http_response(200, error_response.to_json_dict())

        # Handle the request asynchronously
        # (is_notification already determined at line 414)
        jsonrpc_response = asyncio.run(
            handle_jsonrpc_request(jsonrpc_request, is_notification)
        )

        # If this was a notification (no id), don't send a response
        if jsonrpc_response is None:
            return create_http_response(204, {})

        # Return JSON-RPC response
        return create_http_response(200, jsonrpc_response.to_json_dict())

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        error_response = create_jsonrpc_response(
            None,
            error=create_jsonrpc_error(-32700, f"Parse error: {str(e)}"),
        )
        return create_http_response(200, error_response.to_json_dict())

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        error_response = create_jsonrpc_response(
            None,
            error=create_jsonrpc_error(-32603, f"Internal error: {str(e)}"),
        )
        return create_http_response(200, error_response.to_json_dict())
