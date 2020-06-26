terraform {
  backend "s3" {
    bucket = "cyber-security-ggroup-data-to-splunk-state-bucket-01"
    key    = "ggroup-data-to-splunk.tfstate"
    region = "eu-west-2"
  }
}
