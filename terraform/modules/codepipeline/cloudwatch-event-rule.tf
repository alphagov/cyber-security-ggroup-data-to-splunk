resource "aws_cloudwatch_event_rule" "weekday-google-contract-tests-trigger" {
  name                = "weekday-google-contract-tests-trigger"
  description         = "An event rule to trigger a pipeline"
  schedule_expression = "cron(0 8 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "codepipeline" {
  rule     = aws_cloudwatch_event_rule.weekday-google-contract-tests-trigger.name
  arn      = aws_codepipeline.google-groups-to-splunk-contract-test.arn
  role_arn = data.aws_iam_role.pipeline_role.arn
}
