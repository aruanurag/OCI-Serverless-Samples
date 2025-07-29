# API Gateway Function Queue Async

This project demonstrates an asynchronous messaging pattern using Oracle Cloud Infrastructure (OCI) services:

- **API Gateway**: Receives HTTP requests and routes them to functions
- **OCI Functions**: Serverless functions for processing requests
- **OCI Queue**: Asynchronous message queue for decoupling services

## Architecture

```
HTTP Request → API Gateway → Function → Queue → Processing Function → Database
```

## Components

### API Gateway
- Receives HTTP requests at `/order` endpoint
- Routes requests to the `place-order` function
- Handles authentication and rate limiting

### Functions
- **place-order**: Receives order requests and sends them to the queue
- **process-order**: Reads from queue and processes orders

### Queue
- **OrderQueue**: Asynchronous message queue for order processing
- Provides reliable message delivery and processing

## Directory Structure

```
api-gateway-function-queue-async/
├── terraform/           # Infrastructure as Code
│   ├── main.tf         # Main Terraform configuration
│   ├── variables.tf    # Variable definitions
│   ├── outputs.tf      # Output values
│   └── modules/        # Reusable Terraform modules
│       ├── apigateway/     # API Gateway module
│       ├── functions/      # OCI Functions module
│       ├── queue/          # OCI Queue module
│       └── container_repository/ # Container registry module
└── functions/          # Go function code
    ├── place-order/    # Function to place orders
    └── process-order/  # Function to process orders
```

## Getting Started

1. **Deploy Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

2. **Build and Deploy Functions**:
   ```bash
   # Build function images
   docker build -t place-order functions/place-order/
   docker build -t process-order functions/process-order/
   
   # Push to OCI Container Registry
   docker tag place-order <region>.ocir.io/<namespace>/place-order:latest
   docker tag process-order <region>.ocir.io/<namespace>/process-order:latest
   docker push <region>.ocir.io/<namespace>/place-order:latest
   docker push <region>.ocir.io/<namespace>/process-order:latest
   ```

3. **Test the API**:
   ```bash
   curl -X POST https://<api-gateway-url>/order \
     -H "Content-Type: application/json" \
     -d '{"order_id": "123", "customer_id": "456", "amount": 99.99}'
   ```

## Configuration

Update `terraform/variables.tf` with your OCI configuration:
- `compartment_ocid`: Your OCI compartment OCID
- `subnet_ocid`: Your subnet OCID
- `region`: Your OCI region
- `tenancy_ocid`: Your tenancy OCID

## Benefits

- **Scalability**: Queue decouples request handling from processing
- **Reliability**: Messages are persisted and can be retried
- **Performance**: API responds immediately while processing happens asynchronously
- **Monitoring**: Queue provides visibility into message processing 