variable "compartment_ocid" {
  description = "The OCID of the compartment."
  type        = string
}

variable "queue_name" {
  description = "The name of the OCI queue."
  type        = string
}

variable "application_display_name" {
  description = "Name of function application."
  type        = string
}

variable "subnet_ocid" {
  description = "The OCID of the subnet."
  type        = string
}

variable "functions" {
  description = "A map of function configurations. The key is the function name."
  type = map(object({
    source_image = optional(string, null)
    path = optional(string, null)
  }))
}

variable "region" {
  description = "The OCI region."
  type        = string
}

variable "apigw_id" {
  description = "The OCID of the API Gateway."
  type        = string
}

variable "tenancy_ocid" {
  description = "The OCID of the tenancy."
  type        = string
}

variable "container_repository_name" {
  description = "Name of the OCI Container Repository."
  type        = string
} 