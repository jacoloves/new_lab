variable "stage" {
  description = "The stage of the environment, e.g., dev, test, prod"
  type        = string
}


variable "queue_name_suffix" {
  description = "Suffix to append to the SQS queue name"
  type        = string
}

variable "sqs_queue_visibility_timeout" {
  description = "Visibility timeout for the SQS queue in seconds"
  type        = number
  default     = 30
}
