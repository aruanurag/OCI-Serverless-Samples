# variables.tf

variable "tenancy_ocid" {
  description = "The OCID of your tenancy."
}

variable "region" {
  description = "The OCI region where resources will be created."
  default     = "us-ashburn-1"
}

variable "compartment_id" {
  description = "The OCID of the compartment to create resources in."
}

variable "kubernetes_version" {
  description = "The version of Kubernetes to use for the OKE cluster."
  default     = "v1.33.1"
}