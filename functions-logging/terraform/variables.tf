# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

variable "tenancy_ocid" {
    default = "<your tenancy ocid>"
}
variable "user_ocid" {
    default = "<your user ocid>"
}
variable "fingerprint" {
    default = "<user fingerprint>"
}
variable "private_key_path" {
    default = "<user ssh key>"
}
variable "region" {
    default = "<region example: us-ashburn-1>"
}
variable "compartment_ocid" {
    default = "<compartment to host functions and logs>"
}
variable "subnet_id" {
    default = "<subnet id for the function app>"
}
variable "memory_in_mbs" {
    default = "<example:256>"
}
variable "timeout_in_seconds" {
    default = "<example:30>"
}