# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

variable "function_name" {
  description = "The name of the function."
  type        = string
}

variable "application_id" {
  description = "The OCID of the Functions application."
  type        = string
}

variable "source_image" {
  description = "The source image for the function."
  type        = string
}

variable "compartment_id" {
  description = "The OCID of the compartment."
  type        = string
}

variable "region" {
  description = "The OCI region."
  type        = string
}


variable "path" {
  description = "The API Gateway path for the function route."
  type        = string
  default     = null
}

variable "apigw_id" {
  description = "The OCID of the API Gateway."
  type        = string
  default     = null
}

variable "function_config" {
  type = map(string)
  # default = {
  #   COMPARTMENT_ID   = ""
  #   OCI_REGION       = ""
  #   NOSQL_TABLE_NAME = ""
  # }
}
