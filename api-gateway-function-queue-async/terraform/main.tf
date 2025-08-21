terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "= 7.9.0"
    }
  }
}

provider "oci" {}

locals {
  function_configs = {
    for key, fn in var.functions : key => {
      source_image = fn.source_image
      path         = fn.path
      config = merge(fn.config, {
        COMPARTMENT_ID = var.compartment_ocid
        OCI_REGION     = var.region
        QUEUE_OCID     = module.queue.queue_id
      })
    }
  }
}


module "apigateway" {
  source         = "../../terraform/modules/apigateway"
  compartment_id = var.compartment_ocid
  subnet_id      = var.subnet_ocid
}

module "queue" {
  source         = "../../terraform/modules/queue"
  compartment_id = var.compartment_ocid
  queue_name     = var.queue_name
}

resource "oci_nosql_table" "order_info" {
  compartment_id = var.compartment_ocid
  name           = var.nosql_table_name
  table_limits {
    max_read_units     = 50
    max_write_units    = 50
    max_storage_in_gbs = 1
  }
  ddl_statement = <<DDL
    CREATE TABLE ${var.nosql_table_name} (
      order_id STRING,
      customer_id STRING,
      amount DOUBLE,
      created_at STRING,
      PRIMARY KEY (order_id)
    )
  DDL
}

resource "oci_functions_application" "queue_async_app" {
  compartment_id = var.compartment_ocid
  display_name   = var.application_display_name
  subnet_ids     = [var.subnet_ocid]
  shape          = "GENERIC_ARM"
}

module "place_order_function" {
  source          = "../../terraform/modules/functions"
  count           = local.function_configs["place-order"].source_image != null ? 1 : 0
  function_name   = "place-order"
  application_id  = oci_functions_application.queue_async_app.id
  path            = local.function_configs["place-order"].path
  source_image    = local.function_configs["place-order"].source_image
  compartment_id  = var.compartment_ocid
  region          = var.region
  apigw_id        = module.apigateway.gateway_id
  function_config = local.function_configs["place-order"].config
}

resource "oci_identity_policy" "function_queue_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to use queues"
  name           = "function_queue_access"
  statements = [
    "Allow dynamic-group function_dynamic_group to use queues in compartment id ${var.compartment_ocid}"
  ]
}

resource "oci_identity_dynamic_group" "function_dynamic_group" {
  compartment_id = var.tenancy_ocid
  description    = "Dynamic group containing all functions in compartment ${var.compartment_ocid}"
  matching_rule  = "ALL {resource.type = 'fnfunc', resource.compartment.id = '${var.compartment_ocid}'}"
  name           = "function_dynamic_group"
}

module "container_repository" {
  source                    = "../../terraform/modules/container_repository"
  compartment_id            = var.compartment_ocid
  container_repository_name = var.post_order_container_repository_name
}

module "container_repository_process_order" {
  source                    = "../../terraform/modules/container_repository"
  compartment_id            = var.compartment_ocid
  container_repository_name = var.process_order_container_repository_name
}

# Create Container Instance
resource "oci_container_instances_container_instance" "poll_queue_instance" {
  count               = var.queue_poller_image != null ? 1 : 0
  compartment_id      = var.compartment_ocid
  display_name        = "poll-queue-to-nosql"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape               = "CI.Standard.A1.Flex"
  shape_config {
    ocpus         = 1
    memory_in_gbs = 6
  }
  vnics {
    subnet_id    = var.subnet_ocid
    display_name = "poll-queue-vnic"
  }
  containers {
    image_url    = var.queue_poller_image
    display_name = "queue-poller-container"
    environment_variables = {
      "QUEUE_OCID" = module.queue.queue_id
      "TABLE_OCID" = oci_nosql_table.order_info.id
      "OCI_REGION" = var.region
    }
    is_resource_principal_disabled = false
  }

}

# Create Dynamic Group
resource "oci_identity_dynamic_group" "queue_nosql_dynamic_group" {
  compartment_id = var.tenancy_ocid
  name           = "QueueNoSQLContainerDynamicGroup"
  description    = "Dynamic group for Container Instances polling OCI Queue and inserting into NoSQL table"
  matching_rule  = "ALL {resource.type = 'computecontainerinstance', resource.compartment.id = '${var.compartment_ocid}'}"
}

resource "oci_identity_dynamic_group" "apigw_dynamic_group" {
  compartment_id = var.tenancy_ocid
  description    = "Dynamic group containing all API Gateways in compartment ${var.compartment_ocid}"
  matching_rule  = "ALL {resource.type = 'ApiGateway', resource.compartment.id = '${var.compartment_ocid}'}"
  name           = "apigw_dynamic_group"
}

# Create IAM Policy
resource "oci_identity_policy" "queue_nosql_policy" {
  compartment_id = var.compartment_ocid
  name           = "QueueNoSQLContainerPolicy"
  description    = "Policy for Container Instances to access Queue and NoSQL"
  statements = [
    "allow dynamic-group QueueNoSQLContainerDynamicGroup to use queues in compartment id ${var.compartment_ocid}",
    "allow dynamic-group QueueNoSQLContainerDynamicGroup to read queues in compartment id ${var.compartment_ocid}",
    "allow dynamic-group QueueNoSQLContainerDynamicGroup to use nosql-family in compartment id ${var.compartment_ocid}",
    "allow dynamic-group QueueNoSQLContainerDynamicGroup to read repos in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group apigw_dynamic_group to use functions-family in compartment id ${var.compartment_ocid}"
  ]
}
