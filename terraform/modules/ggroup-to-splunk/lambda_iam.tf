resource "aws_iam_role" "ggroup_lambda_exec_role" {
  name               = "ggroup_lambda_exec_role"
  assume_role_policy = data.aws_iam_policy_document.ggroup_to_splunk_lambda_trust.json

  tags = local.tags
}

resource "aws_iam_role_policy" "ggroup_lambda_exec_rolepolicy" {
  name   = "ggroup_lambda_exec_role_policy"
  role   = aws_iam_role.ggroup_lambda_exec_role.id
  policy = data.aws_iam_policy_document.ggroup_to_splunk_lambda_policy.json
}
