# main.tf
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
}

resource "oci_identity_policy" "mcp_workload_policy" {
  compartment_id = var.tenancy_ocid  

  name        = "mcp-workload-policy"
  description = "Allow OKE workload identity (fastmcp-server-sa in mcp namespace) to manage resources"

  statements = [
    <<EOT
Allow any-user to manage all-resources in tenancy where all {
  request.principal.type = 'workload',
  request.principal.namespace = 'mcp',
  request.principal.service_account = 'fastmcp-server-sa',
  request.principal.cluster_id = '${module.oke_virtual_nodes.cluster_id}'
}
EOT
  ]
}

module "container_repository" {
  source                    = "../terraform/modules/container_repository"
  compartment_id            = var.compartment_id
  container_repository_name = var.mcp_container_repository_name
} 

module "nosql" {
  source           = "../terraform/modules/nosql"
  compartment_id   = var.compartment_id
  nosql_table_name = var.nosql_table_name
}

resource "oci_nosql_table" "order_info" {
  compartment_id = var.compartment_id
  name           = var.order_table_name
  table_limits {
    max_read_units     = 50
    max_write_units    = 50
    max_storage_in_gbs = 1
  }
  ddl_statement = <<DDL
    CREATE TABLE ${var.order_table_name} (
      customerId STRING,
      orderId STRING,
      status STRING,
      date TIMESTAMP(0),
      amount DOUBLE,
      PRIMARY KEY (orderId, customerId)
    )
  DDL
}

# 1. Create Notifications Topic
resource "oci_ons_notification_topic" "email_topic" {
  compartment_id = var.compartment_id
  name           = "order-events-topic"
  description    = "Notification topic for order events"
}

# 2. Create Subscription to send email
resource "oci_ons_subscription" "email_subscription" {
  compartment_id = var.compartment_id
  topic_id       = oci_ons_notification_topic.email_topic.id
  protocol       = "EMAIL"
  endpoint       = var.notification_email  # the email address to receive notifications
}