# OCI Queue Sample

This sample demonstrates how to provision an Oracle Cloud Infrastructure (OCI) Queue using Terraform. OCI Queue is a fully managed, serverless message queue service for asynchronous workloads.

## Overview

The sample includes:
- **Reusable Terraform Module**: Located in `modules/oci-queue/` for provisioning OCI Queue resources
- **Terraform Configuration**: Located in `terraform/` directory ready to deploy

## Directory Structure

```
oci-queue/
├── README.md                    # This file
├── modules/
│   └── oci-queue/              # Reusable module
│       ├── main.tf             # Resource definitions
│       ├── variables.tf         # Input variables
│       ├── outputs.tf           # Output values
│       └── README.md            # Module documentation
└── terraform/
    ├── provider.tf              # Provider configuration
    ├── main.tf                  # Module instantiation
    ├── variables.tf             # Variable definitions
    ├── outputs.tf               # Output definitions
    └── terraform.tfvars         # Terraform variables (update with your values)
```

## Features

- ✅ Create OCI Queue with customizable retention, visibility, and timeout settings
- ✅ Optional Dead Letter Queue (DLQ) support for failed messages
- ✅ Comprehensive input validation
- ✅ Support for both freeform and defined tags
- ✅ Complete outputs for queue endpoints and metadata
- ✅ Production-ready module structure

## Prerequisites

- Terraform >= 1.0
- OCI Provider >= 5.0
- OCI CLI configured with appropriate credentials
- A valid OCI compartment OCID

## Quick Start

### 1. Update Configuration

Edit `terraform/terraform.tfvars` with your OCI details:

```hcl
region            = "us-phoenix-1"  # Your OCI region
compartment_id    = "ocid1.compartment.oc1..xxxx"  # Your compartment OCID
queue_display_name = "my-serverless-queue"
environment       = "dev"
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Review Plan

```bash
terraform plan
```

### 4. Apply Configuration

```bash
terraform apply
```

### 5. Retrieve Outputs

```bash
terraform output
```

## Configuration Options

### Queue Parameters

- **retention_in_seconds**: How long messages are retained (60-1209600 seconds, default: 14 days)
- **visibility_in_seconds**: How long a message is hidden after being received (0-43200, default: 30)
- **timeout_in_seconds**: Receive timeout (0-120, default: 30)
- **dead_letter_queue_delivery_attempts**: Failed attempts before DLQ routing (1-100, default: 5)

### Dead Letter Queue

Enable by setting `create_dead_letter_queue = true` in `terraform.tfvars`:

```hcl
create_dead_letter_queue = true
dlq_retention_in_seconds = 1209600
```

## Module Outputs

The module provides the following outputs:

- `queue_id` - OCID of the created queue
- `queue_display_name` - Display name
- `queue_messages_endpoint` - Endpoint for message operations
- `queue_state` - Lifecycle state
- `dead_letter_queue_id` - DLQ OCID (if created)
- `dead_letter_queue_endpoint` - DLQ endpoint (if created)

## Using the Module

To use this module in your own Terraform configuration:

```hcl
module "my_queue" {
  source = "./modules/oci-queue"

  compartment_id      = "ocid1.compartment.oc1..xxxx"
  queue_display_name  = "my-queue"
  create_dead_letter_queue = true

  freeform_tags = {
    Environment = "production"
    Team        = "platform"
  }
}

output "queue_endpoint" {
  value = module.my_queue.queue_messages_endpoint
}
```

## Cleanup

To destroy resources created by Terraform:

```bash
cd terraform
terraform destroy
```

## Documentation

- [OCI Queue Documentation](https://docs.oracle.com/en-us/iaas/Content/queue/home.htm)
- [OCI Terraform Provider](https://registry.terraform.io/providers/oracle/oci/latest/docs)
- [Module Documentation](./modules/oci-queue/README.md)

## Support

For issues or questions, refer to the main OCI Serverless Samples repository.

## License

This sample is part of the OCI Serverless Samples project.
