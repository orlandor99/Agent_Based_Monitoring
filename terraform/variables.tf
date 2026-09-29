variable "region" {
  type        = string
  description = "AWS region for resources creation"
  default     = "eu-central-1"
}

variable "availability_zone" {
  type        = list(string)
  description = "availability zone for subnets"
  default     = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
}

variable "cidr_block" {
  type        = string
  description = "CIDR block for VPC"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "ami" {
  type        = string
  description = "ec2 ami"
}

variable "default_cidr" {
  type        = string
  description = "Internet gateway"
}

variable "ssh_key_path" {
  type        = string
  description = "Path to ssh key"
  default     = "~/.ssh/id_rsa.pub"
}