resource "aws_codepipeline" "google-groups-to-splunk-contract-test" {
  name     = "${var.pipeline_name}-contract-test"
  role_arn = data.aws_iam_role.pipeline_role.arn
  tags     = merge(local.tags, { Name = "${var.pipeline_name}-contract-test" })

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
      output_artifacts = ["google-groups-to-splunk"]
      configuration = {
        ConnectionArn    = "arn:aws:codestar-connections:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:connection/${var.codestar_connection_id}"
        FullRepositoryId = "alphagov/cyber-security-ggroup-data-to-splunk"
        BranchName       = "master"
      }
    }
  }

  stage {
    name = "GoogleContractTests"

    action {
      name            = "GoogleContractTests"
      category        = "Test"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["google-groups-to-splunk"]
      configuration = {
        ProjectName = aws_codebuild_project.google-contract-tests.name
      }
    }
  }
}
