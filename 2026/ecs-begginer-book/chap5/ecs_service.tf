resource "aws_ecs_service" "frontend_app" {
  name            = "sbcntr-frontend-app"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.frontend_app.arn

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    base              = 0
    weight            = 1
  }

  platform_version = "LATEST"

  scheduling_strategy               = "REPLICA"
  desired_count                     = 1
  availability_zone_rebalancing     = "ENABLED"
  health_check_grace_period_seconds = 60

  deployment_controller {
    type = "ECS"
  }

  deployment_configuration {
    strategy             = "BLUE_GREEN"
    bake_time_in_minutes = 1
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets = module.subnet_pair_app.ids

    security_groups = [
      aws_security_group.frontend_app.id,
    ]

    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend_app_blue.arn
    container_name   = "app"
    container_port   = 8080

    advanced_configuration {
      alternate_target_group_arn = aws_lb_target_group.frontend_app_green.arn
      production_listener_rule   = aws_lb_listener_rule.frontend_app_production.arn
      role_arn                   = aws_iam_role.ecs_role.arn
    }
  }

  depends_on = [
    aws_ecs_cluster_capacity_providers.app,
    aws_cloudwatch_log_group.frontend_app,
  ]

  tags = {
    Name = "sbcntr-frontend-app"
  }
}
