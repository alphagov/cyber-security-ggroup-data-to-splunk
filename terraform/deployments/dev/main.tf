module "ggroup-to-splunk-dev" {
  source              = "../../modules/ggroup-to-splunk"
  environment         = "staging"
  lambda_zip_location = "../../../lambda/get_data_for_google_groups.zip"
  runtime             = "python3.7"
  lambda_memory       = 256
  lambda_timeout      = 900
  service             = "ggroup-data-to-splunk"
  svc_owner           = "cyber"
  deployed_using      = "terraform12"
}
