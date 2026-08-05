##################################################
# セキュリティグループ本体
##################################################

# インターネット公開用セキュリティグループ
resource "aws_security_group" "ingress" {
  name        = "ingress"
  description = "Security group for ingress"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "from 0.0.0.0/0:80"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description      = "from ::/0:80"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-ingress"
  }
}

# 管理用サーバ向けセキュリティグループ
resource "aws_security_group" "management" {
  name        = "management"
  description = "Security Group of management server"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-management"
  }
}

# バックエンドコンテナアプリ用セキュリティグループ
resource "aws_security_group" "backend_app" {
  name        = "backend_app"
  description = "Security Group of backend app"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-backend-app"
  }
}

# フロントエンドコンテナアプリ用セキュリティグループ
resource "aws_security_group" "frontend_app" {
  name        = "frontend-app"
  description = "Security Group of frontend app"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-frontend-app"
  }
}

# DB用セキュリティグループ
resource "aws_security_group" "db" {
  name        = "database"
  description = "Security Group of database"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-db"
  }
}

# VPCエンドポイント用セキュリティグループ
resource "aws_security_group" "egress_vpce" {
  name        = "egress"
  description = "Security Group of VPC Endpoint"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic by default"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sbcntr-vpce"
  }
}

##################################################
# セキュリティグループルール(グループ間の紐付け)
##################################################

# Internet LB -> Frontend app
resource "aws_security_group_rule" "frontend_app_from_ingress_tcp" {
  type                     = "ingress"
  description              = "HTTP from Ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  security_group_id        = aws_security_group.frontend_app.id
  source_security_group_id = aws_security_group.ingress.id
}

# Frontend app -> Backend app
resource "aws_security_group_rule" "backend_app_from_frontend_app_tcp" {
  type                     = "ingress"
  description              = "HTTP for frontend app"
  from_port                = 8081
  to_port                  = 8081
  protocol                 = "tcp"
  security_group_id        = aws_security_group.backend_app.id
  source_security_group_id = aws_security_group.frontend_app.id
}

# Backend app -> DB
resource "aws_security_group_rule" "db_from_backend_app_tcp" {
  type                     = "ingress"
  description              = "PostgreSQL protocol from backend App"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.backend_app.id
}

# Management server -> DB
resource "aws_security_group_rule" "db_from_management_tcp" {
  type                     = "ingress"
  description              = "PostgreSQL protocol from management server"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.management.id
}

# Backend app -> VPC endpoint
resource "aws_security_group_rule" "vpce_from_backend_app_tcp" {
  type                     = "ingress"
  description              = "HTTPS for backend app"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.egress_vpce.id
  source_security_group_id = aws_security_group.backend_app.id
}

# Frontend app -> VPC endpoint
resource "aws_security_group_rule" "vpce_from_frontend_app_tcp" {
  type                     = "ingress"
  description              = "HTTPS for frontend app"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.egress_vpce.id
  source_security_group_id = aws_security_group.frontend_app.id
}

# Management server -> VPC endpoint
resource "aws_security_group_rule" "vpce_from_management_tcp" {
  type                     = "ingress"
  description              = "HTTPS for management server"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.egress_vpce.id
  source_security_group_id = aws_security_group.management.id
}
