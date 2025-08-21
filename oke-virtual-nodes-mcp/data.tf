# Configure the Oracle Cloud Infrastructure provider
provider "oci" {}

# Get a list of availability domains in the region
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_identity_region_subscriptions" "this" {
  tenancy_id = var.tenancy_ocid
}

data "oci_identity_regions" "current" {
  filter {
    name = "name"
    values = [var.region]
  }
}

data "oci_objectstorage_namespace" "this" {}
