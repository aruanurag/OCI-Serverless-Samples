// main.tf - Terraform configuration for OCI resources
terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "= 7.9.0"
    }
  }
}

provider "oci" {
  # Configure your provider here
 
}

# API Gateway
resource "oci_apigateway_gateway" "main" {
  compartment_id = var.compartment_ocid
  display_name   = "main-gateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = var.subnet_ocid
}

# # # API Deployment with routes to functions
# resource "oci_apigateway_deployment" "main" {
#   compartment_id = var.compartment_ocid
#   gateway_id     = oci_apigateway_gateway.main.id
#   display_name   = "main-deployment"
#   path_prefix    = "/api"

#   specification {
#     routes {
#       path   = "/customer"
#       methods = ["GET"]
#       backend {
#         type = "ORACLE_FUNCTIONS_BACKEND"
#         function_id = var.get_customer_function_ocid
#       }
#     }  
# }
# }

# output "api_gateway_endpoint" {
#   value = oci_apigateway_deployment.main.endpoint
# }
   

# OCI NoSQL Table for Customer Info
resource "oci_nosql_table" "customer_info" {
  compartment_id = var.compartment_ocid
  name           = var.nosql_table_name
  table_limits {
    max_read_units = 50
    max_write_units = 50
    max_storage_in_gbs = 1
  }
  ddl_statement = <<DDL
    CREATE TABLE ${var.nosql_table_name} (
      customerId STRING,
      name STRING,
      address STRING,
      email STRING,
      phone STRING,
      PRIMARY KEY (customerId)
    )
  DDL
}

output "nosql_table_id" {
  value = oci_nosql_table.customer_info.id
}

# # Dynamic Group for Functions
# resource "oci_identity_dynamic_group" "functions_group" {
#   compartment_id = var.compartment_ocid
#   name           = "functions-dynamic-group"
#   description    = "Dynamic group for function access to NoSQL"
#   matching_rule  = "Any {resource.id = '${var.get_customer_function_ocid}', resource.id = '${var.post_customer_function_ocid}', resource.id = '${var.place_order_function_ocid}'}"
# }

# # Policy to allow dynamic group to access NoSQL Table
# resource "oci_identity_policy" "functions_nosql_policy" {
#   compartment_id = var.compartment_ocid
#   name           = "functions-nosql-policy"
#   description    = "Allow functions to access NoSQL table"
#   statements     = [
#     "Allow dynamic-group ${oci_identity_dynamic_group.functions_group.name} to use nosql-tables in compartment id ${var.compartment_ocid}"
#   ]
# } 

resource "oci_artifacts_container_repository" "container_repo" {
  compartment_id = var.compartment_ocid
  display_name   = var.container_repository_name
  is_public      = false
} 