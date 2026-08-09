resource "aws_cloudwatch_log_group" "backend_app" {
  name              = "/sbcntr/ecs/backend-app"
  retention_in_days = 14

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_ecs_task_definition" "backend_app" {
  family                   = "sbcntr-backend-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/sbcntr-backend-app:v1"
      essential = true
      cpu       = 256

      portMappings = [
        {
          containerPort = 8081
          hostPort      = 8081
          protocol      = "tcp"
        }
      ]

      memoryReservation = 256

      environment = [
        {
          name  = "DB_NAME"
          value = "app"
        },
        {
          name  = "DB_CONN"
          value = "1"
        }
      ]

      secrets = [
        {
          name      = "DB_HOST"
          valueFrom = "arn:aws:secretsmanager:ap-northeast-1:775115982694:secret:rds-db-credentials/cluster-DBZG3YHZEOIGJLADDUB22XIJWY/sbcntruser/1786244874556-IlvuR6:host::"
        },
        {
          name      = "DB_USERNAME"
          valueFrom = "arn:aws:secretsmanager:ap-northeast-1:775115982694:secret:rds-db-credentials/cluster-DBZG3YHZEOIGJLADDUB22XIJWY/sbcntruser/1786244874556-IlvuR6:username::"
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:ap-northeast-1:775115982694:secret:rds-db-credentials/cluster-DBZG3YHZEOIGJLADDUB22XIJWY/sbcntruser/1786244874556-IlvuR6:password::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/sbcntr/ecs/backend-app"
          "awslogs-region"        = "ap-northeast-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "sbcntr-backend-app"
  }
}
