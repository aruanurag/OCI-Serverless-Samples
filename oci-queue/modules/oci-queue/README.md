# OCI Queue Terraform Module

A reusable Terraform module for provisioning Oracle Cloud Infrastructure (OCI) Queue services.

## Overview

This module simplifies the creation and configuration of OCI Queue resources with support for:
- Main queue configuration
- Dead Letter Queue (DLQ) support
- Custom retention and visibility settings
- Resource tagging (freeform and defined tags)
- Comprehensive output values

## Features

- ✅ Create OCI Queue with customizable parameters
- ✅ Optional Dead Letter Queue creation
- ✅ Configurable retention and visibility timeouts
- ✅ Support for delivery attempt thresholds
- ✅ Freeform and defined tags support
- ✅ Comprehensive validation on all inputs
- ✅ Outputs for queue endpoints and metadata

## Usage

### Basic Queue

```hcl
module "oci_queue" {
  source = "./modules/oci-queue"

  compartment_id      = var.compartment_id
  queue_display_name  = "my-queue"
}
```

### Queue with Dead Letter Queue

```hcl
module "oci_queue" {
  source = "./modules/oci-queue"

  compartment_id                      = var.compartment_id
  queue_display_name                  = "my-queue"
  create_dead_letter_queue            = true
  dead_letter_queue_delivery_attempts = 5
  retention_in_seconds                = 1209600  # 14 days
  visibility_in_seconds               = 30
  timeout_in_seconds                  = 30

  freeform_tags = {
    Environment = "production"
    Team        = "platform"
  }
}
```

## Variables

### Required

- `compartment_id` - The OCID of the compartment where the queue will be created
- `queue_display_name` - Display name for the OCI Queue (1-128 characters)

### Optional

- `retention_in_seconds` - Queue retention period in seconds (60-1209600, default: 1209600/14 days)
- `visibility_in_seconds` - Message visibility timeout (0-43200, default: 30)
- `timeout_in_seconds` - Message receive timeout (0-120, default: 30)
- `dead_letter_queue_delivery_attempts` - Attempts before DLQ (1-100, default: 5)
- `create_dead_letter_queue` - Create dedicated DLQ (default: false)
- `dlq_retention_in_seconds` - DLQ retention period (60-1209600, default: 1209600)
- `freeform_tags` - Freeform tags (default: {})
- `defined_tags` - Defined tags (default: {})

## Outputs

- `queue_id` - OCID of the created queue
- `queue_display_name` - Display name of the queue
- `queue_messages_endpoint` - Endpoint for sending/receiving messages
- `queue_state` - Current lifecycle state
- `queue_retention_in_seconds` - Configured retention period
- `queue_visibility_in_seconds` - Configured visibility timeout
- `dead_letter_queue_id` - OCID of the DLQ (if created)
- `dead_letter_queue_endpoint` - Endpoint of the DLQ (if created)

## Requirements

- Terraform >= 1.0
- OCI Provider >= 5.0
- Valid OCI credentials configured

## License

This module is part of the OCI Serverless Samples project.
