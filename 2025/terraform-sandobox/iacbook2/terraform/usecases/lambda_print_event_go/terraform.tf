terraform {
  required_version = "1.9.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.72.1"
    }
    external = {
      source  = "hashicorp/external"
      version = "2.3.3"
    }
  }
}
