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
  api_endpoint_nsg_ids    = [oci_core_network_security_group.oke_api_endpoint_nsg.id]
}
