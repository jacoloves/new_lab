"""MCP Aggregator for combining multiple MCP servers into a single proxy"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

from .config_loader import get_config_loader
from .mcp_wrapper import get_client_manager, MCPConnectionError
from .models import Tool, Resource, Prompt

logger = logging.getLogger(__name__)


class MCPAggregator:
    """Aggregates tools, resources, and prompts from multiple MCP servers"""

    def __init__(self):
        """Initialize the aggregator"""
        self._config_loader = get_config_loader()
        self._client_manager = get_client_manager()
        self._separator = "__"

    def _prefix_tool_name(self, connector_id: str, tool_name: str) -> str:
        """
        Prefix a tool name with its connector ID

        Args:
            connector_id: The connector ID
            tool_name: The original tool name

        Returns:
            Prefixed tool name (e.g., "github__get_pull_request")
        """
        return f"{connector_id}{self._separator}{tool_name}"

    def _parse_tool_name(self, prefixed_tool_name: str) -> tuple[str, str]:
        """
        Parse a prefixed tool name to extract connector ID and original name

        Args:
            prefixed_tool_name: The prefixed tool name

        Returns:
            Tuple of (connector_id, original_tool_name)

        Raises:
            ValueError: If the tool name format is invalid
        """
        if self._separator not in prefixed_tool_name:
            raise ValueError(f"Invalid tool name format: {prefixed_tool_name}")

        parts = prefixed_tool_name.split(self._separator, 1)
        return parts[0], parts[1]

    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        Aggregate tools from all configured MCP servers

        Returns:
            List of all tools with prefixed names
        """
        # Load all connectors
        connectors = self._config_loader.load_connectors()

        if not connectors:
            logger.warning("No connectors configured")
            return []

        # Fetch tools from all connectors in parallel
        tasks = []
        connector_ids = []

        for connector_id in connectors.keys():
            logger.info(f"Fetching tools from connector: {connector_id}")
            task = self._client_manager.call_connector(connector_id, "tools/list", {})
            tasks.append(task)
            connector_ids.append(connector_id)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_tools = []
        for connector_id, result in zip(connector_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch tools from {connector_id}: {result}")
                continue

            # Extract tools from result
            tools = result.get("tools", [])
            logger.info(f"Got {len(tools)} tools from {connector_id}")

            # Prefix tool names and add to aggregated list
            for tool in tools:
                original_name = tool.get("name", "")
                prefixed_name = self._prefix_tool_name(connector_id, original_name)

                # Create a copy with the prefixed name
                prefixed_tool = tool.copy()
                prefixed_tool["name"] = prefixed_name

                # Add metadata about the source connector
                if "description" in prefixed_tool:
                    prefixed_tool["description"] = (
                        f"[{connector_id}] {prefixed_tool['description']}"
                    )

                all_tools.append(prefixed_tool)

        logger.info(
            f"Aggregated {len(all_tools)} tools from {len(connectors)} connectors"
        )
        return all_tools

    async def list_all_resources(self) -> List[Dict[str, Any]]:
        """
        Aggregate resources from all configured MCP servers

        Returns:
            List of all resources with prefixed URIs
        """
        connectors = self._config_loader.load_connectors()

        if not connectors:
            logger.warning("No connectors configured")
            return []

        # Fetch resources from all connectors in parallel
        tasks = []
        connector_ids = []

        for connector_id in connectors.keys():
            logger.info(f"Fetching resources from connector: {connector_id}")
            task = self._client_manager.call_connector(
                connector_id, "resources/list", {}
            )
            tasks.append(task)
            connector_ids.append(connector_id)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_resources = []
        for connector_id, result in zip(connector_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch resources from {connector_id}: {result}")
                continue

            # Extract resources from result
            resources = result.get("resources", [])
            logger.info(f"Got {len(resources)} resources from {connector_id}")

            # Prefix resource URIs and add to aggregated list
            for resource in resources:
                # Add metadata about the source connector
                prefixed_resource = resource.copy()
                if "name" in prefixed_resource:
                    prefixed_resource["name"] = (
                        f"[{connector_id}] {prefixed_resource['name']}"
                    )

                # Prefix the URI for deterministic routing
                # Format: connector_id://original_uri
                if "uri" in prefixed_resource:
                    original_uri = prefixed_resource["uri"]
                    prefixed_resource["uri"] = f"{connector_id}://{original_uri}"

                all_resources.append(prefixed_resource)

        logger.info(
            f"Aggregated {len(all_resources)} resources from {len(connectors)} connectors"
        )
        return all_resources

    async def list_all_prompts(self) -> List[Dict[str, Any]]:
        """
        Aggregate prompts from all configured MCP servers

        Returns:
            List of all prompts with prefixed names
        """
        connectors = self._config_loader.load_connectors()

        if not connectors:
            logger.warning("No connectors configured")
            return []

        # Fetch prompts from all connectors in parallel
        tasks = []
        connector_ids = []

        for connector_id in connectors.keys():
            logger.info(f"Fetching prompts from connector: {connector_id}")
            task = self._client_manager.call_connector(connector_id, "prompts/list", {})
            tasks.append(task)
            connector_ids.append(connector_id)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_prompts = []
        for (
            connector_id,
            result,
        ) in zip(connector_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch prompts from {connector_id}: {result}")
                continue

            # Extract prompts from result
            prompts = result.get("prompts", [])
            logger.info(f"Got {len(prompts)} prompts from {connector_id}")

            # Prefix prompt names and add to aggregated list
            for prompt in prompts:
                original_name = prompt.get("name", "")
                prefixed_name = self._prefix_tool_name(connector_id, original_name)

                # Create a copy with the prefixed name
                prefixed_prompt = prompt.copy()
                prefixed_prompt["name"] = prefixed_name

                # Add metadata about the source connector
                if "description" in prefixed_prompt:
                    prefixed_prompt["description"] = (
                        f"[{connector_id}] {prefixed_prompt['description']}"
                    )

                all_prompts.append(prefixed_prompt)

        logger.info(
            f"Aggregated {len(all_prompts)} prompts from {len(connectors)} connectors"
        )
        return all_prompts

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the appropriate backend MCP server

        Args:
            tool_name: The prefixed tool name (e.g., "github__get_pull_request")
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If the tool name format is invalid (client error)
            MCPConnectionError: If the tool call fails (server error)
        """
        # Parse the tool name to get connector ID and original tool name
        # Let ValueError propagate - it's a client error (invalid params)
        connector_id, original_tool_name = self._parse_tool_name(tool_name)

        logger.info(f"Calling tool {original_tool_name} on connector {connector_id}")

        try:
            # Call the tool on the backend server
            result = await self._client_manager.call_connector(
                connector_id,
                "tools/call",
                {"name": original_tool_name, "arguments": arguments},
            )

            return result

        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise MCPConnectionError(f"Tool call failed: {e}")

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource from the appropriate backend MCP server

        Args:
            uri: The resource URI (prefixed format: connector_id://original_uri or standard URI)

        Returns:
            Resource content

        Raises:
            MCPConnectionError: If the resource read fails
        """
        # Load connectors to check if prefix matches a known connector
        connectors = self._config_loader.load_connectors()

        # Parse the URI to extract pntential connector ID
        # Format: connector_id://original_uri
        # But only treat as prefix if connector_id matches a known connector
        if "://" in uri:
            parts = uri.split("://", 1)
            if len(parts) == 2:
                potential_connector_id = parts[0]

                # Check if this is actually a connector prefix (not file://, https://, etc.)
                if potential_connector_id in connectors:
                    original_uri = parts[1]
                    logger.info(
                        f"Reading resource {original_uri} from connector {potential_connector_id}"
                    )

                    try:
                        result = await self._client_manager.call_connector(
                            potential_connector_id,
                            "resource/read",
                            {"uri": original_uri},
                        )
                        return result
                    except Exception as e:
                        logger.error(
                            f"Failed to read resource from {potential_connector_id}: {e}"
                        )
                        raise MCPConnectionError(
                            f"Connector {potential_connector_id} failed to read resource {original_uri}: {e}"
                        )

        # Fallback: try all connectors (for non-prefixed URIs or real URIs like file://, https://)
        logger.info(f"Trying all connectors for URI: {uri}")

        for connector_id in connectors.keys():
            try:
                logger.debug(
                    f"Trying to read resource {uri} from connector {connector_id}"
                )
                result = await self._client_manager.call_connector(
                    connector_id, "resources/read", {"uri": uri}
                )
                logger.info(f"Successfully read resource from connector {connector_id}")
                return result
            except Exception as e:
                logger.debug(f"Connector {connector_id} failed to read resource: {e}")
                continue

        raise MCPConnectionError(f"No connector could read resource: {uri}")

    async def get_prompt(
        self, prompt_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a prompt from the appropriate backend MCP server

        Args:
            prompt_name: The prefixed prompt name
            arguments: Optional prompt arguments

        Returns:
            Prompt content

        Raises:
            ValueError: If the prompt name format is invalid (client error)
            MCPConnectionError: If the prompt retrieval fails (server error)
        """
        # Parse the prompt name to get connector ID and original prompt name
        # Let ValueError propagate - it's a client error (invalid params)
        connector_id, original_prompt_name = self._parse_tool_name(prompt_name)

        logger.info(
            f"Getting prompt {original_prompt_name} from connector {connector_id}"
        )

        try:
            # Get the prompt from the backend server
            params = {"name": original_prompt_name}
            if arguments:
                params["arguments"] = arguments

            result = await self._client_manager.call_connector(
                connector_id, "prompts/get", params
            )

            return result

        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_name}: {e}")
            raise MCPConnectionError(f"Prompt retrieval failed: {e}")


# Global aggregator instance
_aggregator: Optional[MCPAggregator] = None


def get_aggregator() -> MCPAggregator:
    """Get the global aggregator instance"""
    global _aggregator
    if _aggregator is None:
        _aggregator = MCPAggregator()
    return _aggregator
