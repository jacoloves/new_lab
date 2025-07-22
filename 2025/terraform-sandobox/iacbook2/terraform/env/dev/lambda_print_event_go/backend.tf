terraform {
  backend "s3" {
    bucket = "dev-tfstate-aws-iac-book-project-shooonng-20250302"
    key    = "lambda_print_event_go/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
