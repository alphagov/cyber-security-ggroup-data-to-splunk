resource "aws_lambda_function" "send_ggroup_data_to_splunk" {
  filename         = var.lambda_zip_location
  source_code_hash = filebase64sha256(var.lambda_zip_location)
  function_name    = "send_ggroup_data_to_splunk"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "send_ggroup_data_to_splunk.main"
  runtime          = var.runtime
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory

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
