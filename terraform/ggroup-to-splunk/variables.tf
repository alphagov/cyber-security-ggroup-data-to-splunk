variable "lambda_zip_location" {
  description = "Location of the lambda zip"
  type        = string
  default     = ""
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
  default = "ggroup_data_to_splunk"
}

variable "environment" {
  default = "test"
}

variable "svc_owner" {
  default = "cyber"
}

variable "deployed_using" {
  default = "terraform"
}
