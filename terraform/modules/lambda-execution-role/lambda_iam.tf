data "aws_iam_policy_document" "lambda_exec_policy" {
  statement {
    sid    = ""
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/google_data_to_splunk/credentials",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/cabinetoffice.gov.uk/google_data_to_splunk/credentials",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/google_data_to_splunk/subject_email",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/cabinetoffice.gov.uk/google_data_to_splunk/subject_email",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/google_data_to_splunk/admin_readonly_scope",
      "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/google_data_to_splunk/groups_scope"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:send_ggroup_data_to_splunk",
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:send_ggroup_data_to_splunk_co"
    ]
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "ggroup_lambda_exec_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec_role_trust_policy.json

  tags = local.tags
}

resource "aws_iam_role_policy" "lambda_exec_role_policy" {
  name   = "ggroup_lambda_exec_role_policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_exec_policy.json
}

data "aws_iam_policy_document" "lambda_exec_role_trust_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
