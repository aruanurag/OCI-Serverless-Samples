# main.tf

# Configure the Oracle Cloud Infrastructure provider
provider "oci" {}

# Get a list of availability domains in the region
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

# ------------ OKE Cluster Configuration ------------

# Create the OKE Cluster (Control Plane)
module "oke_virtual_nodes" {
  source                  = "../terraform/modules/oke-virtual-nodes"
  tenancy_ocid            = var.tenancy_ocid
  compartment_ocid        = var.compartment_id
  region                  = var.region
  vcn_id                  = module.network.vcn_id
  control_plane_subnet_id = module.network.subnets["control_plane"].id
  virtual_nodes_subnet_id = module.network.subnets["data_plane"].id
  load_balancer_subnet_id = module.network.subnets["load_balancer"].id
  kubernetes_version      = var.kubernetes_version
  cluster_name            = var.cluster_name
  api_endpoint_nsg_ids    = [oci_core_network_security_group.oke_api_endpoint_nsg.id]
}

resource "oci_identity_policy" "mcp_workload_policy" {
  compartment_id = var.tenancy_ocid  

  name        = "mcp-workload-policy"
  description = "Allow OKE workload identity (fastmcp-server-sa in mcp namespace) to manage resources"

  statements = [
    <<EOT
Allow any-user to manage all-resources in tenancy where all {
  request.principal.type = workload,
  request.principal.namespace = mcp,
  request.principal.service_account = fastmcp-server-sa,
  request.principal.cluster_id = ${module.oke_virtual_nodes.cluster_id}
}
EOT
  ]
}

module "container_repository" {
  source                    = "../terraform/modules/container_repository"
  compartment_id            = var.compartment_id
  container_repository_name = var.mcp_container_repository_name
} 