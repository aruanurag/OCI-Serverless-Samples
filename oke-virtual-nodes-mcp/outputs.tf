#outputs.tf
output "mcp_server_repository_path" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.mcp_container_repository_name}"
}

output "notification_topic_id" {
  value = oci_ons_notification_topic.email_topic.id
}

output "subscription_id" {
  value = oci_ons_subscription.email_subscription.id
}
