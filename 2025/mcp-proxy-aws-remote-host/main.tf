# 最新のUbuntu AMIを取得
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPCの作成
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# インターネットゲートウェイの作成
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# パブリックサブネットの作成
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-northeast-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

# ルートテーブルの作成
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# ルートテーブルとサブネットの関連付け
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# セキュリティグループの作成
resource "aws_security_group" "main" {
  name        = "${var.project_name}-sg"
  description = "Security group for UV server"
  vpc_id      = aws_vpc.main.id

  # SSH接続用
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # 8080ポート用
  ingress {
    description = "Application port 8080"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # アウトバウンド通信を全て許可
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# EC2インスタンスの作成
resource "aws_instance" "main" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = aws_subnet.public.id

  vpc_security_group_ids = [aws_security_group.main.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # システムの更新
              apt-get update
              apt-get upgrade -y
              
              # 必要なパッケージのインストール
              apt-get install -y curl wget git
              
              # uvのインストール
              curl -LsSf https://astral.sh/uv/install.sh | sh
              
              # uvをシステムワイドで利用可能にする
              ln -s /root/.cargo/bin/uv /usr/local/bin/uv
              
              # インストール確認用のログ
              echo "uv installation completed" > /var/log/uv-install.log
              /usr/local/bin/uv --version >> /var/log/uv-install.log 2>&1 || echo "uv command not found" >> /var/log/uv-install.log
              
              EOF

  tags = {
    Name = "${var.project_name}-instance"
  }
}

# Elastic IPの作成（オプション：固定IPが必要な場合）
resource "aws_eip" "main" {
  instance = aws_instance.main.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }

  depends_on = [aws_internet_gateway.main]
}
