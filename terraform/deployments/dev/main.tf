module "ggroup-to-splunk-dev" {
  source              = "../../modules/ggroup-to-splunk"
  environment         = "staging"
  lambda_zip_location = "../../../get_data_for_google_groups.zip"
  runtime             = "python3.7"
  lambda_memory       = 256
  lambda_role_name    = "ggroup_lambda_exec_role"
  lambda_timeout      = 900
  account_id          = "489877524855"
}
