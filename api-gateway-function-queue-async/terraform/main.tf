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
      config       = merge(fn.config, {
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

resource "oci_functions_application" "queue_async_app" {
  compartment_id = var.compartment_ocid
  display_name   = var.application_display_name
  subnet_ids     = [var.subnet_ocid]
  shape          = "GENERIC_ARM"
}

module "place_order_function" {
  source            = "../../terraform/modules/functions"
  count             = local.function_configs["place-order"].source_image != null ? 1 : 0
  function_name     = "place-order"
  application_id    = oci_functions_application.queue_async_app.id
  path              = local.function_configs["place-order"].path
  source_image      = local.function_configs["place-order"].source_image
  compartment_id    = var.compartment_ocid
  region            = var.region
  apigw_id          = module.apigateway.gateway_id
  function_config   = local.function_configs["place-order"].config
}

# module "process_order_function" {
#   source            = "../../terraform/modules/functions"
#   count             = var.functions["process-order"].source_image != null ? 1 : 0
#   function_name     = "process-order"
#   application_id    = oci_functions_application.customer_info_app.id
#   path              = var.functions["process-order"].path
#   source_image      = var.functions["process-order"].source_image
#   compartment_id    = var.compartment_ocid
#   region            = var.region
#   apigw_id          = module.apigateway.gateway_id
#   function_config   = var.functions["process-order"].config
# }

resource "oci_identity_policy" "function_queue_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to use queues"
  name           = "function_queue_access"
  statements     = [
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
  container_repository_name = var.container_repository_name
} 