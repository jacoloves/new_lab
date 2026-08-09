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

module "subnet_pair_app" {
  source = "./modules/subnet_pair"

  vpc_id              = aws_vpc.main.id
  name_prefix         = "sbcntr-private-app"
  type_tag            = "Isolated"
  cidr_block_a        = "10.0.8.0/24"
  cidr_block_c        = "10.0.9.0/24"
  availability_zone_a = data.aws_availability_zones.available.names[0]
  availability_zone_c = data.aws_availability_zones.available.names[1]
}

##################################################
# DB用プライベートサブネット
##################################################

module "subnet_pair_db" {
  source = "./modules/subnet_pair"

  vpc_id              = aws_vpc.main.id
  name_prefix         = "sbcntr-private-db"
  type_tag            = "Isolated"
  cidr_block_a        = "10.0.16.0/24"
  cidr_block_c        = "10.0.17.0/24"
  availability_zone_a = data.aws_availability_zones.available.names[0]
  availability_zone_c = data.aws_availability_zones.available.names[1]
}

##################################################
# Ingress用パブリックサブネット
##################################################

module "subnet_pair_ingress" {
  source = "./modules/subnet_pair"

  vpc_id                  = aws_vpc.main.id
  name_prefix             = "sbcntr-public-ingress"
  type_tag                = "Public"
  cidr_block_a            = "10.0.0.0/24"
  cidr_block_c            = "10.0.1.0/24"
  availability_zone_a     = data.aws_availability_zones.available.names[0]
  availability_zone_c     = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
}

##################################################
# 管理サーバ用パブリックサブネット
##################################################

module "subnet_pair_management" {
  source = "./modules/subnet_pair"

  vpc_id                  = aws_vpc.main.id
  name_prefix             = "sbcntr-public-management"
  type_tag                = "Public"
  cidr_block_a            = "10.0.240.0/24"
  cidr_block_c            = "10.0.241.0/24"
  availability_zone_a     = data.aws_availability_zones.available.names[0]
  availability_zone_c     = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
}

##################################################
# VPCエンドポイント(Egress通信)用プライベートサブネット
##################################################

module "subnet_pair_egress" {
  source = "./modules/subnet_pair"

  vpc_id              = aws_vpc.main.id
  name_prefix         = "sbcntr-private-egress"
  type_tag            = "Isolated"
  cidr_block_a        = "10.0.248.0/24"
  cidr_block_c        = "10.0.249.0/24"
  availability_zone_a = data.aws_availability_zones.available.names[0]
  availability_zone_c = data.aws_availability_zones.available.names[1]
}
