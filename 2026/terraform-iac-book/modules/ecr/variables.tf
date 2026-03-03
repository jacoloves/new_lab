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
