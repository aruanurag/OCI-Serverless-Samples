#outputs.tf

output "cluster_id" {
  value = module.oke_virtual_nodes.cluster_id
}

output "virtual_node_pool_id" {
  value = module.oke_virtual_nodes.virtual_node_pool_id
}
