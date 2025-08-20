resource "oci_functions_function" "fn" {
  display_name   = var.function_name
  application_id = var.application_id
  image          = var.source_image
  memory_in_mbs  = 128
  config         = var.function_config
}

resource "oci_apigateway_deployment" "customer_info" {
  compartment_id = var.compartment_id
  gateway_id     = var.apigw_id
  display_name   = var.function_name
  path_prefix    = "/api"

  specification {
    routes {
      path    = var.path
      methods = ["GET", "POST"]
      backend {
        type        = "ORACLE_FUNCTIONS_BACKEND"
        function_id = oci_functions_function.fn.id
      }
    }
  }
} 
