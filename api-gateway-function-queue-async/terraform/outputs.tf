output "post_order_repository_path" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.post_order_container_repository_name}"
}

output "process_order_repository_path" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.process_order_container_repository_name}"
}