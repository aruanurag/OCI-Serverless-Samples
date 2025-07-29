module "queue" {
  source         = "../queue"
  compartment_id = var.compartment_ocid
  queue_name     = var.queue_name
}

resource "oci_functions_application" "queue_async_app" {
  compartment_id = var.compartment_ocid
  display_name   = var.application_display_name
  subnet_ids     = [var.subnet_ocid]
  shape          = "GENERIC_ARM"
}

module "functions" {
  source            = "../functions"
  for_each          = { for name, f in var.functions : name => f if f.source_image != null }
  function_name     = each.key
  application_id    = oci_functions_application.queue_async_app.id  
  path              = each.value.path
  source_image      = each.value.source_image
  compartment_id    = var.compartment_ocid
  region            = var.region
  apigw_id          = var.apigw_id
  queue_url         = module.queue.queue_url
}

resource "oci_identity_policy" "function_queue_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to use queues"
  name           = "function_queue_access"
  statements     = [
    "Allow dynamic-group function_dynamic_group to manage queue-family in compartment id ${var.compartment_ocid}"
  ]
}

resource "oci_identity_dynamic_group" "function_dynamic_group" {
  compartment_id = var.tenancy_ocid
  description    = "Dynamic group containing all functions in compartment ${var.compartment_ocid}"
  matching_rule  = "ALL {resource.type = 'fnfunc', resource.compartment.id = '${var.compartment_ocid}'}"
  name           = "function_dynamic_group"
}

module "container_repository" {
  source                    = "../container_repository"
  compartment_id            = var.compartment_ocid
  container_repository_name = var.container_repository_name
} 