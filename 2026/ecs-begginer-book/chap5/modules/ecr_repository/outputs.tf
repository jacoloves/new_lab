output "repository_url" {
  description = "ECRリポジトリのURL(イメージのpush/pull先)"
  value       = aws_ecr_repository.this.repository_url
}

output "arn" {
  description = "ECRリポジトリのARN"
  value       = aws_ecr_repository.this.arn
}
