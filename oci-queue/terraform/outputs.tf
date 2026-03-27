output "queue_id" {
  description = "The OCID of the created OCI Queue"
  value       = module.oci_queue.queue_id
}

output "queue_display_name" {
  description = "The display name of the created OCI Queue"
  value       = module.oci_queue.queue_display_name
}

output "queue_messages_endpoint" {
  description = "The endpoint for sending and receiving messages"
  value       = module.oci_queue.queue_messages_endpoint
}

output "queue_state" {
  description = "The current state of the OCI Queue"
  value       = module.oci_queue.queue_state
}

output "queue_retention_in_seconds" {
  description = "The retention period configured for the queue"
  value       = module.oci_queue.queue_retention_in_seconds
}

output "queue_visibility_in_seconds" {
  description = "The visibility timeout configured for the queue"
  value       = module.oci_queue.queue_visibility_in_seconds
}

output "dead_letter_queue_id" {
  description = "The OCID of the dead letter queue"
  value       = module.oci_queue.dead_letter_queue_id
}

output "dead_letter_queue_endpoint" {
  description = "The endpoint for the dead letter queue"
  value       = module.oci_queue.dead_letter_queue_endpoint
}
