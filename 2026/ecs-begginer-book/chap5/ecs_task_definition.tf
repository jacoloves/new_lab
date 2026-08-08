data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_cloudwatch_log_group" "frontend_app" {
  name = "/sbcntr/ecs/frontend-app"
}

resource "aws_ecs_task_definition" "frontend_app" {
  family                   = "sbcntr-frontend-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/sbcntr-frontend-app:v1.0.1"
      essential = true

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      readonlyRootFilesystem = true
      memoryReservation      = 512

      environment = [
        {
          name  = "BACKEND_FQDN"
          value = "backend-app.sbcntr.local"
        },
        {
          name  = "BACKEND_PORT"
          value = "8081"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/sbcntr/ecs/frontend-app"
          "awslogs-region"        = "ap-northeast-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "sbcntr-frontend-app"
  }

}

