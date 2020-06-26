module "splunk-hybrid-searchhead-prod" {
  prefix         = "prod-"
  region         = "eu-west-2"
  instance_type  = "c5.large"
  source         = "../../modules/splunk-hybrid-searchhead"
  fqdn           = "splunk-hsh.gds-cyber-security.digital"
  root_domain    = "gds-cyber-security.digital"
  environment    = "prod"
  splunk_hsh_eip = var.splunk_hsh_eip
}
