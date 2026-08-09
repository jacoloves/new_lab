resource "aws_subnet" "a" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.cidr_block_a
  availability_zone       = var.availability_zone_a
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = {
    Name = "${var.name_prefix}-a"
    Type = var.type_tag
  }
}

resource "aws_subnet" "c" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.cidr_block_c
  availability_zone       = var.availability_zone_c
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = {
    Name = "${var.name_prefix}-c"
    Type = var.type_tag
  }
}
