variable "vpc_id" {
  description = "VPCエンドポイントを作成するVPCのID"
  type        = string
}

variable "service_name" {
  description = "接続先のAWSサービス名(例: com.amazonaws.ap-northeast-1.ecr.api)"
  type        = string
}

variable "subnet_ids" {
  description = "エンドポイント用ENIを配置するサブネットIDのリスト"
  type        = list(string)
}

variable "security_group_ids" {
  description = "エンドポイントのENIに適用するセキュリティグループIDのリスト"
  type        = list(string)
}

variable "name" {
  description = "リソースのNameタグに設定する値"
  type        = string
}

variable "private_dns_enabled" {
  description = "プライベートDNS名を有効化するかどうか"
  type        = bool
  default     = true
}
