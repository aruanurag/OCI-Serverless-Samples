
variable "region" {
  default = "us-ashburn-1"
}

variable "compartment_ocid" {
  default = "ocid1.compartment.oc1..exampleuniqueID"
}

variable "subnet_ocid" {
  default = "ocid1.subnet.oc1..exampleuniqueID"
}

variable "get_customer_function_ocid" {
  default = "ocid1.fnfunc.oc1..exampleuniqueID"
}

variable "post_customer_function_ocid" {
  default = "ocid1.fnfunc.oc1..exampleuniqueID"
}

variable "place_order_function_ocid" {
  default = "ocid1.fnfunc.oc1..exampleuniqueID"
}

variable "nosql_table_name" {
  default = "customer_info"
} 