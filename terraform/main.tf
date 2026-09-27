terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.0"
    }
  }

  backend "s3" {
    bucket = "monitor-s3-bucket-state"
    key    = "state/terraform.tfstate"
    region = "eu-central-1"
  } 
}

provider "aws" {
  region = var.region
}

resource "aws_vpc" "monitor_vpc" {
  cidr_block = var.cidr_block
  tags = {
    Name = "monitor_vpc"
  }
}

resource "aws_internet_gateway" "monitor-gw" {
  vpc_id = aws_vpc.monitor_vpc.id

  tags = {
    Name = "monitor-gw"
  }
}

resource "aws_route_table" "monitor-rt" {
  vpc_id = aws_vpc.monitor_vpc.id
  route {
    cidr_block = var.default_cidr
    gateway_id = aws_internet_gateway.monitor-gw.id
  }
  tags = {
    Name = "monitor-rt"
  }
}

resource "aws_route_table_association" "monitor-rta" {
  subnet_id      = aws_subnet.monitor_subnet.id
  route_table_id = aws_route_table.monitor-rt.id

}

resource "aws_subnet" "monitor_subnet" {
  vpc_id     = aws_vpc.monitor_vpc.id
  cidr_block = cidrsubnet(var.cidr_block, 8, 2)

  tags = {
    Name = "monitor-subnet"
  }
}

resource "aws_security_group" "monitor-sg" {
  name   = "monitor-sg"
  vpc_id = aws_vpc.monitor_vpc.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "monitor-sg"
  }
}

resource "aws_instance" "monitor" {
  ami                         = var.ami
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.monitor_subnet.id
  vpc_security_group_ids      = [aws_security_group.monitor-sg.id]
  key_name                    = aws_key_pair.deployer.key_name
  associate_public_ip_address = true

  tags = {
    Name = "monitor"
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "monitor-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

