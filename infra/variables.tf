variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "environment" {
  type    = string
  default = "assessment"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_name" {
  type    = string
  default = "flaskdb"
}

variable "db_username" {
  type    = string
  default = "flaskadmin"
}

variable "jenkins_allowed_cidr" {
  description = "Your public IP address in CIDR notation, for example 203.0.113.10/32"
  type        = string
}

variable "github_repository" {
  description = "Repository in OWNER/REPO form"
  type        = string
}