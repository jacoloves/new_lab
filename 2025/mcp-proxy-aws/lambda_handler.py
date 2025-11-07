"""AWS Lambda用のハンドラー"""
import json
import logging
import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from typing import Dict, Any
from mangum import Mangum

from config.settings import settings
from handlers.proxy import MCPProxyServer, create_local_test_config

# ロギング設定
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level))


# グローバル変数でプロキシを保持（Lambda warm start対策）
_proxy_instance = None


def get_proxy():
    """プロキシインスタンスを取得（シングルトン）"""
    global _proxy_instance
    
    if _proxy_instance is None:
        logger.info("Initializing proxy server...")
        config = create_local_test_config()
        proxy_server = MCPProxyServer(config)
        _proxy_instance = proxy_server.create_proxy()
        logger.info("Proxy server initialized")
    
    return _proxy_instance


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda用のメインハンドラー
    
    Args:
        event: API Gatewayからのイベント
        context: Lambda実行コンテキスト
    
    Returns:
        API Gatewayへのレスポンス
    """
    try:
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        logger.info(f"Lambda invoked: {method} {path}")
        
        # ヘルスチェックエンドポイント
        if path == '/' or path == '/health':
            config = create_local_test_config()
            enabled_servers = config.get_enabled_servers()
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "status": "ok",
                    "service": "MCP Proxy Gateway",
                    "version": "0.1.0",
                    "servers": {
                        "total": len(config.servers),
                        "enabled": len(enabled_servers),
                        "list": [
                            {
                                "id": s.id,
                                "name": s.name,
                                "enabled": s.enabled
                            }
                            for s in config.servers
                        ]
                    }
                })
            }
        
        # MCPエンドポイント（/sse または /mcp/sse）
        if path.startswith('/sse') or path.startswith('/mcp'):
            # プロキシを取得
            proxy = get_proxy()
            
            # FastMCPのHTTPアプリを取得
            app = proxy.http_app()
            
            # MangumでASGI -> Lambda変換
            handler = Mangum(app, lifespan="off")
            
            # イベントを処理
            response = handler(event, context)
            
            return response
        
        # その他のパスは404
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Not Found",
                "message": f"Path {path} not found",
                "hint": "Try /health for status, or connect via MCP client to /sse"
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": str(e)
            })
        }


# ローカルテスト用
if __name__ == "__main__":
    test_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "isBase64Encoded": False
    }
    
    class MockContext:
        function_name = "mcp-proxy-local"
        memory_limit_in_mb = 512
        invoked_function_arn = "arn:aws:lambda:local:123456789012:function:mcp-proxy-local"
        aws_request_id = "local-test-id"
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))