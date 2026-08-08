resource "aws_db_subnet_group" "main" {
  name        = "sbcntr-main"
  description = "DB subnet group for Aurora"

  subnet_ids = [
    aws_subnet.private_db_a.id,
    aws_subnet.private_db_c.id,
  ]

  tags = {
    Name = "sbcntr-main"
  }
}
