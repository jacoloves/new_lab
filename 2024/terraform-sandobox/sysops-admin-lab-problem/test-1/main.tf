provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "soalab_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "soalab_vpc"
  }
}

resource "aws_internet_gateway" "soalab_igw" {
  vpc_id = aws_vpc.soalab_vpc.id
  tags = {
    Name = "soalab_igw"
  }
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "public_subnet_1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = {
    Name = "public_subnet_2"
  }
}

resource "aws_subnet" "public_subnet_3" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "us-east-1c"
  map_public_ip_on_launch = true
  tags = {
    Name = "public_subnet_3"
  }
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.101.0/24"
  availability_zone       = "us-east-1d"
  map_public_ip_on_launch = false
  tags = {
    Name = "private_subnet_1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.102.0/24"
  availability_zone       = "us-east-1e"
  map_public_ip_on_launch = false
  tags = {
    Name = "private_subnet_2"
  }
}
resource "aws_subnet" "private_subnet_3" {
  vpc_id                  = aws_vpc.soalab_vpc.id
  cidr_block              = "10.0.103.0/24"
  availability_zone       = "us-east-1f"
  map_public_ip_on_launch = false
  tags = {
    Name = "private_subnet_3"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.soalab_vpc.id
  tags = {
    Name = "public_route_table"
  }
}


