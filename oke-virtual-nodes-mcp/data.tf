# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

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
