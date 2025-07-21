locals {
  lambda_bucket      = "${var.stage}-lambda-assets-iac-book-project-shooonng-20250720"
  lambda_name        = "prinnt_event_py"
  ssm_parameter_name = "/lambda-zip/${var.stage}/${local.lambda_name}"
}

data "aws_ssm_parameter" "sha256" {
  name = local.ssm_parameter_name
}

data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy" "lambda_basic_execution" {
  name = "AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.stage}-${local.lambda_name}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

resource "aws_iam_role_policy_attachments_exclusive" "lambda_role_policy" {
  policy_arns = [data.aws_iam_policy.lambda_basic_execution.arn]
  role_name   = aws_iam_role.lambda_role.name
}

resource "aws_lambda_function" "print_event" {
  function_name = "${var.stage}-${local.lambda_name}-tf"
  s3_bucket     = local.lambda_bucket
  s3_key        = nonsensitive("${local.lambda_name}/${data.aws_ssm_parameter.sha256.value}.zip")
  runtime       = "python3.12"
  handler       = "main.handler"
  architectures = ["arm64"]
  timeout       = 30
  role          = aws_iam_role.lambda_role.arn
}
