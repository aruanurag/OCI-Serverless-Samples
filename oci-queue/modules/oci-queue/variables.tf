variable "compartment_id" {
  description = "The OCID of the compartment where the queue will be created"
  type        = string
}

variable "queue_display_name" {
  description = "Display name for the OCI Queue"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9-_.]{1,128}$", var.queue_display_name))
    error_message = "Queue display name must be 1-128 characters and contain only alphanumeric, dash, dot, and underscore characters."
  }
}

variable "retention_in_seconds" {
  description = "The retention period of the queue in seconds. Default is 1209600 (14 days)"
  type        = number
  default     = 1209600
  validation {
    condition     = var.retention_in_seconds >= 60 && var.retention_in_seconds <= 1209600
    error_message = "Retention period must be between 60 and 1209600 seconds."
  }
}

variable "visibility_in_seconds" {
  description = "The visibility timeout of messages in the queue in seconds. Default is 30 seconds"
  type        = number
  default     = 30
  validation {
    condition     = var.visibility_in_seconds >= 0 && var.visibility_in_seconds <= 43200
    error_message = "Visibility timeout must be between 0 and 43200 seconds."
  }
}

variable "timeout_in_seconds" {
  description = "The timeout for receiving messages from the queue in seconds. Default is 30 seconds"
  type        = number
  default     = 30
  validation {
    condition     = var.timeout_in_seconds >= 0 && var.timeout_in_seconds <= 120
    error_message = "Timeout must be between 0 and 120 seconds."
  }
}

variable "dead_letter_queue_delivery_attempts" {
  description = "The number of delivery attempts before a message is moved to dead letter queue. Default is 5"
  type        = number
  default     = 5
  validation {
    condition     = var.dead_letter_queue_delivery_attempts >= 1 && var.dead_letter_queue_delivery_attempts <= 100
    error_message = "Dead letter queue delivery attempts must be between 1 and 100."
  }
}

variable "create_dead_letter_queue" {
  description = "Whether to create a dedicated dead letter queue"
  type        = bool
  default     = false
}

variable "dlq_retention_in_seconds" {
  description = "The retention period for the dead letter queue in seconds. Default is 1209600 (14 days)"
  type        = number
  default     = 1209600
  validation {
    condition     = var.dlq_retention_in_seconds >= 60 && var.dlq_retention_in_seconds <= 1209600
    error_message = "DLQ retention period must be between 60 and 1209600 seconds."
  }
}

variable "freeform_tags" {
  description = "Freeform tags to apply to the queue"
  type        = map(string)
  default     = {}
}

variable "defined_tags" {
  description = "Defined tags to apply to the queue"
  type        = map(map(string))
  default     = {}
}
