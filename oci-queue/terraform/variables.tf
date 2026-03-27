variable "region" {
  description = "OCI region"
  type        = string
  default     = "us-phoenix-1"
}

variable "compartment_id" {
  description = "The OCID of the compartment where resources will be created"
  type        = string
}

variable "queue_display_name" {
  description = "Display name for the OCI Queue"
  type        = string
  default     = "serverless-queue"
}

variable "retention_in_seconds" {
  description = "The retention period of the queue in seconds"
  type        = number
  default     = 1209600 # 14 days
}

variable "visibility_in_seconds" {
  description = "The visibility timeout of messages in the queue in seconds"
  type        = number
  default     = 30
}

variable "timeout_in_seconds" {
  description = "The timeout for receiving messages from the queue in seconds"
  type        = number
  default     = 30
}

variable "dead_letter_queue_delivery_attempts" {
  description = "Number of delivery attempts before moving to dead letter queue"
  type        = number
  default     = 5
}

variable "create_dead_letter_queue" {
  description = "Whether to create a dedicated dead letter queue"
  type        = bool
  default     = true
}

variable "dlq_retention_in_seconds" {
  description = "The retention period for the dead letter queue in seconds"
  type        = number
  default     = 1209600 # 14 days
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "freeform_tags" {
  description = "Freeform tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "defined_tags" {
  description = "Defined tags to apply to resources"
  type        = map(map(string))
  default     = {}
}
