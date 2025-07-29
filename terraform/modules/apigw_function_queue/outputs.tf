output "queue_id" {
  description = "The OCID of the queue"
  value       = module.queue.queue_id
}

output "queue_url" {
  description = "The URL of the queue"
  value       = module.queue.queue_url
}

output "application_id" {
  description = "The OCID of the function application"
  value       = oci_functions_application.queue_async_app.id
}

output "container_repository_id" {
  description = "The OCID of the container repository"
  value       = module.container_repository.container_repository_id
} 