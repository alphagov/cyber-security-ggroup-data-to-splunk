module "self-update" {
  source                      = "github.com/alphagov/cyber-security-shared-terraform-modules//codebuild/codebuild_apply_terraform"
  codebuild_service_role_name = data.aws_iam_role.pipeline_role.name
  deployment_account_id       = data.aws_caller_identity.current.account_id
  deployment_role_name        = "CodePipelineDeployerRole_${data.aws_caller_identity.current.account_id}"
  terraform_directory         = "terraform/deployments/pipeline"
  codebuild_image             = var.codebuild_image
  pipeline_name               = var.pipeline_name
  environment                 = "prod"
  docker_hub_credentials      = var.docker_hub_credentials
  stage_name                  = "Update"
  action_name                 = "UpdatePipeline"
  tags                        = local.tags
}
