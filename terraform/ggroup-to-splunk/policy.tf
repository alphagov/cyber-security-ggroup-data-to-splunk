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
    resources = ["arn:aws:logs:${var.region}:${var.account_id}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.region}:${var.account_id}:parameter/Google-Data-To-Splunk/credentials",
      "arn:aws:ssm:${var.region}:${var.account_id}:parameter/Google-Data-To-Splunk/subject_email",
      "arn:aws:ssm:${var.region}:${var.account_id}:parameter/Google-Data-To-Splunk/admin_readonly_scope",
      "arn:aws:ssm:${var.region}:${var.account_id}:parameter/Google-Data-To-Splunk/groups_scope"
    ]
  }
}

data "aws_iam_policy_document" "trust_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}