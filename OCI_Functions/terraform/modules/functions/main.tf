
resource "oci_functions_function" "fn" {
  display_name   = var.function_name
  application_id = var.application_id
  image          = var.source_image
  memory_in_mbs  = 128
  config = {
    "COMPARTMENT_ID"   = var.compartment_id
    "OCI_REGION"       = var.region
    "NOSQL_TABLE_NAME" = var.nosql_table_name
  }
} 