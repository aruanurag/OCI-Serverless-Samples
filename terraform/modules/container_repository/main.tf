# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

resource "oci_artifacts_container_repository" "container_repo" {
  compartment_id = var.compartment_id
  display_name   = var.container_repository_name
  is_public      = false
}

output "container_repository_id" {
  value = oci_artifacts_container_repository.container_repo.id
} 
