provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = {
      terraform = "true"
      stage     = "dev"
      module    = "case1"
    }
  }
}

provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
  default_tags {
    tags = {
      terraform = "true"
      stage     = "dev"
      module    = "case1"
    }
  }
}
