resource "aws_cloudwatch_log_subscription_filter" "log_subscription" {
  name = "log_subscription"

  log_group_name  = aws_cloudwatch_log_group.send_ggroup_data_to_splunk.name
  filter_pattern  = ""
  destination_arn = "arn:aws:logs:eu-west-2:885513274347:destination:csls_cw_logs_destination_prod"
}

resource "aws_cloudwatch_log_group" "send_ggroup_data_to_splunk" {
  name = "/aws/lambda/${aws_lambda_function.send_ggroup_data_to_splunk.function_name}${var.suffix}"
  tags = local.tags
}
