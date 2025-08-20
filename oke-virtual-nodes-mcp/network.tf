#network.tf

# network config follows standards from documentation: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengnetworkconfig-virtualnodes.htm
# ------------ Network Configuration ------------
module "network" {
  source = "../terraform/modules/vcn"

  compartment_id     = var.compartment_id
  region             = var.region
  vcn_cidr           = "10.0.0.0/16"
  create_nat_gateway = true # We need this for the private subnet
  create_service_gateway = true

  subnets = {
    "control_plane" = {
      cidr_block = "10.0.0.0/28"
      is_public  = true
      dns_label  = "control"
    },
    "data_plane" = {
      cidr_block = "10.0.10.0/19"
      is_public  = false
      dns_label  = "data"
      use_service_gateway = true
    },
    "load_balancer" = {
      cidr_block = "10.0.32.0/24"
      is_public  = true
      dns_label  = "lb"
    }
  }
}

# Local variables
locals {
  # This should match the CIDR of your virtual node/pods subnet
  nodes_pods_cidr = "10.0.10.0/19"

  ingress_rules = {
    "external_api" = {
      description = "External access to Kubernetes API endpoint."
      protocol    = "6" # TCP
      source      = "0.0.0.0/0"
      port        = 6443
    },
    "nodes_to_api" = {
      description = "Virtual node to Kubernetes API endpoint communication."
      protocol    = "6" # TCP
      source      = local.nodes_pods_cidr
      port        = 6443
    },
    "nodes_to_control_plane" = {
      description = "Virtual node to control plane communication."
      protocol    = "6" # TCP
      source      = local.nodes_pods_cidr
      port        = 12250
    },
    "path_discovery_in" = {
      description = "Path Discovery."
      protocol    = "1" # ICMP
      source      = local.nodes_pods_cidr
      icmp_type   = 3
      icmp_code   = 4
    }
  }

  egress_rules = {
    "api_to_oci_services" = {
      description = "Allow K8s API to communicate with regional OCI service endpoints."
      protocol    = "6" # TCP
      destination = "all-iad-services-in-oracle-services-network"
      dest_type   = "SERVICE_CIDR_BLOCK"
      port        = 443
    },
    "api_to_nodes" = {
      description = "Allow Kubernetes API endpoint to communicate with virtual nodes."
      protocol    = "all"
      destination = local.nodes_pods_cidr
      dest_type   = "CIDR_BLOCK"
    },
    "path_discovery_out" = {
      description = "Path Discovery."
      protocol    = "1"
      destination = local.nodes_pods_cidr
      dest_type   = "CIDR_BLOCK"
      icmp_type   = 3
      icmp_code   = 4
    }
  }
}

# Create the Network Security Group for the K8s API Endpoint
resource "oci_core_network_security_group" "oke_api_endpoint_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = module.network.vcn_id
  display_name   = "OKE-API-Endpoint-NSG"
}

resource "oci_core_network_security_group_security_rule" "oke_api_ingress_rules" {
  for_each = local.ingress_rules

  network_security_group_id = oci_core_network_security_group.oke_api_endpoint_nsg.id
  direction                 = "INGRESS"
  protocol                  = each.value.protocol
  source_type               = "CIDR_BLOCK"
  source                    = each.value.source
  description               = each.value.description
  stateless                 = false

  dynamic "tcp_options" {
    for_each = each.value.protocol == "6" ? [1] : []
    content {
      destination_port_range {
        min = each.value.port
        max = each.value.port
      }
    }
  }

  dynamic "icmp_options" {
    for_each = each.value.protocol == "1" ? [1] : []
    content {
      type = each.value.icmp_type
      code = each.value.icmp_code
    }
  }
}

resource "oci_core_network_security_group_security_rule" "oke_api_egress_rules" {
  for_each = local.egress_rules

  network_security_group_id = oci_core_network_security_group.oke_api_endpoint_nsg.id
  direction                 = "EGRESS"
  protocol                  = each.value.protocol
  destination_type          = each.value.dest_type
  destination               = each.value.destination
  description               = each.value.description
  stateless                 = false

  dynamic "tcp_options" {
    for_each = each.value.protocol == "6" ? [1] : []
    content {
      destination_port_range {
        min = each.value.port
        max = each.value.port
      }
    }
  }

  dynamic "icmp_options" {
    for_each = each.value.protocol == "1" ? [1] : []
    content {
      type = each.value.icmp_type
      code = each.value.icmp_code
    }
  }
}
