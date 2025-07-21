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

module "apigw_function_nosql" {
  source                    = "./modules/apigw_function_nosql"
  compartment_ocid          = var.compartment_ocid
  nosql_table_name          = var.nosql_table_name
  application_display_name  = var.application_display_name
  subnet_ocid               = var.subnet_ocid
  functions                 = var.functions
  region                    = var.region
  apigw_id                  = module.apigateway.gateway_id
  tenancy_ocid              = var.tenancy_ocid
  container_repository_name = var.container_repository_name
} 