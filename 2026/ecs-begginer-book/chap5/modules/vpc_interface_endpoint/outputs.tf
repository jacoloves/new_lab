output "id" {
  description = "作成したVPCエンドポイントのID"
  value       = aws_vpc_endpoint.this.id
}

output "arn" {
  description = "作成したVPCエンドポイントのARN"
  value       = aws_vpc_endpoint.this.arn
}
