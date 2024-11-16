# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "aws_route_table" "sample_rt_public" {
  propagating_vgws = []
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "igw-06f263cc58d79c5a9"
  }
  tags = {
    Name = "sample-rt-public"
  }
  tags_all = {
    Name = "sample-rt-public"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}

# __generated__ by Terraform
resource "aws_route_table" "sample_rt_private02" {
  propagating_vgws = []
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = "nat-0b63abab479353576"
  }
  tags = {
    Name = "sample-rt-private02"
  }
  tags_all = {
    Name = "sample-rt-private02"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}

# __generated__ by Terraform
resource "aws_route_table" "sample_rt_private01" {
  propagating_vgws = []
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = "nat-0e5651f3216afcaef"
  }
  tags = {
    Name = "sample-rt-private01"
  }
  tags_all = {
    Name = "sample-rt-private01"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}
