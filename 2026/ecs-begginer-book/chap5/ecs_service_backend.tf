resource "aws_ecs_service" "backend_app" {
  name            = "sbcntr-backend-app"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.backend_app.arn

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    base              = 0
    weight            = 1
  }

  platform_version = "LATEST"

  desired_count                      = 1
  enable_ecs_managed_tags            = true
  health_check_grace_period_seconds  = 60
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  network_configuration {
    subnets = module.subnet_pair_app.ids

    security_groups = [
      aws_security_group.backend_app.id,
    ]

    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.backend_app.arn
  }

  depends_on = [
    aws_ecs_cluster_capacity_providers.app,
    aws_cloudwatch_log_group.backend_app,
  ]

  tags = {
    Project = "sbcntr"
  }
}
