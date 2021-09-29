module "terraform_apply_dev" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = var.dev_deployment_account_id
  deployment_role_name        = var.dev_deployment_role_name
  terraform_directory         = "terraform/deployments/dev"
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "Deploy"
  action_name                 = "dev-deploy"
  environment                 = "dev"
  docker_hub_credentials      = var.docker_hub_credentials
  tags                        = local.tags
  copy_artifacts = [
    {
      artifact = "lambda_zip",
      source   = "get_data_for_google_groups.zip",
      target   = "."
    }
  ]
}
