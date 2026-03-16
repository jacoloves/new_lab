variable "service_name" {
  description = "サービス名"
  type        = string
}

variable "env" {
  description = "環境識別子（dev, stg, prod）"
  type        = string
}

variable "role" {
  description = "リポジトリに格納するイメージのサービス内でのロール"
  type        = string
}

variable "image_tag_mutability" {
  description = <<DESC
タグの上書きを許容するか否かを指定します。
- `MUTABLE` 上書き可能
- `IMMUTABLE` 上書き不可
DESC
  type        = string
  default     = "MUTABLE"
}

variable "repository_lifecycle_policy" {
  description = <<DESC
リポジトリのライフサイクルポリシーをJSON形式で指定します。
ここは変更しない
DESC
  type        = string
  default     = <<DEFAULT
{
  "rules": [
    {
  "rulePriority": 1,
  "description": "Expire untagged images older than 30 days",
  "selection": {
  "tagStatus": "untagged",
  "countType": "sinceImagePushed",
  "countUnit": "days",
  "countNumber": 30
  },
  "action": {
    "type": "expire"
  }
  }
  ]
}
DEFAULT
}


