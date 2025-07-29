output "api_gateway_url" {
  description = "The URL of the API Gateway"
  value       = module.apigateway.gateway_url
}

output "queue_id" {
  description = "The OCID of the queue"
  value       = module.apigw_function_queue.queue_id
}

output "queue_url" {
  description = "The URL of the queue"
  value       = module.apigw_function_queue.queue_url
}

output "function_application_id" {
  description = "The OCID of the function application"
  value       = module.apigw_function_queue.application_id
}

output "container_repository_id" {
  description = "The OCID of the container repository"
  value       = module.apigw_function_queue.container_repository_id
} 