output "queue_id" {
  description = "The OCID of the created OCI Queue"
  value       = oci_queue_queue.main.id
}

output "queue_display_name" {
  description = "The display name of the created OCI Queue"
  value       = oci_queue_queue.main.display_name
}

output "queue_messages_endpoint" {
  description = "The endpoint for sending and receiving messages"
  value       = oci_queue_queue.main.messages_endpoint
}

output "queue_state" {
  description = "The current state of the OCI Queue"
  value       = oci_queue_queue.main.state
}

output "queue_retention_in_seconds" {
  description = "The retention period configured for the queue"
  value       = oci_queue_queue.main.retention_in_seconds
}

output "queue_visibility_in_seconds" {
  description = "The visibility timeout configured for the queue"
  value       = oci_queue_queue.main.visibility_in_seconds
}

output "dead_letter_queue_id" {
  description = "The OCID of the dead letter queue (if created)"
  value       = try(oci_queue_queue.dead_letter_queue[0].id, null)
}

output "dead_letter_queue_endpoint" {
  description = "The endpoint for the dead letter queue (if created)"
  value       = try(oci_queue_queue.dead_letter_queue[0].messages_endpoint, null)
}
