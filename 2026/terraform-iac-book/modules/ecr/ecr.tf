resource "aws_ecr_repository" "repository" {
  name                 = "${var.service_name}-${var.env}-${var.role}"
  image_tag_mutability = var.image_tag_mutability
}

resource "aws_ecr_lifecycle_policy" "policy" {
  repository = aws_ecr_repository.repository.name
  policy     = var.repository_lifecycle_policy == "" ? file("${path.module}/lifecycle_policy/default_policy.json") : var.repository_lifecycle_policy
}
