variable "number_example" {
  description = "An exapmle of a number varibale in Terraform"
  type        = number
  default     = 42
}

variable "list_exapmle" {
  description = "An exapmle of a list in Terraform"
  type        = list(any)
  default     = ["a", "b", "c"]
}

variable "list_numeric_exapmle" {
  description = "An exapmle of a numeric list in Terraform"
  type        = list(number)
  default     = [1, 2, 3]
}

variable "map_expamle" {
  description = "An exapmle of a map in Terraform"
  type        = map(string)
  default = {
    key1 = "value1"
    key2 = "value2"
    key3 = "value3"
  }
}

variable "object_example" {
  description = "An exapmle of a structural type in Terraform"
  type = object({
    name    = string
    age     = number
    tags    = list(string)
    enabled = bool
  })

  default = {
    name    = "value1"
    age     = 42
    tags    = ["a", "b", "c"]
    enabled = true
  }
}
