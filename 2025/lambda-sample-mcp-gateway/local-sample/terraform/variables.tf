variable "aws_region" {
  description = "AWS region"
  type = string
  default = "ap-northeast-1"
}

variable "environment" {
  description = "Environment name"
  type = string
  default = "dev"
}

variable "allowed_ip" {
  description = "Allowed source IP address"
  type = string
  default = "60.119.75.95/32"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type = number
  default = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type = number
  default = 1024
}