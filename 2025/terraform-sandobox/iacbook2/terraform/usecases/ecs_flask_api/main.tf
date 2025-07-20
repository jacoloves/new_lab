resource "aws_ecs_cluster" "flask_api" {
  name = "${var.stage}-flask-api-tf"
}

resource "aws_ecs_cluster_capacity_providers" "flask_api" {
  capacity_providers = [
    "FARGATE"
  ]
  cluster_name = aws_ecs_cluster.flask_api.name
}

data "aws_ssm_parameter" "flask_api_correct_answer" {
  name = "/flask-apitf/${var.stage}/correct_answer"
}

data "aws_iam_policy_document" "ecs_task_execution_assume_role" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
      type = "Service"
    }
  }
}

data "aws_iam_policy" "managed_ecs_task_execution" {
  name = "AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_task_execution" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
    ]
    resources = [
      data.aws_ssm_parameter.flask_api_correct_answer.arn
    ]
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.stage}-flask-api-execution-role-tf"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role.json
}

resource "aws_iam_role_policy_attachments_exclusive" "ecs_task_execution_managed_policy" {
  policy_arns = [data.aws_iam_policy.managed_ecs_task_execution.arn]
  role_name   = aws_iam_role.ecs_task_execution_role.name
}

resource "aws_iam_role_policy" "ecs_task_execution_inline_policy" {
  name   = "${var.stage}-flask-api-ecs-task-execution-policy"
  policy = data.aws_iam_policy_document.ecs_task_execution.json
  role   = aws_iam_role.ecs_task_execution_role.name
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      identifiers = [
        "ecs-tasks.amazonaws.com"
      ]
      type = "Service"
    }
  }
}

data "aws_iam_policy_document" "ecs_task_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssmmessage:CreateControlChannel",
      "ssmmessage:CreateDataChannel",
      "ssmmessage:OpenControlChannel",
      "ssmmessage:OpenDataChannel",
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role" "ecs_task" {
  name               = "${var.stage}-flask-api-ecs-task-role-tf"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

resource "aws_iam_role_policy" "ecs_task_inline_policy" {
  name   = "${var.stage}-flask-api-ecs-task-policy"
  policy = data.aws_iam_policy_document.ecs_task_policy.json
  role   = aws_iam_role.ecs_task.name
}

locals {
  vpc_name = "${var.stage}-vpc"
}

data "aws_vpc" "this" {
  filter {
    name   = "tag:Name"
    values = [local.vpc_name]
  }
}

data "aws_subnets" "public" {
  filter {
    name = "tag:Name"
    values = [
      "${local.vpc_name}-public-ap-northeast-1a",
      "${local.vpc_name}-public-ap-northeast-1c",
      "${local.vpc_name}-public-ap-northeast-1d"
    ]
  }
}

resource "aws_security_group" "alb" {
  name   = "${var.stage}-flask_api_alb_tf"
  vpc_id = data.aws_vpc.this.id
}

resource "aws_security_group" "ecs_instance" {
  name   = "${var.stage}-flask_api_ecs_instance_tf"
  vpc_id = data.aws_vpc.this.id
}

resource "aws_vpc_security_group_ingress_rule" "lb_from_http" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.alb.id
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "lb_to_ecs_instance" {
  ip_protocol                  = "tcp"
  security_group_id            = aws_security_group.alb.id
  from_port                    = 5000
  to_port                      = 5000
  referenced_security_group_id = aws_security_group.ecs_instance.id
}

resource "aws_vpc_security_group_ingress_rule" "ecs_instance_from_lb" {
  ip_protocol                  = "tcp"
  security_group_id            = aws_security_group.ecs_instance.id
  from_port                    = 5000
  to_port                      = 5000
  referenced_security_group_id = aws_security_group.alb.id
}

resource "aws_vpc_security_group_egress_rule" "ecs_instance_to_https" {
  ip_protocol       = "tcp"
  security_group_id = aws_security_group.ecs_instance.id
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_lb" "flask_api" {
  name               = "${var.stage}-flask-api-alb-tf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.public.ids
}

resource "aws_lb_target_group" "flask_api" {
  name        = "flask-api-tf"
  port        = 5000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.this.id
  health_check {
    path     = "/health"
    protocol = "HTTP"
    matcher  = "200"
    interval = 10
  }
}

resource "aws_lb_listener" "flask_api" {
  load_balancer_arn = aws_lb.flask_api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    forward {
      target_group {
        arn = aws_lb_target_group.flask_api.arn
      }
    }
  }

  depends_on = [aws_lb_target_group.flask_api]
}

data "aws_region" "current" {}

data "aws_ecr_repository" "flask_api" {
  name = "${var.stage}-flask-api-tf"
}

resource "aws_cloudwatch_log_group" "flask_api" {
  name              = "/ecs/${var.stage}-flask-api-tf"
  retention_in_days = 90
}

locals {
  container_definitions = {
    flask_api = {
      name = "flask-api"
      secrets = [
        {
          name      = "CORRECT_ANSWER"
          valueFrom = data.aws_ssm_parameter.flask_api_correct_answer.arn
        },
      ]
      essential = true

      image = "${data.aws_ecr_repository.flask_api.repository_url}:latest"
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.flask_api.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "flask_api"
        }
      }

      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        },
      ]
    },
  }
}

resource "aws_ecs_task_definition" "flask_api" {
  container_definitions = jsonencode(
    values(local.container_definitions)
  )
  cpu                = "256"
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  family             = "${var.stage}-flask-api-tf"
  memory             = "512"
  network_mode       = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  task_role_arn = aws_iam_role.ecs_task.arn
  skip_destroy  = true
}

resource "aws_ecs_service" "flask_api" {
  cluster                           = aws_ecs_cluster.flask_api.arn
  desired_count                     = 0
  enable_execute_command            = true
  health_check_grace_period_seconds = 60
  launch_type                       = "FARGATE"
  name                              = "flask-api-tf"
  task_definition                   = aws_ecs_task_definition.flask_api.arn

  deployment_circuit_breaker {
    enable   = true
    rollback = false
  }

  load_balancer {
    container_name   = local.container_definitions.flask_api.name
    container_port   = 5000
    target_group_arn = aws_lb_target_group.flask_api.arn
  }

  network_configuration {
    security_groups = [
      aws_security_group.ecs_instance.id
    ]

    subnets          = data.aws_subnets.public.ids
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [
      desired_count
    ]
  }

  depends_on = [aws_lb_listener.flask_api]
}
