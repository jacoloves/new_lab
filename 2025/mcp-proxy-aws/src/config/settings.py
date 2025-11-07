"""アプリケーション設定"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """環境変数から設定を読み込む"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # AWS設定
    aws_region: str = "ap-northeast-1"
    dynamodb_table_name: str = "mcp-servers"
    secrets_manager_prefix: str = "mcp/tokens/"
    
    # アプリケーション設定
    local_mode: bool = True
    log_level: str = "INFO"
    proxy_name: str = "MCP-Proxy-Gateway"
    
    # サーバー設定（ローカル開発用）
    host: str = "127.0.0.1"
    port: int = 8080


# シングルトンインスタンス
settings = Settings()