data "aws_iam_policy_document" "ggroup_to_splunk_lambda_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:eu-west-2:${var.account_id}:*"
    ]
  }

  statement {
      actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
      ]
      resources = [
      "*"
      ]
  }

  statement {
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"  
    ]
    
    resources = [
      "arn:aws:ssm:eu-west-2:${var.account_id}:parameter/google_data_to_splunk/*"
    ]
  }
}

data "aws_iam_policy_document" "ggroup_to_splunk_lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
