terraform {
  backend "s3" {
    region       = "ap-northeast-1"
    bucket       = "shooonng-terraform-plactice"
    key          = "terraform-iac-book/terraform.tfstate"
    use_lockfile = true
  }
}
