terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "= 7.11.0"
    }
  }
}

provider "oci" {
  tenancy_ocid        = var.tenancy_ocid
  user_ocid           = var.user_ocid
  fingerprint         = var.fingerprint
  private_key_path    = var.private_key_path
  region              = var.region
}

resource "oci_functions_application" "log_app" {
  compartment_id = var.compartment_ocid
  display_name   = "LogGenApp"
  subnet_ids     = [var.subnet_id]
  shape          = "GENERIC_ARM"
}

resource "oci_logging_log_group" "log_generator_group" {
  compartment_id = var.compartment_ocid
  display_name   = "log-generator-group"
  description    = "Log group for synthetic log generator function"
}

resource "oci_logging_log" "log_generator_log" {
  display_name   = "log-generator-custom-log"
  log_group_id   = oci_logging_log_group.log_generator_group.id
  log_type       = "CUSTOM"
  is_enabled     = true
  retention_duration = 30
}

# Container Registry Repository for Log Generator
resource "oci_artifacts_container_repository" "log_generator_repo" {
  compartment_id = var.compartment_ocid
  display_name   = "log-generator-repo"
  is_immutable   = false
  is_public      = false
}

# Dynamic Group for Functions
resource "oci_identity_dynamic_group" "function_dynamic_group" {
  compartment_id = var.tenancy_ocid
  description    = "Dynamic group containing all functions in compartment ${var.compartment_ocid}"
  matching_rule  = "ALL {resource.type = 'fnfunc', resource.compartment.id = '${var.compartment_ocid}'}"
  name           = "function_dynamic_group"
}

# IAM Policy for Function to access Container Registry
resource "oci_identity_policy" "function_registry_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to access Container Registry"
  name           = "function_registry_access"
  statements     = [
    "Allow dynamic-group function_dynamic_group to read repos in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group function_dynamic_group to manage repos in compartment id ${var.compartment_ocid}"
  ]
}

# IAM Policy for Function to access Logging Service
resource "oci_identity_policy" "function_logging_policy" {
  compartment_id = var.compartment_ocid
  description    = "Allows function applications to write to Logging Service"
  name           = "function_logging_access"
  statements     = [
    "Allow dynamic-group function_dynamic_group to manage log-groups in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group function_dynamic_group to manage log-content in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group function_dynamic_group to use log-content in compartment id ${var.compartment_ocid}"
  ]
}

  