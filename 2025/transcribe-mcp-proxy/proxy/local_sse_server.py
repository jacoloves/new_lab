#!/usr/bin/env python
"""
Local SSE Server for MCP Proxy

This server provides an SSE endpoint for MCP clients (like VSCode or Claude Desktop)
to connect to the MCP Proxy Lambda locally.

Usage:
    export CONFIG_SOURCE=file
    export MCP_CONFIG_FILE=$(pwd)/local-config/connectors.json
    export SECRETS_DIR=$(pwd)/local-config/secrets
    python local_sse_server.py

Then configure your MCP client:
    {
      "mcpServers": {
        "proxy": {
          "type": "sse",
          "url": "http://localhost:3000/sse"
        }
      }
    }
"""

import asyncio
import json
import logging
import os
import queue
import threading
from typing import Dict, Any, Optional
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS

from app.handler import handle_jsonrpc_request
from app.models import JSONRPCRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s = %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class SSESession:
    """Manages an SSE session with a client"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.message_queue = queue.Queue()
        self.is_active = True
        logger.info(f"Created SSE session: {session_id}")

    def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send an event to the client"""
        if not self.is_active:
            return

        event_data = json.dumps(data, ensure_ascii=False)
        sse_message = f"event: {event_type}\ndata: {event_data}\n\n"
        self.message_queue.put(sse_message)
        logger.debug(f"Queued event {event_type} for session {self.session_id}")

    def send_message(self, message: str):
        """Send a raw message to the client"""
        if not self.is_active:
            return
        self.message_queue.put(message)

    def close(self):
        """Close the session"""
        self.is_active = False
        logger.info(f"Closed SSE session: {self.session_id}")


# Global session storage
sessions: Dict[str, SSESession] = {}


def generate_sse_stream(session: SSESession):
    """Generate SSE event stream for a client"""
    try:
        # Send initial connection confirmation
        yield f"event: connected\ndata: {json.dumps({'session_id': session.session_id})}\n\n"

        # Keep connection alive and send messages
        while session.is_active:
            try:
                # Wait for messages with timeout for keepalive
                message = session.message_queue.get(timeout=15)
                yield message
            except queue.Empty:
                # Send keepalive ping
                yield f": keepalive\n\n"
                continue

    except GeneratorExit:
        logger.info(f"Client disconnected from session {session.session_id}")
        session.close()

    except Exception as e:
        logger.error(f"Error in SSE stream: {e}", exc_info=True)
        session.close()


def handle_jsonrpc_in_thread(session: SSESession, jsonrpc_data: Dict[str, Any]):
    """Handle JSON-RPC request in a separate thread and send response via SSE"""

    async def process_request():
        try:
            # Detect if this is a notification
            is_notification = "id" not in jsonrpc_data

            # Parse and validate JSON-RPC request
            jsonrpc_request = JSONRPCRequest(**jsonrpc_data)

            # Handle the request using the existing handler
            response = await handle_jsonrpc_request(jsonrpc_request, is_notification)

            # Send response via SSE (skip for notifications)
            if response is not None:
                session.send_event("message", response.model_dump())

        except Exception as e:
            logger.error(f"Error processing JSON-RPC request: {e}", exc_info=True)
            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": jsonrpc_data.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }
            session.send_event("message", error_response)

    # Run async function in new event loop (since we're in a thread)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_request())
    finally:
        loop.close()


@app.route("/sse", methods=["GET", "POST"])
def sse_endpoint():
    """
    SSE endpoint for MCP clients (MCP SSE Transport compliant)

    POST: Establish SSE connection and send initial request
    GET: Legacy support for establishing SSE connection
    """
    if request.method == "POST":
        # MCP SSE standard: POST establishes SSE connection and sends initial request
        # Create a new session
        session_id = os.urandom(16).hex()
        session = SSESession(session_id)
        sessions[session_id] = session

        logger.info(f"Client connected via POST to SSE endpoint: {session_id}")

        # Check if there's a JSON-RPC request in the body
        try:
            if request.content_type == "application/json" and request.data:
                jsonrpc_data = request.get_json()

                # Process request in background thread
                thread = threading.Thread(
                    target=handle_jsonrpc_in_thread, args=(session, jsonrpc_data)
                )
                thread.daemon = True
                thread.start()
        except Exception as e:
            logger.warning(f"No JSON-RPC request in POST body or error parsing: {e}")

        # Return SSE stream
        return Response(
            stream_with_context(generate_sse_stream(session)),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    elif request.method == "GET":
        # Legacy support: GET to establish SSE connection
        session_id = request.args.get("session_id", os.urandom(16).hex())
        session = SSESession(session_id)
        sessions[session_id] = session

        logger.info(f"Client connected via GET to SSE endpoint: {session_id}")

        return Response(
            stream_with_context(generate_sse_stream(session)),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )


@app.route("/message", methods=["POST"])
def mesage_endpoint():
    """
    Alternative endpoint for sending JSON-RPC messages
    This is for MCP clients that use a separate endpoint for sending messages
    """
    try:
        # Get session ID
        session_id = request.headers.get("X-Session-ID") or request.args.get(
            "session_id"
        )

        if not session_id or session_id not in sessions:
            return json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32000,
                        "message": "Invalid or missing session_id",
                    },
                }
            ), 400

        session = sessions[session_id]

        # Parse JSON-RPC request
        jsonrpc_data = request.get_json()

        # Process request in background thread
        thread = threading.Thread(
            target=handle_jsonrpc_in_thread, args=(session, jsonrpc_data)
        )
        thread.daemon = True
        thread.start()

        # Return acknowledgment
        return "", 202

    except Exception as e:
        logger.error(f"Error in message endpoint: {e}", exc_info=True)
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }
        ), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return json.dumps(
        {
            "status": "healthy",
            "service": "MCP Proxy SSE Server (Local)",
            "active_sessions": len([s for s in sessions.values() if s.is_active]),
        }
    )


def main():
    """Start the local SSE server"""
    # Check environment variables
    config_source = os.environ.get("CONFIG_SOURCE")
    if config_source == "file":
        config_file = os.environ.get("MCP_CONFIG_FILE")
        secrets_dir = os.environ.get("SECRETS_DIR")
        logger.info("Using file-based configuration:")
        logger.info(f"  CONFIG_FILE: {config_file}")
        logger.info(f"  SECRETS_DIR: {secrets_dir}")
    else:
        logger.warning(f"CONFIG_SOURCE is set to: {config_source}")
        logger.warning("For local development, use CONFIG_SOURCE=file")

    # Start server
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting MCP Proxy SSE Server on http://localhost:{port}")
    logger.info(f"SSE endpoint: http://localhost:{port}/sse")
    logger.info("Press Ctrl+C to stop")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
