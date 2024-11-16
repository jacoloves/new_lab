# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "igw-06f263cc58d79c5a9"
resource "aws_internet_gateway" "sample_igw" {
  tags = {
    Name = "sample-igw"
  }
  tags_all = {
    Name = "sample-igw"
  }
  vpc_id = "vpc-01571316db9f0fe51"
}
