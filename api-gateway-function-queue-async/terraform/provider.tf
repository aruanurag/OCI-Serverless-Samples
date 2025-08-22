terraform {
  required_version = ">= 1.10.0"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 7.14.0"
    }
  }
}

provider "oci" {}
