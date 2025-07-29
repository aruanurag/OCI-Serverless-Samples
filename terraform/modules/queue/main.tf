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