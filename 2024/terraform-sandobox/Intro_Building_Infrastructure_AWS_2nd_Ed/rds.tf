# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "sample-db-og"
resource "aws_db_option_group" "sample_db_og" {
  engine_name              = "mysql"
  major_engine_version     = "8.0"
  name                     = "sample-db-og"
  name_prefix              = null
  option_group_description = "sample option group"
  skip_destroy             = false
  tags                     = {}
  tags_all                 = {}
}

# __generated__ by Terraform from "sample-db-subnet"
resource "aws_db_subnet_group" "sample_db_subnet" {
  description = "sample db subnet"
  name        = "sample-db-subnet"
  name_prefix = null
  subnet_ids  = ["subnet-061d4a755835d9659", "subnet-083eed64326cd933f"]
  tags        = {}
  tags_all    = {}
}

# __generated__ by Terraform
resource "aws_db_instance" "sample_db_instance" {
  allocated_storage           = 20
  allow_major_version_upgrade = null
  apply_immediately           = null
  auto_minor_version_upgrade  = true
  availability_zone           = "ap-northeast-1c"
  backup_retention_period     = 1
  backup_target               = "region"
  backup_window               = "16:30-17:00"
  ca_cert_identifier          = "rds-ca-rsa2048-g1"
  character_set_name          = null
  copy_tags_to_snapshot       = true
  custom_iam_instance_profile = null
  customer_owned_ip_enabled   = false
  db_name                     = null
  db_subnet_group_name        = "sample-db-subnet"
  dedicated_log_volume        = false
  delete_automated_backups    = true
  deletion_protection         = false
  domain                      = null
  domain_auth_secret_arn      = null
  #domain_dns_ips                        = []
  domain_fqdn                           = null
  domain_iam_role_name                  = null
  domain_ou                             = null
  enabled_cloudwatch_logs_exports       = []
  engine                                = "mysql"
  engine_lifecycle_support              = "open-source-rds-extended-support-disabled"
  engine_version                        = "8.0.39"
  final_snapshot_identifier             = null
  iam_database_authentication_enabled   = false
  identifier                            = "sample-db"
  identifier_prefix                     = null
  instance_class                        = "db.t3.micro"
  iops                                  = 0
  kms_key_id                            = "arn:aws:kms:ap-northeast-1:775115982694:key/05c3c443-0a16-48d1-aa6e-995a71a6eaf4"
  license_model                         = "general-public-license"
  maintenance_window                    = "sat:17:50-sat:18:20"
  manage_master_user_password           = null
  master_user_secret_kms_key_id         = null
  max_allocated_storage                 = 1000
  monitoring_interval                   = 0
  monitoring_role_arn                   = null
  multi_az                              = false
  nchar_character_set_name              = null
  network_type                          = "IPV4"
  option_group_name                     = "sample-db-og"
  parameter_group_name                  = "sample-db-pg"
  password                              = null # sensitive
  performance_insights_enabled          = false
  performance_insights_kms_key_id       = null
  performance_insights_retention_period = 0
  port                                  = 3306
  publicly_accessible                   = false
  replica_mode                          = null
  replicate_source_db                   = null
  skip_final_snapshot                   = true
  snapshot_identifier                   = null
  storage_encrypted                     = true
  storage_throughput                    = 0
  storage_type                          = "gp2"
  tags                                  = {}
  tags_all                              = {}
  timezone                              = null
  upgrade_storage_config                = null
  username                              = "admin"
  vpc_security_group_ids                = ["sg-06f53c1fded3389e3"]
}

# __generated__ by Terraform from "sample-db-pg"
resource "aws_db_parameter_group" "sample_db_sg" {
  description  = "sample parameter group"
  family       = "mysql8.0"
  name         = "sample-db-pg"
  name_prefix  = null
  skip_destroy = false
  tags         = {}
  tags_all     = {}
}
