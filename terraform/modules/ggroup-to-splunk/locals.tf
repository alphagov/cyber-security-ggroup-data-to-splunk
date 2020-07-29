locals {
  tags = {
    "Service"       = "ggroups_to_splunk"
    "SvcOwner"      = "cyber-security-engineering@digital.cabinet-office.gov.uk"
    "DeployedUsing" = "Terraform"
    "SvcCodeURL"    = "https://github.com/alphagov/cyber-security-ggroup-data-to-splunk/"
    "Environment"   = var.environment
  }
}
