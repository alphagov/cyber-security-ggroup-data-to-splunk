data "aws_ssm_parameter" "google_credentials" {
  name = "/Google-Data-To-Splunk/credentials"
}

data "aws_ssm_parameter" "subject_email" {
  name = "/Google-Data-To-Splunk/subject_email"
}

data "aws_ssm_parameter" "groups_scope" {
  name = "/Google-Data-To-Splunk/groups_scope"
}

data "aws_ssm_parameter" "admin_readonly_scope" {
  name = "/Google-Data-To-Splunk/admin_readonly_scope"
}

resource "aws_lambda_function" "send_ggroup_data_to_splunk" {
  filename         = var.lambda_zip_location
  source_code_hash = filebase64sha256(var.lambda_zip_location)
  function_name    = "send_ggroup_data_to_splunk"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda_function.main"
  runtime          = var.runtime
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      CREDENTIALS  = "/Google-Data-To-Splunk/credentials"
      SUBJECT      = "/Google-Data-To-Splunk/subject_email"
      ADMIN_SCOPE  = "/Google-Data-To-Splunk/admin_readonly_scope"
      GROUPS_SCOPE = "/Google-Data-To-Splunk/groups_scope"
    }
  }

  tags = {
    Service       = var.Service
    Environment   = var.Environment
    SvcOwner      = var.SvcOwner
    DeployedUsing = var.DeployedUsing
  }
}

resource "aws_cloudwatch_event_rule" "send_ggroup_data_to_splunk_24_hours" {
  name                = "ggroup-to-splunk-24-hours"
  description         = "Send google groups data to splunk every 24 hours"
  schedule_expression = "cron(0 23 * * ? *)"
}

resource "aws_cloudwatch_event_target" "send_ggroup_data_to_splunk_24_hours_tg" {
  rule = aws_cloudwatch_event_rule.send_ggroup_data_to_splunk_24_hours.name
  arn  = aws_lambda_function.send_ggroup_data_to_splunk.arn
}

resource "aws_lambda_permission" "send_ggroup_data_to_splunk_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.send_ggroup_data_to_splunk.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.send_ggroup_data_to_splunk_24_hours.arn
}
