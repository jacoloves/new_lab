resource "aws_db_subnet_group" "main" {
  name        = "sbcntr-main"
  description = "DB subnet group for Aurora"

  subnet_ids = [
    aws_subnet.private_db_a.id,
    aws_subnet.private_db_c.id,
  ]

  tags = {
    Name = "sbcntr-main"
  }
}

resource "aws_rds_cluster" "main" {
  cluster_identifier = "sbcntr-main"
  engine             = "aurora-postgresql"

  engine_lifecycle_support = "open-source-rds-extended-support-disabled"

  database_name   = "app"
  master_username = "sbcntradmin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  port                   = 5432

  enable_http_endpoint = true

  serverlessv2_scaling_configuration {
    min_capacity             = 0
    max_capacity             = 4
    seconds_until_auto_pause = 300
  }

  backup_retention_period = 1
  storage_encrypted       = true

  deletion_protection = true

  preferred_maintenance_window = "sat:12:00-sat:12:30"

  skip_final_snapshot = true

  tags = {
    Name = "sbcntr-main"
  }
}

resource "aws_rds_cluster_instance" "main" {
  identifier         = "sbcntr-main-instance-1"
  cluster_identifier = aws_rds_cluster.main.id

  instance_class = "db.serverless"
  engine         = aws_rds_cluster.main.engine
  engine_version = aws_rds_cluster.main.engine_version

  publicly_accessible        = false
  auto_minor_version_upgrade = true

  tags = {
    Name = "sbcntr-main-instance-1"
  }
}


resource "aws_secretsmanager_secret" "sbcntruser_db_credentials" {
  name        = "rds-db-credentials/cluster-DBZG3YHZEOIGJLADDUB22XIJWY/sbcntruser/1786244874556"
  description = "RDS database sbcntruser credentials for sbcntr-main"
}
