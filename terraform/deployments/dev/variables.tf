variable "lambda_zip_location" {
  default = "../lambda.zip"
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
  default = 2048
}

variable "lambda_timeout" {
  default = 900
}

variable "Service" {
  default = "ggroup-data-to-splunk"
}

variable "Environment" {
  default = "test"
}

variable "SvcOwner" {
  default = "cyber"
}

variable "DeployedUsing" {
  default = "terraform"
}