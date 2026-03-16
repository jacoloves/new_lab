resource "aws_ecs_task_definition" "task_definition" {
  family = local.task_family_name
  requires_compatibilities = [
    "FARGATE"
  ]

  network_mode = "awsvpc"

  cpu    = var.task_cpu_allocation
  memory = var.task_memory_allocation

  task_role_arn      = var.task_role_arn
  execution_role_arn = var.task_exec_role_arn

  container_definitions = var.container_definition

  tags = local.task_resource_tags

  lifecycle {
    ignore_changes = [
      container_definitions
    ]
  }
}
