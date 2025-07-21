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
  source         = "./modules/apigateway"
  compartment_id = var.compartment_ocid
  subnet_id      = var.subnet_ocid
}

module "nosql" {
  source           = "./modules/nosql"
  compartment_id   = var.compartment_ocid
  nosql_table_name = var.nosql_table_name
}

resource "oci_functions_application" "customer_info_app" {
    compartment_id = var.compartment_ocid
    display_name = var.application_display_name
    subnet_ids = [var.subnet_ocid]
    shape = "GENERIC_ARM"
}

resource "oci_functions_function" "my_functions" {
  # Iterates over the var.functions map and includes only those
  # items 'f' where the source_image attribute is not null.
  for_each = {
    for name, f in var.functions : name => f if f.source_image != null
  }

  display_name = each.key # Use the map key as the function name  
  application_id = oci_functions_application.customer_info_app.id
  image = each.value.source_image
  memory_in_mbs      = 128
  config = {
     "COMPARTMENT_ID" = var.compartment_ocid,
     "OCI_REGION" = var.region,
     "NOSQL_TABLE_NAME" = var.nosql_table_name
  }
}

resource "oci_identity_policy" "function_nosql_policy" {
    compartment_id = var.compartment_ocid
    description = "Allows function applications to use NoSQL tables"
    name = "function_nosql_access"
    statements = [
      "Allow dynamic-group function_dynamic_group to manage nosql-family in compartment id ${var.compartment_ocid}"
    ]
}

resource "oci_identity_dynamic_group" "function_dynamic_group" {
    compartment_id = var.tenancy_ocid
    description = "Dynamic group containing all functions in compartment ${var.compartment_ocid}"
    matching_rule = "ALL {resource.type = 'fnfunc', resource.compartment.id = '${var.compartment_ocid}'}"
    name = "function_dynamic_group"
}

module "container_repository" {
  source                    = "./modules/container_repository"
  compartment_id            = var.compartment_ocid
  container_repository_name = var.container_repository_name
} 