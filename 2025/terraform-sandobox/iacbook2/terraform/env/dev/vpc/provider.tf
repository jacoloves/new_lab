provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = {
      Terraform = "true"
      STAGE     = "dev"
      MODULE    = "vpc"
    }
  }
}

provider "aws" {
  alias  = "us_east_1"
  region = "us_east_1"
  default_tags {
    tags = {
      Terraform = "true"
      STAGE     = "dev"
      MODULE    = "vpc"
    }
  }
}
