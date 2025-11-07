"""fastMCP Proxyの実装"""
import logging
from typing import List
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient

from src.config.settings import settings
from src.config.models import MCPServerConfig, ProxyConfig

# ロギング設定
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPProxyServer:
    """MCP Proxyサーバー"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.proxy: Optional[FastMCP] = None
        
    def create_proxy(self) -> FastMCP:
        """プロキシサーバーを作成"""
        logger.info(f"Creating proxy server: {settings.proxy_name}")
        
        # メインのプロキシサーバーを作成
        proxy = FastMCP(
            name=settings.proxy_name,
            instructions="""
            This is an MCP Proxy Gateway that aggregates multiple MCP servers.
            You can access various MCP servers through a single endpoint.
            """
        )
        
        # 有効な各MCPサーバーをマウント
        enabled_servers = self.config.get_enabled_servers()
        
        if not enabled_servers:
            logger.warning("No enabled MCP servers found")
            return proxy
        
        logger.info(f"Mounting {len(enabled_servers)} MCP servers")
        
        for server_config in enabled_servers:
            try:
                self._mount_server(proxy, server_config)
            except Exception as e:
                logger.error(f"Failed to mount server {server_config.name}: {e}")
                continue
        
        self.proxy = proxy
        return proxy
    
    def _mount_server(self, proxy: FastMCP, server_config: MCPServerConfig):
        """個別のMCPサーバーをマウント"""
        logger.info(f"Mounting server: {server_config.name} ({server_config.endpoint})")
        
        # ProxyClientを作成
        backend = ProxyClient(server_config.endpoint)
        
        # サブプロキシとして作成
        sub_proxy = FastMCP.as_proxy(
            backend,
            name=server_config.name
        )
        
        # メインプロキシにマウント
        proxy.mount(sub_proxy, prefix=server_config.id)
        
        logger.info(f"Successfully mounted: {server_config.name} with prefix '{server_config.id}'")


def create_local_test_config() -> ProxyConfig:
    """ローカルテスト用の設定を作成"""
    return ProxyConfig(
        servers=[
            MCPServerConfig(
                id="test-echo",
                name="Test Echo Server",
                endpoint="http://127.0.0.1:8081/sse",  # 後で実際のサーバーに置き換え
                enabled=True,
                priority=1,
                metadata={"description": "Simple echo server for testing"}
            )
        ]
    )