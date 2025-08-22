#outputs.tf

output "cluster_id" {
  value = module.oke_virtual_nodes.cluster_id
}

output "virtual_node_pool_id" {
  value = module.oke_virtual_nodes.virtual_node_pool_id
}

output "process_order_repository_path" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.mcp_container_repository_name}"
}
