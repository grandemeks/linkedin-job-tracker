# Terraform blok - definise koja verzija Terraforma i providera je potrebna
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Koristi verziju 5.x, ne stariju
    }
  }
}

# Provider blok - govori Terraformu kako da se konektuje na AWS
provider "aws" {
  region = var.aws_region # Koristimo varijablu, ne hardcodujemo
}

# -----------------------------------------------------------------------------
# SSH KEY PAIR
# Terraform ce uploadovati tvoj public key na AWS
# Tako ces moci SSH-ovati na server bez passworda
# -----------------------------------------------------------------------------
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key" # job-tracker-key
  public_key = var.ssh_public_key
}

# -----------------------------------------------------------------------------
# SECURITY GROUP - Firewall za nas server
# Definisemo koje portove dozvoljavamo
# -----------------------------------------------------------------------------
resource "aws_security_group" "main" {
  name        = "${var.project_name}-sg"
  description = "Security group za ${var.project_name}"

  # SSH pristup - samo za nas
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # U produkciji ovo bi bio samo tvoj IP
  }

  # HTTP - za Traefik ingress
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # K3s API server - za kubectl i ArgoCD
  ingress {
    description = "K3s API"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound - dozvoljavamo sav izlazni saobracaj
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 znaci sve protokole
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# -----------------------------------------------------------------------------
# EC2 INSTANCE - Nas server gde ce K3s raditi
# -----------------------------------------------------------------------------

# Data source - dinamicki dohvatamo najnoviji Ubuntu 24.04 AMI
# Umjesto da hardcodujemo AMI ID koji se mijenja po regionima
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical (Ubuntu) official AWS account

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "main" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  key_name               = aws_key_pair.main.key_name
  vpc_security_group_ids = [aws_security_group.main.id]

  # Root disk - 20GB je dovoljno za K3s + nase aplikacije
  root_block_device {
    volume_size = 20
    volume_type = "gp3" # Noviji, brzi i jeftiniji od gp2
  }

  # User data - skript koji se pokrece kada se server prvi put bootuje
  # Instaliramo K3s automatski!
  user_data = <<-EOF
    #!/bin/bash
    # Update sistem
    apt-get update -y
    apt-get upgrade -y

    # Install K3s - lightweight Kubernetes
    curl -sfL https://get.k3s.io | sh -

    # Wait for K3s to start
    sleep 30

    # Allow ubuntu user to use kubectl without sudo
    mkdir -p /home/ubuntu/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
    chown ubuntu:ubuntu /home/ubuntu/.kube/config
    chmod 600 /home/ubuntu/.kube/config
  EOF

  tags = {
    Name        = "${var.project_name}-server"
    Environment = var.environment
    Project     = var.project_name
  }
}

# -----------------------------------------------------------------------------
# ELASTIC IP - Fiksna IP adresa za nas server
# Bez ovoga, svaki restart servera daje novu IP adresu
# -----------------------------------------------------------------------------
resource "aws_eip" "main" {
  instance = aws_instance.main.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-eip"
    Project = var.project_name
  }
}