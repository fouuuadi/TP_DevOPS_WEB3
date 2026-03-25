# Variables Terraform avec validation

variable "app_name" {
  description = "Nom de l'application"
  type        = string
  default     = "quotes-api"
}

variable "web_port" {
  description = "Port externe du serveur web"
  type        = number
  default     = 8080
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "L'environnement doit etre dev, staging ou prod."
  }
}

# Locals pour eviter de repeter les memes expressions partout
locals {
  common_tags = {
    project     = var.app_name
    environment = var.environment
    managed_by  = "terraform"
  }

  container_name = "${var.app_name}-${var.environment}"
}

# Data source pour recuperer le reseau bridge existant
data "docker_network" "bridge" {
  name = "bridge"
}
