variable "lambda_zip_location" {
  description = "Location of the lambda zip"
  type        = string
  default     = ""
}

variable "runtime" {
  description = "runtime for lambda"
  default     = "python3.7"
}

variable "lambda_memory" {
  default = 256
}

variable "lambda_timeout" {
  default = 900
}

variable "environment" {
  type = string
}

variable "lambda_role_name" {
  type = string
}


variable "credentials_prefix" {
  type    = string
  default = ""
}

variable "suffix" {
  type    = string
  default = ""
}