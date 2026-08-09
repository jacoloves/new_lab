resource "aws_lb_target_group" "frontend_app_blue" {
  name             = "sbcntr-frontapp-blue"
  target_type      = "ip"
  protocol         = "HTTP"
  port             = 8080
  ip_address_type  = "ipv4"
  vpc_id           = aws_vpc.main.id
  protocol_version = "HTTP1"

  health_check {
    path                = "/healthcheck"
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 15
    matcher             = "200"
  }

  tags = {
    Name = "sbcntr-frontapp-blue"
  }
}

resource "aws_lb_target_group" "frontend_app_green" {
  name             = "sbcntr-frontapp-green"
  target_type      = "ip"
  protocol         = "HTTP"
  port             = 8080
  ip_address_type  = "ipv4"
  vpc_id           = aws_vpc.main.id
  protocol_version = "HTTP1"

  health_check {
    path                = "/healthcheck"
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 15
    matcher             = "200"
  }

  tags = {
    Name = "sbcntr-frontapp-green"
  }
}

resource "aws_lb" "ingress" {
  name               = "sbcntr-ingress"
  load_balancer_type = "application"
  internal           = false
  ip_address_type    = "ipv4"

  security_groups = [
    aws_security_group.ingress.id,
  ]

  subnets = module.subnet_pair_ingress.ids

  tags = {
    Name = "sbcntr-ingress"
  }
}

resource "aws_lb_listener" "frontend_app_blue" {
  load_balancer_arn = aws_lb.ingress.arn
  protocol          = "HTTP"
  port              = 80

  default_action {
    type = "forward"

    forward {
      target_group {
        arn    = aws_lb_target_group.frontend_app_blue.arn
        weight = 1
      }

      target_group {
        arn    = aws_lb_target_group.frontend_app_green.arn
        weight = 0
      }
    }

  }

  tags = {
    Name = "sbcntr-ingress"
  }
}

resource "aws_lb_listener_rule" "frontend_app_production" {
  listener_arn = aws_lb_listener.frontend_app_blue.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend_app_blue.arn
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }

  tags = {
    Name = "sbcntr-ingress-production"
  }

  lifecycle {
    ignore_changes = [action]
  }
}
