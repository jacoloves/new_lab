terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

resource "aws_security_group" "cluster_instance" {
  name = var.security_group_name
}

moved {
  from = aws_security_group.instance
  to   = aws_security_group.cluster_instance
}
