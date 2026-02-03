# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

output "cluster_id" {
  description = "The OCID of the created cluster."
  value       = oci_containerengine_cluster.oke_cluster.id
}

output "virtual_node_pool_id" {
  description = "The OCID of the virtual node pool."
  value       = oci_containerengine_virtual_node_pool.virtual_node_pool.id
}
