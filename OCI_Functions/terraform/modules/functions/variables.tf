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

variable "nosql_table_name" {
  description = "The name of the NoSQL table."
  type        = string
} 