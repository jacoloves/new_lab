module "vpc_endpoint_ecr_api" {
  source = "./modules/vpc_interface_endpoint"

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.ap-northeast-1.ecr.api"
  subnet_ids         = module.subnet_pair_egress.ids
  security_group_ids = [aws_security_group.egress_vpce.id]
  name               = "sbcntr-ecr-api"
}

module "vpc_endpoint_ecr_dkr" {
  source = "./modules/vpc_interface_endpoint"

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.ap-northeast-1.ecr.dkr"
  subnet_ids         = module.subnet_pair_egress.ids
  security_group_ids = [aws_security_group.egress_vpce.id]
  name               = "sbcntr-ecr-dkr"
}

module "vpc_endpoint_logs" {
  source = "./modules/vpc_interface_endpoint"

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.ap-northeast-1.logs"
  subnet_ids         = module.subnet_pair_egress.ids
  security_group_ids = [aws_security_group.egress_vpce.id]
  name               = "sbcntr-logs"
}

module "vpc_endpoint_secretsmanager" {
  source = "./modules/vpc_interface_endpoint"

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.ap-northeast-1.secretsmanager"
  subnet_ids         = module.subnet_pair_egress.ids
  security_group_ids = [aws_security_group.egress_vpce.id]
  name               = "sbcntr-secrets-manager"
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.ap-northeast-1.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.app.id
  ]

  tags = {
    Name = "sbcntr-s3"
  }
}
