# OCI Queue Terraform Configuration

region                              = "us-phoenix-1"
compartment_id                      = "ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
queue_display_name                  = "serverless-queue"
retention_in_seconds                = 1209600
visibility_in_seconds               = 30
timeout_in_seconds                  = 30
create_dead_letter_queue            = true
dlq_retention_in_seconds            = 1209600
environment                         = "dev"

freeform_tags = {
  Project     = "OCI-Serverless-Samples"
  Owner       = "Platform-Team"
  CostCenter  = "Engineering"
}

defined_tags = {
  # Example: "department.cost-center" = "engineering.12345"
}
