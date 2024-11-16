# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "aws_subnet" "sample_subnet_public01" {
  assign_ipv6_address_on_creation = false
  availability_zone               = "ap-northeast-1a"
  # availability_zone_id                           = "apne1-az4"
  cidr_block               = "10.0.0.0/20"
  customer_owned_ipv4_pool = null
  enable_dns64             = false
  # enable_lni_at_device_index                     = 1
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_cidr_block                                = null
  ipv6_native                                    = false
  # map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch             = false
  outpost_arn                         = null
  private_dns_hostname_type_on_launch = "ip-name"
  tags = {
    Name = "sample-subnet-public01"
  }
  tags_all = {
    Name = "sample-subnet-public01"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}

# __generated__ by Terraform
resource "aws_subnet" "sample_subnet_public02" {
  assign_ipv6_address_on_creation = false
  availability_zone               = "ap-northeast-1c"
  # availability_zone_id                           = "apne1-az1"
  cidr_block               = "10.0.16.0/20"
  customer_owned_ipv4_pool = null
  enable_dns64             = false
  # enable_lni_at_device_index                     = 1
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_cidr_block                                = null
  ipv6_native                                    = false
  # map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch             = false
  outpost_arn                         = null
  private_dns_hostname_type_on_launch = "ip-name"
  tags = {
    Name = "sample-subnet-public02"
  }
  tags_all = {
    Name = "sample-subnet-public02"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}

# __generated__ by Terraform
resource "aws_subnet" "sample_subnet_private01" {
  assign_ipv6_address_on_creation = false
  availability_zone               = "ap-northeast-1a"
  # availability_zone_id                           = "apne1-az4"
  cidr_block               = "10.0.64.0/20"
  customer_owned_ipv4_pool = null
  enable_dns64             = false
  # enable_lni_at_device_index                     = 1
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_cidr_block                                = null
  ipv6_native                                    = false
  # map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch             = false
  outpost_arn                         = null
  private_dns_hostname_type_on_launch = "ip-name"
  tags = {
    Name = "sample-subnet-private01"
  }
  tags_all = {
    Name = "sample-subnet-private01"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}

# __generated__ by Terraform
resource "aws_subnet" "sample_subnet_private02" {
  assign_ipv6_address_on_creation = false
  availability_zone               = "ap-northeast-1c"
  # availability_zone_id                           = "apne1-az1"
  cidr_block               = "10.0.80.0/20"
  customer_owned_ipv4_pool = null
  enable_dns64             = false
  # enable_lni_at_device_index                     = 1
  enable_resource_name_dns_a_record_on_launch    = false
  enable_resource_name_dns_aaaa_record_on_launch = false
  ipv6_cidr_block                                = null
  ipv6_native                                    = false
  # map_customer_owned_ip_on_launch                = false
  map_public_ip_on_launch             = false
  outpost_arn                         = null
  private_dns_hostname_type_on_launch = "ip-name"
  tags = {
    Name = "sample-subnet-private02"
  }
  tags_all = {
    Name = "sample-subnet-private02"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}
