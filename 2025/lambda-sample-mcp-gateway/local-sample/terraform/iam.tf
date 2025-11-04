resource "aws_iam_role" "lambda_role" {
  name = "mcp-proxy-lambda-role-${var.environment}"

  assume_role_policy = jsondecode({
    Version = "2012-10-17"
    Statement = [{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
            Service = "lambda.amazonaws.com"
        }
    }]
  })
}

# CloudWatch Logs permissions
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Parameter Store access policy
resource "aws_iam_role_policy" "parameter_store_access" {
  name = "parameter-store-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
            Effect = "Allow"
            Action = [
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParametersByPath"
            ]
            Resource = [
                "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/mcp-proxy/${var.environment}/*"
            ]
        },
        {
            Effect = "Allow"
            Action = [
                "kms:Decrypt"
            ]
            Resource = aws_kms_key.parameter_store.arn
        }
    ]
  })
}