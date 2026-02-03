# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

region                    = "us-ashburn-1"
compartment_ocid          = "ocid1.compartment.oc1..exampleuniqueID"
subnet_ocid               = "ocid1.subnet.oc1..exampleuniqueID"
functions = {
    "customer_info" = {
      # This function will be SKIPPED because its source_image is null.
      source_image = null #Change this to image name after uploading image to OCIR
      path = "/customer"
    }
    "place-order" = {
      # This function will be SKIPPED because its source_image is null.
      source_image = null #Change this to image name after uploading image to OCIR
      path = "/order"
    }
}