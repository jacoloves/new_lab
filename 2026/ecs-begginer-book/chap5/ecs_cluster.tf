resource "aws_ecs_cluster" "app" {
  name = "sbcntr-app"

  setting {
    name  = "containerInsights"
    value = "enhanced"
  }

  tags = {
    Name = "sbcntr-app"
  }
}

resource "aws_ecs_cluster_capacity_providers" "app" {
  cluster_name       = aws_ecs_cluster.app.name
  capacity_providers = ["FARGATE"]
}
