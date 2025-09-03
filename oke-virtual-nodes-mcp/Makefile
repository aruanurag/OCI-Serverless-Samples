# Makefile for OKE Deployment

TF_VAR_FILE     ?= "terraform.tfvars"
DOCKER_USER     ?= ""
#DOCKER_PASS     ?= "" # export DOCKER_PASS=<password>
DOCKER_EMAIL    ?= "abc@abc.com"
REGION          ?= "us-ashburn-1"
KUBECONFIG_PATH ?= "$(HOME)/.kube/config"
K8S_NAMESPACE   ?= "mcp"
MANIFEST_FILE   ?= "$(CURDIR)/mcp-server/k8s/manifest.yaml"
# OCI Variables for terraform.tfvars
TENANCY_OCID       ?= "ocid1.tenancy.oc1..aaaaaaaa3ocohl2rfeixo3ikcbfeq4iveaysj5dfv2uo3kgnidowlifw6aiq"
COMPARTMENT_OCID   ?= "ocid1.tenancy.oc1..aaaaaaaa3ocohl2rfeixo3ikcbfeq4iveaysj5dfv2uo3kgnidowlifw6aiq"
NOTIFICATION_EMAIL ?= "email@example.com"
IMAGE_VERSION   ?= "0.0.1"
SED_INPLACE = sed -i'' -e



# PHONY TARGETS
# ------------------------------------------------------------------------------
# .PHONY ensures that make will not confuse these targets with actual files.
.PHONY: all plan apply kubeconfig create-secret build-push deploy destroy clean update-tfvars update-manifest

# MAIN TARGET
# ------------------------------------------------------------------------------
# This is the default target that runs when you just type 'make'.
all: update-tfvars init plan apply update-manifest

# TFVARS TARGET
# ------------------------------------------------------------------------------
# Populates the terraform.tfvars file with required values from Makefile variables.
update-tfvars:
	@echo "INFO: Updating $(TF_VAR_FILE) file..."
	@echo "tenancy_ocid       = \"$(TENANCY_OCID)\"" > $(TF_VAR_FILE)
	@echo "compartment_id   = \"$(COMPARTMENT_OCID)\"" >> $(TF_VAR_FILE)
	@echo "region             = \"$(REGION)\"" >> $(TF_VAR_FILE)
	@echo "notification_email = \"$(NOTIFICATION_EMAIL)\"" >> $(TF_VAR_FILE)


# TERRAFORM TARGETS
# ------------------------------------------------------------------------------
# Initializes and validates the terraform configuration.
init:
	@echo "INFO: Initializing Terraform..."
	terraform init

# Shows the execution plan for terraform.
plan: init update-tfvars
	@echo "INFO: Planning Terraform infrastructure changes..."
	terraform plan -var-file=$(TF_VAR_FILE)

# Applies the terraform configuration to build infrastructure.
apply: init update-tfvars
	@echo "INFO: Applying Terraform configuration..."
	terraform apply -var-file=$(TF_VAR_FILE) -auto-approve


# MANIFEST UPDATE TARGET
# ------------------------------------------------------------------------------
# Updates the manifest.yaml file with Compartment_OCID from variable and Notification_Topic_OCID, mcp-server-image-tag from Terraform outputs.
update-manifest: apply
	@echo "INFO: Updating $(MANIFEST_FILE) with required values..."
	@NOTIFICATION_TOPIC_OCID=$$(terraform output -raw notification_topic_ocid) && \
	MCP_SERVER_IMAGE_PATH=$$(terraform output -raw mcp_server_repository_path) && \
	MCP_SERVER_IMAGE_TAG=$${MCP_SERVER_IMAGE_PATH}:$(IMAGE_VERSION) && \
	$(SED_INPLACE) 's|<Compartment_OCID>|$(COMPARTMENT_OCID)|g' $(MANIFEST_FILE) && \
	$(SED_INPLACE) "s|<Notification_Topic_OCID>|$${NOTIFICATION_TOPIC_OCID}|g" $(MANIFEST_FILE) && \
	$(SED_INPLACE) "s|<mcp-server-image-tag>|$${MCP_SERVER_IMAGE_TAG}|g" $(MANIFEST_FILE)



#setting up Cluster Credentials
kubectl: 
	@echo "INFO: Generating kubeconfig for cluster $(CLUSTER_ID)..."
	cluster_id=$$(terraform output -raw cluster_id) && \
	oci ce cluster create-kubeconfig \
	--cluster-id $${cluster_id} \
	--file $(KUBECONFIG_PATH) \
	--region $(REGION) \
	--token-version 2.0.0 \
	--kube-endpoint PUBLIC_ENDPOINT


create-namespace: kubectl
	@echo "INFO: Ensuring namespace (K8S NAMESPACE)exists..."
	kubectl --kubeconfig $(KUBECONFIG_PATH) create ns mcp

create-docker-credentials: 
	@echo "INFO: Creating Docker credentials for mcp namespace..."
	kubectl --kubeconfig $(KUBECONFIG_PATH) create secret docker-registry ocirsecret \
	--docker-server=iad.ocir.io \
	--docker-username=$(DOCKER_USER) \
	--docker-password='$(DOCKER_PASS)' \
	--docker-email=$(DOCKER_EMAIL) \
	--namespace mcp

docker-build: kubectl
	@echo "INFO: Building Docker image..."	
	MCP_SERVER_IMAGE_PATH=$$(terraform output -raw mcp_server_repository_path) && \
	docker build --platform linux/amd64 -t $${MCP_SERVER_IMAGE_PATH}:$(IMAGE_VERSION) mcp-server/

docker-push: docker-build
	@echo "INFO: Pushing Docker image to registry..."
	@echo $(DOCKER_PASS) | docker login --username $(DOCKER_USER) --password-stdin iad.ocir.io
	MCP_SERVER_IMAGE_PATH=$$(terraform output -raw mcp_server_repository_path) && \
	docker push $${MCP_SERVER_IMAGE_PATH}:$(IMAGE_VERSION)

deploy:
	kubectl --kubeconfig $(KUBECONFIG_PATH) apply -f $(MANIFEST_FILE)

destroy-manifest: 
	kubectl --kubeconfig $(KUBECONFIG_PATH) delete -f $(MANIFEST_FILE)


# Destroys the terraform configuration to build infrastructure.
destroy-terraform: 
	@echo "INFO: Destroying Terraform configuration..."
	terraform destroy -var-file=$(TF_VAR_FILE) -auto-approve
	