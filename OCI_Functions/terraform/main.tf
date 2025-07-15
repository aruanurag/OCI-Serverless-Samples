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

module "container_repository" {
  source                    = "./modules/container_repository"
  compartment_id            = var.compartment_ocid
  container_repository_name = var.container_repository_name
} 