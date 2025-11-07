"""テスト用のシンプルなMCPエコーサーバー"""
from fastmcp import FastMCP

# シンプルなエコーサーバー
echo_server = FastMCP(name="Echo Server")


@echo_server.tool()
def echo(message: str) -> str:
    """メッセージをエコーバックする"""
    return f"Echo: {message}"


@echo_server.tool()
def add(a: int, b: int) -> int:
    """2つの数値を足す"""
    return a + b


@echo_server.resource("echo://info")
def get_info() -> str:
    """サーバー情報を返す"""
    return "This is a simple echo server for testing MCP Proxy"


if __name__ == "__main__":
    print("🎤 Starting Echo Server on port 8081...")
    echo_server.run(transport="sse", host="127.0.0.1", port=8081)