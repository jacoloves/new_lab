data "archive_file" "put_s3_object_lambda_zip" {
  output_path = "./lambda_function.zip"
  source_file = "../../../lambda/put_s3_object/main.py" # 実際のパスに合わせて修正
  type        = "zip"
}

data "aws_iam_policy_document" "lambda_exec_assume_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy" "lambda_basic_role" {
  name = "AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "put_s3_object_lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "put_s3_object_tf_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec_assume_role_policy.json
}

resource "aws_iam_role_policy_attachments_exclusive" "lambda_inline_policy" {
  policy_arns = [data.aws_iam_policy.lambda_basic_role.arn]
  role_name   = aws_iam_role.lambda_exec.name
}

resource "aws_iam_role_policy" "lambda_inline_policy" {
  name   = "put_s3_object_lambda_policy_tf"
  policy = data.aws_iam_policy_document.put_s3_object_lambda_policy.json
  role   = aws_iam_role.lambda_exec.name
}

resource "aws_lambda_function" "put_s3_object" {
  filename         = data.archive_file.put_s3_object_lambda_zip.output_path
  function_name    = "put_s3_object_tf"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.lambda_handler"
  source_code_hash = filebase64sha256(data.archive_file.put_s3_object_lambda_zip.output_path)
  runtime          = "python3.12"
  timeout          = 10
}

data "aws_caller_identity" "current" {}

resource "aws_lambda_invocation" "put_s3_object" {
  function_name = aws_lambda_function.put_s3_object.function_name
  input = jsonencode({
    resource_properties = {
      bucket = "${data.aws_caller_identity.current.account_id}-test-bucket",
      key    = "test-key-tf",
      body   = "Hello, S3!"
    }
  })
  lifecycle_scope = "CRUD"
}
