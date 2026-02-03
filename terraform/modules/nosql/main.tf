# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------


resource "oci_nosql_table" "customer_info" {
  compartment_id = var.compartment_id
  name           = var.nosql_table_name
  table_limits {
    max_read_units     = 50
    max_write_units    = 50
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
