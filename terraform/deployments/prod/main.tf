module "ggroup-to-splunk-prod" {
  region              = "eu-west-2"
  source              = "../../ggroup-to-splunk"
  environment         = "staging"
  lambda_zip_location = var.lambda_zip_location
  runtime             = var.runtime
  lambda_memory       = var.lambda_memory
  lambda_timeout      = var.lambda_timeout
  service             = var.service
  svc_owner           = var.svc_owner
  deployed_using      = var.deployed_using
}
