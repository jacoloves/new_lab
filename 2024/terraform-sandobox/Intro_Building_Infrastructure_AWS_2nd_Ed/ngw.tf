# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform
resource "aws_nat_gateway" "sample_ngw_02" {
  allocation_id            = "eipalloc-07f857fe3c3d6bdec"
  connectivity_type        = "public"
  private_ip               = "10.0.28.28"
  secondary_allocation_ids = []
  #secondary_private_ip_address_count = 0
  #secondary_private_ip_addresses     = []
  subnet_id = "subnet-015c52918c6ea2fd3"
  tags = {
    Name = "sample-ngw-02"
  }
  tags_all = {
    Name = "sample-ngw-02"
  }
}

# __generated__ by Terraform
resource "aws_nat_gateway" "sample_ngw_01" {
  allocation_id            = "eipalloc-04126cd0cd0149d90"
  connectivity_type        = "public"
  private_ip               = "10.0.0.71"
  secondary_allocation_ids = []
  #secondary_private_ip_address_count = 0
  #secondary_private_ip_addresses     = []
  subnet_id = "subnet-0d6d765076afb5bd0"
  tags = {
    Name = "sample-ngw-01"
  }
  tags_all = {
    Name = "sample-ngw-01"
  }
}
