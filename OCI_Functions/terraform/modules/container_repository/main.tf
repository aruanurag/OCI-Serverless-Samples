resource "oci_artifacts_container_repository" "container_repo" {
  compartment_id = var.compartment_id
  display_name   = var.container_repository_name
  is_public      = false
}

output "container_repository_id" {
  value = oci_artifacts_container_repository.container_repo.id
} 