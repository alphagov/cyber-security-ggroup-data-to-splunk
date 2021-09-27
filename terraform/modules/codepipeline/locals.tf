locals {
  tags = {
    Service       = "google-groups-to-splunk"
    Environment   = "prod"
    SvcOwner      = "Cyber"
    DeployedUsing = "Terraform_v12"
    SvcCodeURL    = "https://github.com/alphagov/cyber-security-ggroup-data-to-splunk"
  }
  docker_hub_username = jsondecode(data.aws_secretsmanager_secret_version.dockerhub_creds.secret_string)["username"]
  docker_hub_password = jsondecode(data.aws_secretsmanager_secret_version.dockerhub_creds.secret_string)["password"]
}
