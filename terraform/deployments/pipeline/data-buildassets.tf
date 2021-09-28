data "aws_iam_role" "pipeline_role" {
  name = "CodePipelineExecutionRole"
}

data "aws_s3_bucket" "artifact_store" {
  bucket = "co-cyber-codepipeline-artifact-store"
}

data "aws_secretsmanager_secret_version" "dockerhub_creds" {
  secret_id = var.docker_hub_credentials
}

data "aws_secretsmanager_secret" "dockerhub_creds" {
  name = var.docker_hub_credentials
}
