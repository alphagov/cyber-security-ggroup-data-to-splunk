resource "aws_lambda_function" "send_ggroup_data_to_splunk" {
  filename         = var.lambda_zip_location
  source_code_hash = filebase64sha256(var.lambda_zip_location)
  function_name    = "send_ggroup_data_to_splunk${var.suffix}"
  role             = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.lambda_role_name}"
  handler          = "lambda_function.main"
  runtime          = var.runtime
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

  environment {
    variables = {
      CREDENTIALS  = "${var.credentials_prefix}/google_data_to_splunk/credentials"
      SUBJECT      = "${var.credentials_prefix}/google_data_to_splunk/subject_email"
      ADMIN_SCOPE  = "/google_data_to_splunk/admin_readonly_scope"
      GROUPS_SCOPE = "/google_data_to_splunk/groups_scope"
    }
  }

  tags = local.tags
}

resource "aws_cloudwatch_event_rule" "send_ggroup_data_to_splunk_every_hour" {
  name                = "ggroup-to-splunk-24-hours"
  description         = "Send google groups data to splunk every 24 hours"
  schedule_expression = "cron(0 * * * ? *)"
  tags                = local.tags
}

resource "aws_cloudwatch_event_target" "send_ggroup_data_to_splunk_every_hour_tg" {
  rule = aws_cloudwatch_event_rule.send_ggroup_data_to_splunk_every_hour.name
  arn  = aws_lambda_function.send_ggroup_data_to_splunk.arn
}

resource "aws_lambda_permission" "send_ggroup_data_to_splunk_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.send_ggroup_data_to_splunk.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.send_ggroup_data_to_splunk_every_hour.arn
}
