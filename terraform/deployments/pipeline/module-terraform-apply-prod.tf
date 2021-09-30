module "terraform_apply_prod" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = var.prod_deployment_account_id
  deployment_role_name        = var.prod_deployment_role_name
  terraform_directory         = "terraform/deployments/prod"
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  stage_name                  = "Deploy"
  action_name                 = "prod-deploy"
  environment                 = "prod"
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
