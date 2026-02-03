# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

resource "oci_apigateway_gateway" "main" {
  compartment_id = var.compartment_id
  display_name   = "main-gateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = var.subnet_id
}

output "gateway_id" {
  value = oci_apigateway_gateway.main.id
} 
