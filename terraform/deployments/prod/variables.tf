variable "lambda_zip_location" {
  default = "../../../lambda/get_data_for_google_groups.zip"
}

variable "runtime" {
  description = "runtime for lambda"
  default     = "python3.7"
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "lambda_memory" {
  default = 256
}

variable "lambda_timeout" {
  default = 900
}

variable "service" {
  default = "ggroup-data-to-splunk"
}

variable "environment" {
  default = "prod"
}

variable "svc_owner" {
  default = "cyber"
}

variable "deployed_using" {
  default = "terraform"
}

variable "account_id" {
  default = "779799343306"
}
