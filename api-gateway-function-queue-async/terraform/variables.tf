variable "tenancy_ocid" {
  default = "ocid1.tenancy.oc1..exampleuniqueID"
}

variable "region" {
  default = "us-ashburn-1"
}

variable "compartment_ocid" {
  default = "ocid1.compartment.oc1..exampleuniqueID"
}

variable "subnet_ocid" {
  default = "ocid1.subnet.oc1..exampleuniqueID"
}

variable "queue_name" {
  description = "Name of the OCI Queue"
  default     = "OrderQueue"
}

variable "post_order_container_repository_name" {
  description = "Name of the OCI Container Repository"
  default     = "queue_async_repo"
}

variable "process_order_container_repository_name" {
  description = "Name of the OCI Container Repository"
  default     = "process_order"
}

variable "application_display_name" {
  description = "Name of function application"
  default     = "queue_async_app"
}

variable "nosql_table_name" {
  default = "order_info"
}

variable "functions" {
  description = "A map of function configurations. The key is the function name."
  type = map(object({
    source_image = optional(string, null)
    path         = optional(string, null)
    config       = map(string)
  }))
  default = {
    "place-order" = {
      # This function will be SKIPPED because its source_image is null.
      source_image = null #Change this to image name after uploading image to OCIR
      path         = "/order"
      config       = {}
    }
  }
}

variable "queue_poller_image" {
  type    = string
  default = null
}
