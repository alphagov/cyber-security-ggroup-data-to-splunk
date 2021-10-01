resource "aws_codebuild_project" "google-contract-tests" {
  name        = "codepipeline-${var.pipeline_name}-google-contract-tests"
  description = "Check data from Google APIs to see if it's in the format we expect"

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

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = var.dev_deployment_account_id
    }

    environment_variable {
      name  = "ROLE_NAME"
      value = var.dev_deployment_role_name
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = file("${path.module}/codebuild-google-contract-tests.yml")
  }
}
