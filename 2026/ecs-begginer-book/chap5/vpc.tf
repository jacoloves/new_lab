##################################################
# VPC
##################################################

# メインVPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"

  tags = {
    Name = "sbcntr-main"
  }
}

##################################################
# インターネットゲートウェイ
##################################################

# インターネット通信用のIGW
# Terraformではvpc_idを指定するだけでVPCへのアタッチが行われるため、
# CloudFormationのAWS::EC2::VPCGatewayAttachmentに相当するリソースは不要
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "sbcntr-main"
  }
}
