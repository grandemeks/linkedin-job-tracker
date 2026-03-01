# SVE varijable na jednom mjestu - lako mijenjati

# Svaka varijabla ima tip, opis i default value
# Ovo je "docs" tvoje infrastrukture

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "eu-central-1"
}

variable project_name {
  description = "Name of the project for tagging resources"
  type        = string
  default     = "job-tracker"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "prod"
}

variable "instance_type" {
  description = "EC2 tip instance - t4g.small je ARM Free Tier"
  type        = string
  default     = "t4g.small"
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 instance access"
  type        = string
  # Nema default - ide u tfvars fajl
}
