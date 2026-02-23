variable "service_name" {
  description = "VPCを利用するサービス名"
  type        = string
}

variable "env" {
  description = "環境識別子（dev, stg, prod）"
  type        = string
}

variable "cluster_additional_tags" {
  description = "ECSクラスターに付与したい追加タグ"
  type        = map(string)
  default     = {}

  validation {
    condition     = length(setintersection(keys(var.cluster_additional_tags), ["ServiceName", "Env"])) == 0
    error_message = "Key names, ServiceName and Env is reserved. Not allowed to use them."
  }
}
