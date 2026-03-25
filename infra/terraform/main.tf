# Configuration Terraform principale
# On utilise le provider Docker pour gerer des conteneurs en local

terraform {
  required_version = ">= 1.5"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# Reseau partage entre les conteneurs
resource "docker_network" "app_network" {
  name = "devops-network"
}

# Image Nginx pour le reverse proxy
resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}

# Conteneur web principal
resource "docker_container" "web" {
  name  = "${var.app_name}-${var.environment}"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = var.web_port
  }

  networks_advanced {
    name = docker_network.app_network.name
  }

  env = [
    "NGINX_HOST=localhost",
    "NGINX_PORT=80"
  ]
}

# Outputs pour verifier que tout tourne
output "web_url" {
  value       = "http://localhost:${docker_container.web.ports[0].external}"
  description = "URL du serveur web"
}

output "container_id" {
  value = docker_container.web.id
}
