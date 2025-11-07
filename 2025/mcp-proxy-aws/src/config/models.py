"""データモデル定義"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class MCPServerConfig(BaseModel):
    """MCPサーバーの設定"""
    
    id: str = Field(..., description="サーバーID")
    name: str = Field(..., description="サーバー名")
    endpoint: str = Field(..., description="エンドポイントURL")
    token_path: Optional[str] = Field(None, description="トークンのSecrets Managerパス")
    enabled: bool = Field(True, description="有効/無効")
    priority: int = Field(1, description="優先度（数字が小さいほど優先）")
    rate_limit: int = Field(100, description="1分あたりのリクエスト数制限")
    timeout: int = Field(30000, description="タイムアウト（ミリ秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "github-mcp",
                "name": "GitHub MCP Server",
                "endpoint": "stdio://github-mcp-server",
                "token_path": "mcp/tokens/github",
                "enabled": True,
                "priority": 1,
                "rate_limit": 100,
                "timeout": 30000,
                "metadata": {
                    "version": "1.0.0",
                    "description": "GitHub integration"
                }
            }
        }


class ProxyConfig(BaseModel):
    """プロキシ全体の設定"""
    
    servers: List[MCPServerConfig] = Field(default_factory=list)
    
    def get_enabled_servers(self) -> List[MCPServerConfig]:
        """有効なサーバーのみを取得"""
        return sorted(
            [s for s in self.servers if s.enabled],
            key=lambda x: x.priority
        )