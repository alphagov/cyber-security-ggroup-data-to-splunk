# data "template_file" "lambda_trust" {
#   template = file("${path.module}/lambda_json/trust.json")
#   vars     = {}
# }

# data "template_file" "lambda_policy" {
#   template = file("${path.module}/lambda_json/policy.json")
#   vars = {
#     region     = var.region
#     account_id = var.account_id
#   }
# }

resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda_exec_role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json

  tags = {
    Service       = var.Service
    Environment   = var.Environment
    SvcOwner      = var.SvcOwner
    DeployedUsing = var.DeployedUsing
  }
}

resource "aws_iam_role_policy" "lambda_exec_role_policy" {
  name   = "lambda_exec_role_policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_exec_policy.json
}
 