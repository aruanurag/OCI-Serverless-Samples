output "repository_url" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.container_repository_name}"
}