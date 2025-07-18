variable "stage" {
  type        = string
  description = "The stage of the environment, e.g., dev, prod."
}

variable "vpc_cidr" {
  type        = string
  description = "value of the VPC CIDR block"
}

variable "enable_nat_gateway" {
  type        = bool
  description = "value to enable NAT Gateway"
}

variable "one_nat_gateway_per_az" {
  type        = bool
  default     = false
  description = "value to create one NAT Gateway per Availability Zone"
}
