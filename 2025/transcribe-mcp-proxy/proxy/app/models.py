"""Data models for MCP Proxy"""

from typing import Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, model_validator


class MCPConnector(BaseModel):
    """MCP Connector configuration model"""

    id: str = Field(..., description="Unique identifier for the connector")
    type: Literal["rest", "stdio", "sse", "http"] = Field(
        ..., description="Connection type"
    )
    endpoint: Optional[str] = Field(
        None, description="Endpoint URL for REST/SSE/HTTP connectors"
    )
    url: Optional[str] = Field(
        None, description="URL for HTTP connectors (MCP standard alias for endpoint)"
    )
    command: Optional[str] = Field(None, description="command for stdio connectors")
    args: Optional[list[str]] = Field(
        None, description="Arguments for stdio connectors"
    )
    secret_arn: Optional[str] = Field(
        None, description="ARN of the secret in Secrets Manager"
    )
    headers: Optional[Dict[str, str]] = Field(
        None, description="Custom HTTP headers for HTTP connectors"
    )
    timeout: int = Field(30, description="Timeout in seconds for the connection")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @model_validator(mode="after")
    def validate_url_endpoint(self):
        """Ensure url and endpoint are synchronized"""
        # If url is provided but not endpoint, copy url to endpoint
        if self.url and not self.endpoint:
            self.endpoint = self.url
        # If endpoint is provided but not url, copy endpoint to url
        elif self.endpoint and not self.url:
            self.url = self.endpoint
        # If both are provided, they should be the same
        elif self.url and self.endpoint and self.url != self.endpoint:
            raise ValueError("Both 'url' and 'endpoint' are provided but they differ")
        return self


# Legacy models (kept for backward compatibility)
class MCPRequest(BaseModel):
    """MCP Request from client (legacy format)"""

    mcp_target: str = Field(..., description="Target MCP connector ID")
    method: str = Field(..., description="MCP method to call")
    params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Parameters for the method"
    )


class MCPResponse(BaseModel):
    """MCP Response to client (legacy format)"""

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    connector_id: Optional[str] = Field(
        None, description="ID of the connector that handled the request"
    )


# JSON-RPC 2.0 Models (MCP Protocol compliant)
class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 Error object"""

    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""

    jsonrpc: Literal["2.0"] = Field("2.0", description="JSON-RPC version")
    id: Optional[Union[str, int, float]] = Field(
        None, description="Request ID (null for notifications)"
    )
    method: str = Field(..., description="Method name")
    params: Optional[Union[Dict[str, Any], list]] = Field(
        None, description="Method parameters (object or array)"
    )


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""

    jsonrpc: Literal["2.0"] = Field("2.0", description="JSON-RPC version")
    id: Optional[Union[str, int, float]] = Field(..., description="Request ID")
    result: Optional[Any] = Field(None, description="Result (if success)")
    error: Optional[JSONRPCError] = Field(None, description="Error (if failure)")

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Serialize to JSON-RPC 2.0 compliant dectionary

        JSON-RPC 2.0 requires:
        - id field always present (can be null)
        - Either result or error, not both
        """
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
        }

        if self.error is not None:
            response["error"] = self.error.model_dump()
        else:
            response["result"] = self.result

        return response


# MCP Protocol Specific Models
class ServerCaapabilities(BaseModel):
    """MCP Server capabilities"""

    tools: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Tool capabilities"
    )
    resources: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Resource capabilities"
    )
    prompts: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Prompt capabilities"
    )
    logging: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Logging capabilities"
    )


class ServerInfo(BaseModel):
    """MCP Server information"""

    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")


class InitializeResult(BaseModel):
    """Result of initialize method"""

    protocolVersion: str = Field("2025-11-05", description="MCP protocol version")
    capabilities: ServerCaapabilities = Field(
        default_factory=ServerCaapabilities, description="Server capabilities"
    )
    serverInfo: ServerInfo = Field(..., description="Server information")


class Tool(BaseModel):
    """MCP Tool definition"""

    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="JSON Schema for tool input")


class Resource(BaseModel):
    """MCP Resource definition"""

    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    mimeType: Optional[str] = Field(None, description="MIME type")


class Prompt(BaseModel):
    """MCP Prompt definition"""

    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    arguments: Optional[list[Dict[str, Any]]] = Field(
        None, description="Prompt arguments"
    )
