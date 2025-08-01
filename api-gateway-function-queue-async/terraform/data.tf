data "oci_identity_tenancy" "home" {
  tenancy_id = var.tenancy_ocid
}

data "oci_identity_regions" "current" {
  filter {
    name = "name"
    values = [var.region]
  }
}

data "oci_objectstorage_namespace" "this" {}
