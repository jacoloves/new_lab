variable "vpc_id" {
  description = "サブネットを作成するVPCのID"
  type        = string
}

variable "name_prefix" {
  description = "サブネット名の接頭辞(例: sbcntr-private-app)。末尾に-a/-cが付与される"
  type        = string
}

variable "type_tag" {
  description = "Typeタグの値(例: Isolated, Public)"
  type        = string
}

variable "cidr_block_a" {
  description = "a側サブネットのCIDRブロック"
  type        = string
}

variable "cidr_block_c" {
  description = "c側サブネットのCIDRブロック"
  type        = string
}

variable "availability_zone_a" {
  description = "a側サブネットのアベイラビリティゾーン"
  type        = string
}

variable "availability_zone_c" {
  description = "c側サブネットのアベイラビリティゾーン"
  type        = string
}

variable "map_public_ip_on_launch" {
  description = "起動したインスタンスにパブリックIPを自動割り当てするかどうか"
  type        = bool
  default     = false
}
