variable "tenancy_ocid" {}
variable "compartment_ocid" {}
variable "region" {}
variable "cluster_name" {
  default = "oke-virtual-cluster"
}
variable "kubernetes_version" {
  default = "v1.33.1"
}
variable "vcn_id" {}
variable "control_plane_subnet_id" {}
variable "load_balancer_subnet_id" {}
variable "virtual_nodes_subnet_id" {}
variable "pods_cidr" {
  default = "10.244.0.0/16"
}
variable "services_cidr" {
  default = "10.96.0.0/16"
}