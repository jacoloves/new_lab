resource "aws_sqs_queue" "my_queue_2" {
  name             = "test-queue-tf-2"
  max_message_size = 2048
  tags = {
    "name" = "test-queue-tf-2"
  }
}
