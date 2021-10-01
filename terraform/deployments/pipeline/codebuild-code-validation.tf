resource "aws_codebuild_project" "code-validation" {
  name        = "codepipeline-${var.pipeline_name}-code-validation"
  description = "Run tests against Python and Terraform to make sure it is valid"

  service_role = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE", "LOCAL_SOURCE_CACHE"]
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = var.codebuild_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = false

    registry_credential {
      credential_provider = "SECRETS_MANAGER"
      credential          = data.aws_secretsmanager_secret.dockerhub_creds.arn
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${path.module}/codebuild-code-validation.yml")
  }
}
