data "template_file" "lambda_trust" {
  template = file("${path.module}/lambda_json/trust.json")
  vars     = {}
}

data "template_file" "lambda_policy" {
  template = file("${path.module}/json/interface_lambda/policy.json")
  vars = {
    region     = var.region
    account_id = data.aws_ssm_parameter.account_id.value
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda_exec_role"
  assume_role_policy = data.template_file.lambda_trust.rendered

  tags = {
    Service       = var.Service
    Environment   = var.Environment
    SvcOwner      = var.SvcOwner
    DeployedUsing = var.DeployedUsing
    SvcCodeURL    = var.SvcCodeURL
  }
}

resource "aws_iam_role_policy" "lambda_exec_role_policy" {
  name   = "lambda_exec_role_policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.template_file.lambda_policy.rendered
}
