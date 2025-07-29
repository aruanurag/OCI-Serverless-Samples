terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "= 7.9.0"
    }
  }
}

provider "oci" {}

module "apigateway" {
  source         = "../../terraform/modules/apigateway"
  compartment_id = var.compartment_ocid
  subnet_id      = var.subnet_ocid
}

module "nosql" {
  source           = "../../terraform/modules/nosql"
  compartment_id   = var.compartment_ocid
  nosql_table_name = var.nosql_table_name
}

resource "oci_functions_application" "customer_info_app" {
  compartment_id = var.compartment_ocid
  display_name   = var.application_display_name
  subnet_ids     = [var.subnet_ocid]
  shape          = "GENERIC_ARM"
}

module "functions" {
  source            = "../../terraform/modules/functions"
  for_each          = { for name, f in var.functions : name => f if f.source_image != null }
  function_name     = each.key
  application_id    = oci_functions_application.customer_info_app.id  
  path              = each.value.path
  source_image      = each.value.source_image
  compartment_id    = var.compartment_ocid
  region            = var.region
  nosql_table_name  = var.nosql_table_name
  apigw_id          = module.apigateway.gateway_id
}

resource "oci_identity_policy" "function_nosql_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to use NoSQL tables"
  name           = "function_nosql_access"
  statements     = [
    "Allow dynamic-group function_dynamic_group to manage nosql-family in compartment id ${var.compartment_ocid}"
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

output "repository_url" {
  description = "The full URL for pushing images to the OCIR repository."
  value       = "${lower(data.oci_identity_regions.current.regions[0].key)}.ocir.io/${data.oci_objectstorage_namespace.this.namespace}/${var.container_repository_name}"
}