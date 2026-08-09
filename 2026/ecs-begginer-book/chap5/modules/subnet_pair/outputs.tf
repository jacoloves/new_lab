output "a_id" {
  description = "a側サブネットのID"
  value       = aws_subnet.a.id
}

output "c_id" {
  description = "c側サブネットのID"
  value       = aws_subnet.c.id
}

output "ids" {
  description = "a側・c側サブネットIDのリスト"
  value       = [aws_subnet.a.id, aws_subnet.c.id]
}
