#network.tf

# network config follows standards from documentation: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengnetworkconfig-virtualnodes.htm
# ------------ Network Configuration ------------
module "network" {
  source                 = "../terraform/modules/vcn"
  compartment_id         = var.compartment_id
  region                 = var.region
  vcn_cidr               = "10.0.0.0/16"
  create_nat_gateway     = true
  create_service_gateway = true

  subnets = {
    "control_plane" = {
      cidr_block = "10.0.0.0/28"
      is_public  = true
      dns_label  = "control"
    },
    "data_plane" = {
      cidr_block          = "10.0.8.0/21"
      is_public           = false
      dns_label           = "data"
      use_service_gateway = true
    },
    "load_balancer" = {
      cidr_block = "10.0.20.0/24"
      is_public  = true
      dns_label  = "lb"
    }
  }

  security_lists = {
    control_plane = {
      ingress_rules = [
        { protocol = "6", source = "0.0.0.0/0", tcp_min = 6443, tcp_max = 6443 },                  #ingress 443 from 0.0.0.0/0
        { protocol = "6", source = var.data_subnet_cidr_block, tcp_min = 12250, tcp_max = 12250 }, #ingress 12250 from data plane
        { protocol = "1", source = var.data_subnet_cidr_block, icmp_type = 3, icmp_code = 4 }      #egress ICMP path discovery from data_plane
      ]
      egress_rules = [
        {
          protocol    = "6", #egress 443 to all OCI services in region
          dest_type   = "SERVICE_CIDR_BLOCK",
          destination = "all-${local.current_region_short_lower}-services-in-oracle-services-network",
          tcp_min     = 443, tcp_max = 443
        },
        { protocol = "6", destination = var.data_subnet_cidr_block },                              #egress all TCP to data plane
        { protocol = "1", destination = var.data_subnet_cidr_block, icmp_type = 3, icmp_code = 4 } #egress ICMP path discovery to data plane
      ]
    }
    data_plane = {
      ingress_rules = [
        { protocol = "all", source = var.data_subnet_cidr_block },                                #ingress all from data plane
        { protocol = "6", source = var.control_subnet_cidr_block }, #ingress all TCP from control plane
        { protocol = "1", source = var.control_subnet_cidr_block, icmp_type = 3, icmp_code = 4 }  #ingress ICMP path discovery from control plane
      ]
      egress_rules = [
        { protocol = "all", destination = "0.0.0.0/0" } #egress all to 0.0.0.0/0
      ]
    }
    load_balancer = {
      ingress_rules = [
        { protocol = "6", source = "0.0.0.0/0", tcp_min = 80, tcp_max = 80 },  #ingress 80 from 0.0.0.0/0
        { protocol = "6", source = "0.0.0.0/0", tcp_min = 443, tcp_max = 443 } #ingress 443 from 0.0.0.0/0
      ]
      egress_rules = [
        { protocol = "6", destination = var.data_subnet_cidr_block, tcp_min = 30000, tcp_max = 32767 }, #egress TCP & UDP to data plane
        { protocol = "17", destination = var.data_subnet_cidr_block, min = 30000, max = 32767 },
        { protocol = "6", destination = var.data_subnet_cidr_block, tcp_min = 10256, tcp_max = 10256 }, #egress TCP & UDP to data plane
        { protocol = "17", destination = var.data_subnet_cidr_block, min = 10256, max = 10256 },
      ]
    }
  }
}


# # Local variables
# locals {
#   ingress_rules = {
#     "external_api" = {
#       description = "External access to Kubernetes API endpoint."
#       protocol    = "6" # TCP
#       source      = "0.0.0.0/0"
#       port        = 6443
#     },
#     "nodes_to_api" = {
#       description = "Virtual node to Kubernetes API endpoint communication."
#       protocol    = "6" # TCP
#       source      = var.data_subnet_cidr_block
#       port        = 6443
#     },
#     "nodes_to_control_plane" = {
#       description = "Virtual node to control plane communication."
#       protocol    = "6" # TCP
#       source      = var.data_subnet_cidr_block
#       port        = 12250
#     },
#     "path_discovery_in" = {
#       description = "Path Discovery."
#       protocol    = "1" # ICMP
#       source      = var.data_subnet_cidr_block
#       icmp_type   = 3
#       icmp_code   = 4
#     }
#   }

#   egress_rules = {
#     "api_to_oci_services" = {
#       description = "Allow K8s API to communicate with regional OCI service endpoints."
#       protocol    = "6" # TCP
#       destination = "all-iad-services-in-oracle-services-network"
#       dest_type   = "SERVICE_CIDR_BLOCK"
#       port        = 443
#     },
#     "api_to_nodes" = {
#       description = "Allow Kubernetes API endpoint to communicate with virtual nodes."
#       protocol    = "all"
#       destination = var.data_subnet_cidr_block
#       dest_type   = "CIDR_BLOCK"
#     },
#     "path_discovery_out" = {
#       description = "Path Discovery."
#       protocol    = "1"
#       destination = var.data_subnet_cidr_block
#       dest_type   = "CIDR_BLOCK"
#       icmp_type   = 3
#       icmp_code   = 4
#     }
#   }
# }

# # Create the Network Security Group for the K8s API Endpoint
# resource "oci_core_network_security_group" "oke_api_endpoint_nsg" {
#   compartment_id = var.compartment_id
#   vcn_id         = module.network.vcn_id
#   display_name   = "OKE-API-Endpoint-NSG"
# }

# resource "oci_core_network_security_group_security_rule" "oke_api_ingress_rules" {
#   for_each = local.ingress_rules

#   network_security_group_id = oci_core_network_security_group.oke_api_endpoint_nsg.id
#   direction                 = "INGRESS"
#   protocol                  = each.value.protocol
#   source_type               = "CIDR_BLOCK"
#   source                    = each.value.source
#   description               = each.value.description
#   stateless                 = false

#   dynamic "tcp_options" {
#     for_each = each.value.protocol == "6" ? [1] : []
#     content {
#       destination_port_range {
#         min = each.value.port
#         max = each.value.port
#       }
#     }
#   }

#   dynamic "icmp_options" {
#     for_each = each.value.protocol == "1" ? [1] : []
#     content {
#       type = each.value.icmp_type
#       code = each.value.icmp_code
#     }
#   }
# }

# resource "oci_core_network_security_group_security_rule" "oke_api_egress_rules" {
#   for_each = local.egress_rules

#   network_security_group_id = oci_core_network_security_group.oke_api_endpoint_nsg.id
#   direction                 = "EGRESS"
#   protocol                  = each.value.protocol
#   destination_type          = each.value.dest_type
#   destination               = each.value.destination
#   description               = each.value.description
#   stateless                 = false

#   dynamic "tcp_options" {
#     for_each = each.value.protocol == "6" ? [1] : []
#     content {
#       destination_port_range {
#         min = each.value.port
#         max = each.value.port
#       }
#     }
#   }

#   dynamic "icmp_options" {
#     for_each = each.value.protocol == "1" ? [1] : []
#     content {
#       type = each.value.icmp_type
#       code = each.value.icmp_code
#     }
#   }
# }

locals {
  current_region_short_lower = [
    for r in data.oci_identity_region_subscriptions.this.region_subscriptions :
    lower(r.region_key) if r.region_name == var.region
  ][0]
}
