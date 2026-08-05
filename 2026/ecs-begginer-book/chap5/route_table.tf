##################################################
# コンテナアプリ用ルートテーブル
##################################################

resource "aws_route_table" "app" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "sbcntr-app"
  }
}

resource "aws_route_table_association" "app_a" {
  route_table_id = aws_route_table.app.id
  subnet_id      = aws_subnet.private_app_a.id
}

resource "aws_route_table_association" "app_c" {
  route_table_id = aws_route_table.app.id
  subnet_id      = aws_subnet.private_app_c.id
}

##################################################
# Ingress用ルートテーブル
##################################################

resource "aws_route_table" "ingress" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "sbcntr-ingress"
  }
}

resource "aws_route_table_association" "ingress_a" {
  route_table_id = aws_route_table.ingress.id
  subnet_id      = aws_subnet.public_ingress_a.id
}

resource "aws_route_table_association" "ingress_c" {
  route_table_id = aws_route_table.ingress.id
  subnet_id      = aws_subnet.public_ingress_c.id
}

# Ingress用ルートテーブルのデフォルトルート(IGW経由)
resource "aws_route" "ingress_default" {
  route_table_id         = aws_route_table.ingress.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

##################################################
# 管理サーバ用ルートテーブル
##################################################

resource "aws_route_table" "management" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "sbcntr-management"
  }
}

resource "aws_route_table_association" "management_a" {
  route_table_id = aws_route_table.management.id
  subnet_id      = aws_subnet.public_management_a.id
}

resource "aws_route_table_association" "management_c" {
  route_table_id = aws_route_table.management.id
  subnet_id      = aws_subnet.public_management_c.id
}

# 管理用ルートテーブルのデフォルトルート(IGW経由)
resource "aws_route" "management_default" {
  route_table_id         = aws_route_table.management.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}
