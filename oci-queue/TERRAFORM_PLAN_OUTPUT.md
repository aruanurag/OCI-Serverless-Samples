# Terraform Plan Output

## Example Plan Output

When you run `terraform plan` with valid OCI credentials, you will see output similar to:

```
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # module.oci_queue.oci_queue_queue.main will be created
  + resource "oci_queue_queue" "main" {
      + compartment_id           = "ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxx"
      + display_name             = "serverless-queue"
      + freeform_tags            = {
          + "CostCenter" = "Engineering"
          + "Environment" = "dev"
          + "ManagedBy"   = "Terraform"
          + "Owner"       = "Platform-Team"
          + "Project"     = "OCI-Serverless-Samples"
        }
      + id                       = (known after apply)
      + messages_endpoint        = (known after apply)
      + retention_in_seconds     = 1209600
      + state                    = (known after apply)
      + timeout_in_seconds       = 30
      + visibility_in_seconds    = 30
    }

  # module.oci_queue.oci_queue_queue.dead_letter_queue[0] will be created
  + resource "oci_queue_queue" "dead_letter_queue" {
      + compartment_id           = "ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxx"
      + display_name             = "serverless-queue-dlq"
      + freeform_tags            = {
          + "CostCenter" = "Engineering"
          + "Environment" = "dev"
          + "ManagedBy"   = "Terraform"
          + "Owner"       = "Platform-Team"
          + "Project"     = "OCI-Serverless-Samples"
          + "Purpose"     = "DeadLetterQueue"
        }
      + id                       = (known after apply)
      + messages_endpoint        = (known after apply)
      + retention_in_seconds     = 1209600
      + state                    = (known after apply)
      + timeout_in_seconds       = 30
      + visibility_in_seconds    = 30
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + dead_letter_queue_endpoint = (known after apply)
  + dead_letter_queue_id       = (known after apply)
  + queue_display_name         = "serverless-queue"
  + queue_id                   = (known after apply)
  + queue_messages_endpoint    = (known after apply)
  + queue_retention_in_seconds = 1209600
  + queue_state                = (known after apply)
  + queue_visibility_in_seconds = 30
```

## What Will Be Created

The plan shows that Terraform will create:

1. **Main OCI Queue** (`oci_queue_queue.main`)
   - Display Name: `serverless-queue`
   - Retention: 14 days (1209600 seconds)
   - Visibility Timeout: 30 seconds
   - Message Timeout: 30 seconds
   - Tags: Environment, Project, Owner, CostCenter, ManagedBy

2. **Dead Letter Queue** (`oci_queue_queue.dead_letter_queue`)
   - Display Name: `serverless-queue-dlq`
   - Same retention and timeout settings
   - Additional "Purpose" tag marking it as DLQ

## Outputs Generated

After `terraform apply`, you will receive:
- `queue_id` - OCID of the main queue
- `queue_display_name` - Display name ("serverless-queue")
- `queue_messages_endpoint` - API endpoint for message operations
- `queue_state` - Current state (ACTIVE)
- `queue_retention_in_seconds` - 1209600
- `queue_visibility_in_seconds` - 30
- `dead_letter_queue_id` - OCID of the DLQ
- `dead_letter_queue_endpoint` - API endpoint for DLQ operations

## To Run This Plan

1. Configure OCI credentials:
   ```bash
   oci config
   # or set OCI_CLI_* environment variables
   ```

2. Update `oci-queue/terraform/terraform.tfvars`:
   ```hcl
   region            = "us-phoenix-1"  # Your region
   compartment_id    = "ocid1.compartment.oc1..xxxxx"  # Your compartment
   queue_display_name = "serverless-queue"
   ```

3. Generate the plan:
   ```bash
   cd oci-queue/terraform
   terraform init
   terraform plan
   ```

4. Apply the plan:
   ```bash
   terraform apply
   ```

## Configuration Details

- **Terraform Version**: >= 1.0
- **OCI Provider Version**: >= 5.0
- **Environment**: dev (configurable)
- **Region**: us-phoenix-1 (configurable)
- **Resource Count**: 2 (main queue + DLQ)

## Cost Estimate

OCI Queue is a serverless, pay-as-you-go service. Costs depend on:
- Number of messages processed
- Standard pricing applies per million messages

See [OCI Queue Pricing](https://www.oracle.com/cloud/price-list/) for current rates.

## Notes

- The terraform configuration is validated and production-ready
- All resource IDs and endpoints will be populated after `terraform apply`
- The DLQ can be disabled by setting `create_dead_letter_queue = false`
- All resources are tagged for easy identification and cost tracking
