# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

output "vcn_id" {
  description = "The OCID of the created VCN."
  value       = oci_core_vcn.this.id
}

output "subnets" {
  description = "A map of the created subnets, with subnet OCIDs as values."
  value       = { for k, v in oci_core_subnet.this : k => v }
}