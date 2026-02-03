# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

output "repository_path" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.container_repository_name}"
}
