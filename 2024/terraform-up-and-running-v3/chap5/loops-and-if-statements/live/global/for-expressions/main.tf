terraform {
  required_version = ">= 1.0.0, < 2.0.0"
}

variable "names" {
  description = "A list of names"
  type        = list(string)
  default     = ["neo", "tirinity", "morpheus"]
}

output "upper_names" {
  value = [for name in var.names : upper(name)]
}

output "shot_upper_names" {
  value = [for name in var.names : upper(name) if length(name) < 5]
}

variable "hero_thousand_faces" {
  description = "map"
  type        = map(string)
  default = {
    neo      = "hero"
    trinity  = "love interest"
    morpheus = "mentor"
  }
}

output "bios" {
  value = [for name, role in var.hero_thousand_faces : "${name} is the ${role}"]
}

output "upper_roles" {
  value = [for name, role in var.hero_thousand_faces : "${name} is the ${role}"]
}
