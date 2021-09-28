variable "pipeline_name" {
  type    = string
  default = "google-groups-to-splunk"
}

variable "docker_hub_credentials" {
  description = "Name of the secret in SSM that stores the Docker Hub credentials"
  type        = string
}

variable "codestar_connection_id" {
  type = string
}

variable "codebuild_image" {
  type    = string
  default = "gdscyber/cyber-security-cd-base-image:latest"
}

variable "dev_deployment_account_id" {
   type = string
   default = "489877524855"
}

variable "dev_deployment_role_name" {
   type = string
   default = "CodePipelineDeployerRole_489877524855"
}
