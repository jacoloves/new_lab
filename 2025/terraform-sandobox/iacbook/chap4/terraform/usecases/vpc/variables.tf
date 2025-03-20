variable "stage" {
  type = string
  description = "stage: dev, prd"
}
variable "vpc_cidr" {
  type = string
  description = "CIDR of CIDR. ex: 10.0.0.0/16"
}
variable "enable_nat_gateway" {
  type = bool
  description = "use Nat Gateway"
}
variable "one_nat_gateway_per_az" {
  type = bool
  default = false
  description = "Install one Nat Gateway per AZ"
}
