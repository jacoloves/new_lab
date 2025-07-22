locals {
  lambda_name           = "lambda_print_event_go"
  lambda_bucket         = "${var.stage}-lambda-deploy-shooonng-20250721-apne1"
  lambda_local_code_dir = abspath("${path.module}/../../../lambda/print_event_go")
}

data "external" "create_asset_zip" {
  program = ["sh", "${path.module}/../../../scripts/create_asset_zip.sh"]
  query = {
    lambda_local_code_dir = local.lambda_local_code_dir
    lambda_name           = local.lambda_name
    method                = "DOCKER"
    dockerfile            = "${local.lambda_local_code_dir}/Dockerfile.build"
  }
}

resource "terraform_data" "upload_zip_s3" {
  provisioner "local-exec" {
    command = "aws s3 cp ${data.external.create_asset_zip.result.zipfile} s3://${local.lambda_bucket}/${local.lambda_name}/"
  }
  triggers_replace = [
    basename(data.external.create_asset_zip.result.zipfile),
  ]
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

resource "aws_iam_role" "lambda" {
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
  name               = "${var.stage}-${local.lambda_name}-lambda-role"
}

resource "aws_iam_role_policy_attachments_exclusive" "lambda_managed_policy" {
  policy_arns = [data.aws_iam_policy.lambda_basic_execution.arn]
  role_name   = aws_iam_role.lambda.name
}

resource "aws_lambda_function" "print_event" {
  function_name = "${var.stage}-${local.lambda_name}-tf"
  s3_bucket     = local.lambda_bucket
  s3_key        = "${local.lambda_name}/${basename(data.external.create_asset_zip.result.zipfile)}"
  runtime       = "provided.al2023"
  handler       = "bootstrap"
  memory_size   = 128
  timeout       = 30
  architectures = ["arm64"]
  role          = aws_iam_role.lambda.arn
  depends_on    = [terraform_data.upload_zip_s3]
}
