resource "aws_sqs_queue" "default_region" {
  name                       = "${var.stage}-${var.queue_name_suffix}-default-region"
  visibility_timeout_seconds = var.sqs_queue_visibility_timeout_seconds
  max_message_size           = 2048
}

resource "aws_sqs_queue" "another_region" {
  name                       = "${var.stage}-${var.queue_name_suffix}-another-region"
  visibility_timeout_seconds = var.sqs_queue_visibility_timeout_seconds
  max_message_size           = 2048
  provider                   = aws.another_region
}
