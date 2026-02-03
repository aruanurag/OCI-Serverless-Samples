# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

data "oci_identity_tenancy" "home" {
  tenancy_id = var.tenancy_ocid
}

data "oci_identity_regions" "current" {
  filter {
    name = "name"
    values = [var.region]
  }
}

# Data source for availability domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

data "oci_objectstorage_namespace" "this" {}
