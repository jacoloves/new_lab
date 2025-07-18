terraform {
  backend "s3" {
    bucket = "dev-tfstate-aws-iac-book-project-shooonng-20250302"
    key    = "sqs/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
