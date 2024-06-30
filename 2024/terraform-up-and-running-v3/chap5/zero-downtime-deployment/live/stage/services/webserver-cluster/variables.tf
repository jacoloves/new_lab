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

variable "server_text" {
  description = "The text for each EC2 instance to display. You can change this text to force a redeploy"
  type        = string
  default     = "New server text"
}
