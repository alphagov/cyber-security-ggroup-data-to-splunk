resource "aws_iam_role" "lambda_exec_role" {
  name               = "ggroup_lambda_exec_role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json

  tags = {
    Service       = var.service
    Environment   = var.environment
    SvcOwner      = var.svc_owner
    DeployedUsing = var.deployed_using
  }
}

resource "aws_iam_role_policy" "lambda_exec_role_policy" {
  name   = "lambda_exec_role_policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_exec_policy.json
}
