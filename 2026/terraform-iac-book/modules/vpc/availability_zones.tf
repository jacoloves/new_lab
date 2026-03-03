data "aws_availability_zones" "availability_zones" {
  state = "available"

  exclude_names = [
    "ap-northeast-1b"
  ]
}

locals {
  number_of_availability_zones = length(data.aws_availability_zones.availability_zones.names)
}
