resource "aws_route_table" "public_route_tables" {
  for_each = aws_subnet.public_subnets
  vpc_id   = aws_vpc.vpc.id

  tags = {
    Name            = "${var.service_name}-${var.env}-${each.value.availability_zone}-public-route-table"
    AvailablityZone = each.value.availability_zone
    Scope           = "public"
  }
}

resource "aws_route" "public_default_route" {
  for_each       = aws_subnet.public_subnets
  route_table_id = aws_route_table.public_route_tables[each.key].id

  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_route_table_associations" {
  for_each       = aws_subnet.public_subnets
  route_table_id = aws_route_table.public_route_tables[each.key].id
  subnet_id      = each.value.id
}
