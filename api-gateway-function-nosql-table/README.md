# OCI Functions Project

This project contains:
- **Terraform code** for provisioning Oracle Cloud Infrastructure (OCI) resources.
- **Go code** for OCI Functions: GetCustomerInfo, PostCustomerInfo, and PlaceOrder.

## Structure
```
terraform/                # Terraform code for OCI resources
functions/
  customer/               # Go code for GET and POST Customer Info functions
  place-order/            # Go code for Place Order function
```

## Getting Started
1. **Terraform**: Edit files in `terraform/` and run `terraform init` and `terraform apply` to provision resources.
2. **Functions**: Edit Go code in each function directory. Deploy using OCI CLI or Fn Project CLI.

## Deploying Terraform Infrastructure

### Prerequisites
- [Terraform](https://www.terraform.io/downloads.html) installed
- [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliconfigure.htm) configured locally
- [Virtual Cloud Network](https://docs.oracle.com/en/solutions/wls-on-prem-to-oci/use-wizard-create-vcn.html) with a public subnet and port 443 allowed

### Steps
1. **Navigate to the Terraform directory:**
   ```sh
   cd terraform
   ```
2. **(Optional) Edit `terraform.tfvars`** to provide your actual OCIDs and configuration values.
3. **Initialize Terraform:**
   ```sh
   terraform init
   ```
4. **Apply the Terraform configuration:**
   ```sh
   terraform apply -var-file=terraform.tfvars
   ```
   Or, to skip interactive approval:
   ```sh
   terraform apply -var-file=terraform.tfvars --auto-approve
   ```

### Outputs
- The API Gateway endpoint and NoSQL table OCID will be displayed after a successful apply.
### Troubleshooting
- If you get authorization errors, ensure you have the correct IAM policies in OCI for API Gateway and NoSQL access.
- If you get DDL errors for NoSQL, check the DDL syntax in `main.tf`.

---
## Building and Deploying function images
### Prerequisites 
- [Docker](https://docs.docker.com/engine/install/) installed

### Steps
1. **Navigate to the functions directory:**
   ```sh
   cd functions
   ```
2. **Follow [these docs](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionslogintoocir.htm) to log in to the created registry with Docker.**
3. **Build the function image and tag it with the necessary information:**
   
   *Replace <repo_path> with the 'repository_path' value - which is output after running `terraform apply`*
   ```sh
   docker build -t <repo_path> customer/
   ```
4. **Push the image to the registry:**
   ```sh
   docker push <repo_path>
   ```
5. **Update the *source_image* parameter under the *functions* tf variable:**

   *Replace null with* `<repo_path>:latest` 

6. **After updating the function image value, re-run the terraform script:**
   ```sh
   terraform apply -var-file=terraform.tfvars --auto-approve
   ```
---

See each subdirectory for more details. 
