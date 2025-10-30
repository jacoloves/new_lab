variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the instance"
  type        = list(string)
  default     = ["0.0.0.0/0"] # 本番環境では自分のIPに限定することを推奨
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "mcp-proxy-server"
}
