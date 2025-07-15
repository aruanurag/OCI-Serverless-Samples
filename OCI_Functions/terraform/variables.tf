
variable "region" {
  default = "us-ashburn-1"
}

variable "compartment_ocid" {
  default = "ocid1.compartment.oc1..exampleuniqueID"
}

variable "subnet_ocid" {
  default = "ocid1.subnet.oc1..exampleuniqueID"
}

variable "nosql_table_name" {
  default = "customer_info"
}

variable "container_repository_name" {
  description = "Name of the OCI Container Repository"
  default     = "customer_info_repo"
} 