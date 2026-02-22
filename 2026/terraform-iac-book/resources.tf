module "vpc" {
  source         = "./modules/vpc"
  service_name   = "sample"
  env            = terraform.workspace
  vpc_cidr_block = "10.0.0.0/16"
  vpc_additional_tags = {
    Usage = "sample vpc explanation"
  }
}
