"""Lambda関数のエントリーポイント"""
import json
import logging
from typing import Dict, Any

from src.config.settings import settings
from src.handlers.proxy import MCPProxyServer, create_local_test_config

logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda関数のハンドラー
    
    Args:
        event: API Gatewayからのイベント
        context: Lambda実行コンテキスト
    
    Returns:
        API Gatewayへのレスポンス
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # プロキシ設定を読み込み（現時点ではハードコード）
        config = create_local_test_config()
        
        # プロキシサーバーを作成
        proxy_server = MCPProxyServer(config)
        proxy = proxy_server.create_proxy()
        
        # TODO: 実際のMCPリクエスト処理を実装
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "MCP Proxy Gateway",
                "servers": len(config.get_enabled_servers())
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def run_local_server():
    """ローカル開発用サーバーを起動"""
    print(f"🚀 Starting MCP Proxy Server on {settings.host}:{settings.port}")
    print(f"📝 Log level: {settings.log_level}")
    print(f"🔧 Local mode: {settings.local_mode}")
    
    # テスト用設定でプロキシを作成
    config = create_local_test_config()
    proxy_server = MCPProxyServer(config)
    proxy = proxy_server.create_proxy()
    
    # HTTPサーバーとして起動
    print(f"\n✅ Server is running!")
    print(f"🌐 Access: http://{settings.host}:{settings.port}")
    print(f"📊 Mounted servers: {len(config.get_enabled_servers())}")
    
    proxy.run(
        transport="sse",  # Server-Sent Events
        host=settings.host,
        port=settings.port
    )


if __name__ == "__main__":
    # ローカルで直接実行された場合
    run_local_server()