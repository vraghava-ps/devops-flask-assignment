terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "venkat-flask-assessment-tfstate2026"
    key            = "flask-assessment/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks11"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "flask-devops-assessment"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}