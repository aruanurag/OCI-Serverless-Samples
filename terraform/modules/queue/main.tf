# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

resource "oci_queue_queue" "order_queue" {
  compartment_id = var.compartment_id
  display_name   = var.queue_name
}

output "queue_id" {
  value = oci_queue_queue.order_queue.id
}

output "queue_url" {
  value = oci_queue_queue.order_queue.messages_endpoint
} 