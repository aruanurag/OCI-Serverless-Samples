# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

# terraform.tfvars

tenancy_ocid                  = "ocid1.tenancy.oc1..your_tenancy_ocid"
compartment_id                = "ocid1.compartment.oc1..your_compartment_ocid"
region                        = "us-ashburn-1" # Or your desired region
cluster_name                  = "my-oke-cluster"
kubernetes_version            = "v1.33.1"
mcp_container_repository_name = "mcp-sentiment-tool-repo"
notification_email            = "" # email address for notification
