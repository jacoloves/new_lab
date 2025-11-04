# Lambda function
resource "aws_lambda_function" "mcp_proxy" {
  filename = data.archive_file.lambda_zip.output_path
  function_name = "mcp-proxy-${var.environment}"
  role = aws_iam_role.lambda_role.arn
  handler = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime = "python3.11"
  timeout = var.lambda_timeout
  memory_size = var.lambda_memory_size

  environment {
    variables = {
      
    }
  }
}