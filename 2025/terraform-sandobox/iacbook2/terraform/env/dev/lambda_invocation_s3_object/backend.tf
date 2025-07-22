terraform {
  backend "s3" {
    bucket = "dev-tfstate-aws-iac-book-project-shooonng-20250302"
    key    = "lambda_invocation_s3_object/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
