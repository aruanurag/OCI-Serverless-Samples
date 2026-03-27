terraform {
  required_version = ">= 1.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.0"
    }
  }
}

resource "oci_queue_queue" "main" {
  compartment_id = var.compartment_id
  display_name   = var.queue_display_name
  
  # Queue configuration
  retention_in_seconds = var.retention_in_seconds
  visibility_in_seconds = var.visibility_in_seconds
  timeout_in_seconds = var.timeout_in_seconds
  
  # Dead letter queue configuration (optional)
  dead_letter_queue_delivery_attempts = var.dead_letter_queue_delivery_attempts

  # Tags
  freeform_tags = var.freeform_tags
  defined_tags  = var.defined_tags

  lifecycle {
    create_before_destroy = true
  }
}

# Dead Letter Queue (optional)
resource "oci_queue_queue" "dead_letter_queue" {
  count              = var.create_dead_letter_queue ? 1 : 0
  compartment_id     = var.compartment_id
  display_name       = "${var.queue_display_name}-dlq"
  retention_in_seconds = var.dlq_retention_in_seconds

  freeform_tags = merge(
    var.freeform_tags,
    { "Purpose" = "DeadLetterQueue" }
  )
  defined_tags = var.defined_tags
}
