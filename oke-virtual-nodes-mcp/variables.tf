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

variable "mcp_container_repository_name" {
  description = "The name of the container repository to use for the MCP container."
  default     = "mcp-server-repo"
}

variable "kubernetes_version" {
  description = "The version of Kubernetes to use for the OKE cluster."
  default     = "v1.33.1"
}

variable "cluster_name" {
  description = "The name of the OKE cluster."
  default     = "oke-cluster"
}

variable "control_subnet_cidr_block" {
  description = "The CIDR block for the control subnet."
  default     = "10.0.0.0/28"
}

variable "data_subnet_cidr_block" {
  description = "The CIDR block for the data subnet."
  default     = "10.0.16.0/20"
}

variable "load_balancer_subnet_cidr_block" {
  description = "The CIDR block for the public subnet."
  default     = "10.0.32.0/24"
}

variable "nosql_table_name" {
  default = "customer_info"
}

variable "order_table_name" {
  default = "order_info"
}
variable "notification_email" {
  
}
