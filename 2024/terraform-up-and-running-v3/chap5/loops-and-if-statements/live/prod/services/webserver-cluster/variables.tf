variable "db_remote_state_bucket" {
  description = "The name of the S3 bucket used for the database's remote state storage"
  type        = string
}

variable "db_remote_state_key" {
  description = "The name of the key in the S3 bucket used for the database's remote state stotage"
  type        = string
}

variable "cluster_name" {
  description = "The name to use to namespace all the resources in the cluster"
  type        = string
  default     = "webservers-prod"
}
