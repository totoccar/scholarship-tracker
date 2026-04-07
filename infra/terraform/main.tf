terraform {
  required_version = ">= 1.6.0"

  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Placeholder para infraestructura futura (RDS, ECS, networking, etc.)
resource "null_resource" "bootstrap" {}
