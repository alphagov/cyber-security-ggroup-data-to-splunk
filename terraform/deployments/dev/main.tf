module "splunk-hybrid-searchhead-dev" {
  prefix              = "staging-"
  region              = "eu-west-2"
  source              = "../../modules/splunk-hybrid-searchhead"
  Environment         = "staging"
  lambda_zip_location = var.lambda_zip_location
  runtime             = var.runtime
  lambda_memory       = var.lambda_memory
  lambda_timeout      = var.lambda_timeout
  Service             = var.Service
  SvcOwner            = var.SvcOwner
  DeployedUsing       = var.DeployedUsing
}
