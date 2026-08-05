##################################################
# データソース
##################################################

# 利用可能なAZ一覧を取得(CFNのFn::GetAZsに相当)
data "aws_availability_zones" "available" {
  state = "available"
}

##################################################
# コンテナアプリ用プライベートサブネット
##################################################

resource "aws_subnet" "private_app_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.8.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-app-a"
    Type = "Isolated"
  }
}

resource "aws_subnet" "private_app_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.9.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-app-c"
    Type = "Isolated"
  }
}

##################################################
# DB用プライベートサブネット
##################################################

resource "aws_subnet" "private_db_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.16.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-db-a"
    Type = "Isolated"
  }
}

resource "aws_subnet" "private_db_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.17.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-db-c"
    Type = "Isolated"
  }
}

##################################################
# Ingress用パブリックサブネット
##################################################

resource "aws_subnet" "public_ingress_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "sbcntr-public-ingress-a"
    Type = "Public"
  }
}

resource "aws_subnet" "public_ingress_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "sbcntr-public-ingress-c"
    Type = "Public"
  }
}

##################################################
# 管理サーバ用パブリックサブネット
##################################################

resource "aws_subnet" "public_management_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.240.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "sbcntr-public-management-a"
    Type = "Public"
  }
}

resource "aws_subnet" "public_management_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.241.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "sbcntr-public-management-c"
    Type = "Public"
  }
}

##################################################
# VPCエンドポイント(Egress通信)用プライベートサブネット
##################################################

resource "aws_subnet" "private_egress_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.248.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-egress-a"
    Type = "Isolated"
  }
}

resource "aws_subnet" "private_egress_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.249.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = false

  tags = {
    Name = "sbcntr-private-egress-c"
    Type = "Isolated"
  }
}
