terraform {
  backend "s3" {
    bucket = "dev-tfstate-aws-iac-book-project-shooonng-20250302"
    key    = "ecs_flask_api/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
