# Main Terraform configuration to provision OKE cluster with virtual nodes

# Provider configuration
provider "oci" {
}


# Module reference for OKE virtual nodes
module "oke_virtual_nodes" {
  source                   = "../terraform/modules/oke-virtual-nodes"
  tenancy_ocid             = var.tenancy_ocid
  compartment_ocid         = var.compartment_ocid
  region                   = var.region
  vcn_id                   = var.vcn_id
  control_plane_subnet_id  = var.control_plane_subnet_id
  load_balancer_subnet_id  = var.load_balancer_subnet_id
  virtual_nodes_subnet_id  = var.virtual_nodes_subnet_id
  cluster_name             = var.cluster_name
  kubernetes_version       = var.kubernetes_version
}

# Outputs
output "cluster_id" {
  value = module.oke_virtual_nodes.cluster_id
}

output "virtual_node_pool_id" {
  value = module.oke_virtual_nodes.virtual_node_pool_id
}