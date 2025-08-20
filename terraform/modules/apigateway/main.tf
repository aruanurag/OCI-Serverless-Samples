resource "oci_apigateway_gateway" "main" {
  compartment_id = var.compartment_id
  display_name   = "main-gateway"
  endpoint_type  = "PUBLIC"
  subnet_id      = var.subnet_id
}

output "gateway_id" {
  value = oci_apigateway_gateway.main.id
} 
