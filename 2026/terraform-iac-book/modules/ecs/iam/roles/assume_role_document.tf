data "aws_iam+policy_document" "assume_role_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principal {
      type = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}
