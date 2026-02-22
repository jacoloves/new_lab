output "vpc_id" {
  description = "VPCのIDです"
  value       = aws_vpc.vpc.id
}

output "vpc_name" {
  description = "作成したVPCの名前です"
  value       = aws_vpc.vpc.tags["Name"]
}
