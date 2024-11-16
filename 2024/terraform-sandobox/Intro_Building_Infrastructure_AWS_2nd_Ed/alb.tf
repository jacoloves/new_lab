# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "aws_lb_target_group" "sample_tg" {
  connection_termination             = null
  deregistration_delay               = "300"
  ip_address_type                    = "ipv4"
  lambda_multi_value_headers_enabled = null
  load_balancing_algorithm_type      = "round_robin"
  load_balancing_anomaly_mitigation  = "off"
  load_balancing_cross_zone_enabled  = "use_load_balancer_configuration"
  name                               = "sample-tg"
  name_prefix                        = null
  port                               = 3000
  preserve_client_ip                 = null
  protocol                           = "HTTP"
  protocol_version                   = "HTTP1"
  proxy_protocol_v2                  = null
  slow_start                         = 0
  tags                               = {}
  tags_all                           = {}
  target_type                        = "instance"
  vpc_id                             = "vpc-01571316db9f0fe51"
  health_check {
    enabled             = true
    healthy_threshold   = 5
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  stickiness {
    cookie_duration = 86400
    cookie_name     = null
    enabled         = false
    type            = "lb_cookie"
  }
  target_failover {
    on_deregistration = "no_rebalance"
    on_unhealthy      = "no_rebalance"
  }
  target_group_health {
    dns_failover {
      minimum_healthy_targets_count      = "1"
      minimum_healthy_targets_percentage = "off"
    }
    unhealthy_state_routing {
      minimum_healthy_targets_count      = 1
      minimum_healthy_targets_percentage = "off"
    }
  }
  target_health_state {
    enable_unhealthy_connection_termination = true
    unhealthy_draining_interval             = null
  }
}

# __generated__ by Terraform
resource "aws_lb" "sample_elb" {
  client_keep_alive                                            = 3600
  customer_owned_ipv4_pool                                     = null
  desync_mitigation_mode                                       = "defensive"
  dns_record_client_routing_policy                             = null
  drop_invalid_header_fields                                   = false
  enable_cross_zone_load_balancing                             = true
  enable_deletion_protection                                   = false
  enable_http2                                                 = true
  enable_tls_version_and_cipher_suite_headers                  = false
  enable_waf_fail_open                                         = false
  enable_xff_client_port                                       = false
  enable_zonal_shift                                           = null
  enforce_security_group_inbound_rules_on_private_link_traffic = null
  idle_timeout                                                 = 60
  internal                                                     = false
  ip_address_type                                              = "ipv4"
  load_balancer_type                                           = "application"
  name                                                         = "sample-elb"
  name_prefix                                                  = null
  preserve_host_header                                         = false
  security_groups                                              = ["sg-0256379c4fc699f58", "sg-06f53c1fded3389e3"]
  #subnets                                                      = ["subnet-015c52918c6ea2fd3", "subnet-0d6d765076afb5bd0"]
  tags                       = {}
  tags_all                   = {}
  xff_header_processing_mode = "append"
  access_logs {
    bucket  = ""
    enabled = false
    prefix  = null
  }
  connection_logs {
    bucket  = ""
    enabled = false
    prefix  = null
  }
  subnet_mapping {
    allocation_id        = null
    ipv6_address         = null
    private_ipv4_address = null
    subnet_id            = "subnet-015c52918c6ea2fd3"
  }
  subnet_mapping {
    allocation_id        = null
    ipv6_address         = null
    private_ipv4_address = null
    subnet_id            = "subnet-0d6d765076afb5bd0"
  }
}
