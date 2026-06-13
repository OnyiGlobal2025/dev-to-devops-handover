variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name, used for naming and tags"
  type        = string
  default     = "notes"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "image_tag" {
  description = "Container image tag to deploy"
  type        = string
  default     = "latest"
}