module "oci_queue" {
  source = "../modules/oci-queue"

  compartment_id              = var.compartment_id
  queue_display_name          = var.queue_display_name
  retention_in_seconds        = var.retention_in_seconds
  visibility_in_seconds       = var.visibility_in_seconds
  timeout_in_seconds          = var.timeout_in_seconds
  dead_letter_queue_delivery_attempts = var.dead_letter_queue_delivery_attempts
  create_dead_letter_queue    = var.create_dead_letter_queue
  dlq_retention_in_seconds    = var.dlq_retention_in_seconds

  freeform_tags = merge(
    var.freeform_tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
  defined_tags = var.defined_tags
}
