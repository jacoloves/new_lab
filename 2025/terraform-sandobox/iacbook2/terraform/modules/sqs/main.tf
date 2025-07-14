resource "aws_sqs_queue" "this" {
  name                       = "${var.stage}-${var.queue_name_suffix}"
  visibility_timeout_seconds = var.sqs_queue_visibility_timeout
  max_message_size           = 2048
}
