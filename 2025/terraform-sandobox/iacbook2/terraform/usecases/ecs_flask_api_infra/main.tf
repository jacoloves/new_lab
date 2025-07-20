resource "aws_ecr_repository" "flask_api" {
  name = "${var.stage}-flask-api-tf"
}

resource "aws_ssm_parameter" "flask_api_correct_answer" {
  name  = "/flask-apitf/${var.stage}/correct_answer"
  type  = "SecureString"
  value = "uninitialized"
  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
