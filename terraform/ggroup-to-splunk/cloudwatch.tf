# resource "aws_cloudwatch_log_group" "google_group_data" {
#   name = "/aws/lambda/google-group-data"

#   tags = {
#     Environment = var.Environment
#     Service     = var.Service
#   }
# }

resource "aws_cloudwatch_log_subscription_filter" "log_subscription" {
  name = "log_subscription"

  log_group_name  = "/aws/lambda/send_ggroup_data_to_splunk"
  filter_pattern  = ""
  destination_arn = "arn:aws:logs:eu-west-2:885513274347:destination:csls_cw_logs_destination_prod"
}