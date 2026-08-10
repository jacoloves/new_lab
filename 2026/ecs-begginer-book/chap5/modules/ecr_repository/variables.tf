variable "name" {
  description = "ECRリポジトリ名"
  type        = string
}

variable "image_tag_mutability" {
  description = "イメージタグの上書き可否(MUTABLE/IMMUTABLE)"
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "プッシュ時の脆弱性スキャンを有効化するかどうか"
  type        = string
  default     = false
}
