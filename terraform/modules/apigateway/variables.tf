# -----------------------------------------------------------------------------
# Copyright (c) 2025 Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl

# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS HEADER.
# -----------------------------------------------------------------------------

variable "compartment_id" {
  description = "The OCID of the compartment."
  type        = string
}

variable "subnet_id" {
  description = "The OCID of the subnet."
  type        = string
}
