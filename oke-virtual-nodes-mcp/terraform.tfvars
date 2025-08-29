# terraform.tfvars

tenancy_ocid                  = "ocid1.tenancy.oc1..your_tenancy_ocid"
compartment_id                = "ocid1.compartment.oc1..your_compartment_ocid"
region                        = "us-ashburn-1" # Or your desired region
cluster_name                  = "my-oke-cluster"
kubernetes_version            = "v1.33.1"
mcp_container_repository_name = "mcp-sentiment-tool-repo"
notification_email            = "" # email address for notification
