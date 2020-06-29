module "group-to-splunk-dev" {
  region              = "eu-west-2"
  source              = "../../ggroup-to-splunk"
  Environment         = "staging"
  lambda_zip_location = var.lambda_zip_location
  runtime             = var.runtime
  lambda_memory       = var.lambda_memory
  lambda_timeout      = var.lambda_timeout
  Service             = var.Service
  SvcOwner            = var.SvcOwner
  DeployedUsing       = var.DeployedUsing
  account_id          = var.account_id
}
