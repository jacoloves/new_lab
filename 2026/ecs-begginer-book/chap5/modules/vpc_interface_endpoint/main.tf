resource "aws_vpc_endpoint" "this" {
  vpc_id              = var.vpc_id
  service_name        = var.service_name
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = var.private_dns_enabled

  subnet_ids         = var.subnet_ids
  security_group_ids = var.security_group_ids

  tags = {
    Name = var.name
  }
}
