# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "aws_instance" "sample_ec2_bastion" {
  ami                                  = "ami-094dc5cf74289dfbc"
  associate_public_ip_address          = true
  availability_zone                    = "ap-northeast-1a"
  disable_api_stop                     = false
  disable_api_termination              = false
  ebs_optimized                        = false
  get_password_data                    = false
  hibernation                          = false
  host_id                              = null
  host_resource_group_arn              = null
  iam_instance_profile                 = null
  instance_initiated_shutdown_behavior = "stop"
  instance_type                        = "t2.micro"
  #ipv6_address_count                   = 0
  #ipv6_addresses                       = []
  key_name                   = "stanaka"
  monitoring                 = false
  placement_group            = null
  placement_partition_number = 0
  private_ip                 = "10.0.1.21"
  secondary_private_ips      = []
  security_groups            = []
  source_dest_check          = true
  subnet_id                  = "subnet-0d6d765076afb5bd0"
  tags = {
    Name = "sample-ec2-bastion"
  }
  tags_all = {
    Name = "sample-ec2-bastion"
  }
  tenancy                     = "default"
  user_data                   = null
  user_data_base64            = null
  user_data_replace_on_change = null
  volume_tags                 = null
  vpc_security_group_ids      = ["sg-021df59fc83e3d633", "sg-06f53c1fded3389e3"]
  capacity_reservation_specification {
    capacity_reservation_preference = "open"
  }
  cpu_options {
    amd_sev_snp      = null
    core_count       = 1
    threads_per_core = 1
  }
  credit_specification {
    cpu_credits = "standard"
  }
  enclave_options {
    enabled = false
  }
  maintenance_options {
    auto_recovery = "default"
  }
  metadata_options {
    http_endpoint               = "enabled"
    http_protocol_ipv6          = "disabled"
    http_put_response_hop_limit = 2
    http_tokens                 = "required"
    instance_metadata_tags      = "disabled"
  }
  private_dns_name_options {
    enable_resource_name_dns_a_record    = false
    enable_resource_name_dns_aaaa_record = false
    hostname_type                        = "ip-name"
  }
  root_block_device {
    delete_on_termination = true
    encrypted             = false
    iops                  = 100
    kms_key_id            = null
    tags                  = {}
    tags_all              = {}
    throughput            = 0
    volume_size           = 8
    volume_type           = "gp2"
  }
}
