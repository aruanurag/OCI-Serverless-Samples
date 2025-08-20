variable "region" {
  description = "The OCI region identifier, e.g., 'us-ashburn-1'."
  type        = string
}

variable "compartment_id" {
  description = "The OCID of the compartment where the VCN will be created."
  type        = string
}

variable "vcn_name" {
  description = "The name for the VCN."
  type        = string
  default     = "sample_vcn"
}

variable "vcn_cidr" {
  description = "The CIDR block for the VCN."
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnets" {
  description = "A map of subnets to create. Key is the subnet name."
  type = map(object({
    cidr_block          = string
    is_public           = bool
    dns_label           = string
    use_service_gateway = optional(bool, false)
  }))
  default = {}
}

variable "create_internet_gateway" {
  description = "Set to true to create an internet Gateway for public subnets."
  type        = bool
  default     = true
}

variable "create_nat_gateway" {
  description = "Set to true to create a NAT Gateway for private subnets."
  type        = bool
  default     = false
}

variable "create_service_gateway" {
  description = "Set to true to create a service Gateway."
  type        = bool
  default     = false
}

variable "vcn_dns_label" {
  description = "The DNS label for the VCN."
  type        = string
  default     = "modvcn"
}