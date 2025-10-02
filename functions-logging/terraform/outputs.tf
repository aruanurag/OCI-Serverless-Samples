# Outputs for Log Generator
output "log_generator_group_id" {
  description = "OCID of the log generator group"
  value       = oci_logging_log_group.log_generator_group.id
}

output "log_generator_log_id" {
  description = "OCID of the log generator custom log"
  value       = oci_logging_log.log_generator_log.id
}

output "log_generator_repo_id" {
  description = "OCID of the log generator container repository"
  value       = oci_artifacts_container_repository.log_generator_repo.id
}

output "log_generator_repo_name" {
  description = "Name of the log generator container repository"
  value       = oci_artifacts_container_repository.log_generator_repo.display_name
}

output "log_generator_func_app_id" {
  description = "OCID of the log generator function app"
  value       = oci_functions_application.log_app.id
}

output "log_generator_func_app_name" {
  description = "Name of the log generator function app"
  value       = oci_functions_application.log_app.display_name
}