resource "aws_codepipeline" "google-groups-to-splunk" {
  name     = var.pipeline_name
  role_arn = data.aws_iam_role.pipeline_role.arn
  tags     = merge(local.tags, { Name = var.pipeline_name })

  artifact_store {
    type     = "S3"
    location = data.aws_s3_bucket.artifact_store.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["google_groups_to_splunk"]
      configuration = {
        ConnectionArn    = "arn:aws:codestar-connections:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:connection/${var.codestar_connection_id}"
        FullRepositoryId = "alphagov/cyber-security-ggroup-data-to-splunk"
        BranchName       = "master"
      }
    }
  }

  stage {
    name = "CodeValidation"

    action {
      name            = "CodeValidation"
      category        = "Test"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["google_groups_to_splunk"]
      configuration = {
        ProjectName = aws_codebuild_project.code-validation.name
      }
    }
  }

  stage {
    name = "BuildZip"

    action {
      name = "BuildZip"
      category = "Build"
      owner = "AWS"
      provider = "CodeBuild"
      version = "1"
      input_artifacts = ["google_groups_to_splunk"]
      output_artifacts = ["lambda_zip"]
      configuration = {
        ProjectName = aws_codebuild_project.build-zip.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name = "dev-deploy"
      category = "Build"
      owner = "AWS"
      provider = "CodeBuild"
      version = "1"
      run_order = 1
      input_artifacts = ["google_groups_to_splunk", "lambda_zip"]
      configuration = {
        PrimarySource = "google_groups_to_splunk"
        ProjectName = module.terraform_apply_dev.project_name
      }
    }

    action {
      name = "prod-deploy"
      category = "Build"
      owner = "AWS"
      provider = "CodeBuild"
      version = "1"
      run_order = 2
      input_artifacts = ["google_groups_to_splunk", "lambda_zip"]
      configuration = {
        PrimarySource = "google_groups_to_splunk"
        ProjectName = module.terraform_apply_prod.project_name
      }
    }
    action {
      name = "prod-co-deploy"
      category = "Build"
      owner = "AWS"
      provider = "CodeBuild"
      version = "1"
      run_order = 2
      input_artifacts = ["google_groups_to_splunk", "lambda_zip"]
      configuration = {
        PrimarySource = "google_groups_to_splunk"
        ProjectName = module.terraform_apply_prod_co.project_name
      }
    }
  }

  stage {
    name = "Update"

    action {
      name             = "UpdatePipeline"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["google_groups_to_splunk"]
      output_artifacts = []

      configuration = {
        ProjectName = module.self-update.project_name
      }
    }
  }
}
