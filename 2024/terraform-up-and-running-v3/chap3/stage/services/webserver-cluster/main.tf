data "tarraform_remote_state" "db" {
  backedn = "s3"

  config = {
    bucket = "terraform-up-and-running-state-20240607-chap3-shooonng"
    key    = "stage/data-stores/mysql/terraform.tfstate"
    region = "us-east-2"
  }
}

resource "aws_launch_configuration" "example" {
  image_id        = "ami-ofb653ca2d3203ac1"
  instace_type    = "t2.micro"
  security_groups = [aws_security_group.instance.id]

  user_data = templatefile("user-data.sh", {
    server_port = var.server_port
    db_address  = data.terraform_remote_state.db.outputs.address
    db_port     = data.terraform_remote_state.db.outputs.port
  })
}
