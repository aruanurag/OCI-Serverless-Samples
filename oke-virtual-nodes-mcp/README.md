# MCP Server on OCI OKE Virtual Nodes

## 📌 What is this project about
This project demonstrates how to run an **MCP server** on **serverless compute**, specifically using **OCI OKE Virtual Nodes**.  

- The server runs an MCP service that exposes **one tool**, which leverages the **OCI Language Service**.  
- Currently, no additional security is built in (to be added in future steps).  
- The MCP server provides access to the tool for an MCP client, which can then consume it.  

Right now, the tool performs **sentiment analysis** using the OCI Language Service.

---

## ✅ Prerequisites
Before you begin, ensure you have the following installed:

- **Terraform v1.10.x**  
- **Docker** (or another container engine)  
- **Python 3.x** (required for the MCP client)  
- **kubectl** configured for your OCI tenancy  

---

## 🚀 How to Use

### Step 1: Update Terraform Variables
1. Navigate to the `terraform/` folder.  
2. Open the `terraform.tfvars` file.  
3. Fill in the required values:
   - `tenancy_ocid`
   - `compartment_ocid`
   - `region`
   - `vcn_id`
   - `control_plane_subnet_id`
   - `load_balancer_subnet_id`
   - `virtual_node_subnet_id`

---

### Step 2: Provision Infrastructure
Run the following:

```bash
cd okvirtualnodes.mcp
terraform init
terraform plan
terraform apply
```

This will create:
- An OKE cluster
- A Language Service endpoint
- Virtual networks
- A Container repository

👉 Copy the name of the container repository created.

### Step 3: Build and Push the MCP Server Image
Navigate to the `mcpsentiment/` directory.

Build the Docker image and tag it with your repo name:

```bash
docker build -t <region-key>.ocir.io/<tenancy-namespace>/<repo-name>:v1 .
```

Push it to your repo:

```bash
docker push <region-key>.ocir.io/<tenancy-namespace>/<repo-name>:v1
```

### Step 4: Configure OKE to Pull from OCIR
Create a Docker registry secret in your cluster:

```bash
kubectl create secret docker-registry ocirsecret \
  --docker-server=<region-key>.ocir.io \
  --docker-username='<tenancy-namespace>/<username>' \
  --docker-password='<auth-token>' \
  --docker-email='<email>'
```

This secret allows your OKE pods to authenticate and pull images from your private OCIR repository.

### Step 5: Deploy MCP Server on OKE
Navigate to the `k8s/` folder.

Open the manifest file (`manifest.yaml`) and update the image name with your repo and tag.

Apply the manifest:

```bash
kubectl apply -f manifest.yaml
```

Wait for the Load Balancer service to be provisioned.  
👉 Copy the public IP once available.

### Step 6: Run the MCP Client
Navigate to the `mcp-client/` directory.

Open `agent-client.py` and update the URL with the public IP of your MCP server.

Run the client:

```bash
python agent-client.py
```

You’ll get a URL with a UI where you can interact with the MCP agent.

---

## 🎯 What can you do now?
Right now, the agent supports **sentiment analysis**.  
Try entering any sentence, and it will return the sentiment classification using OCI Language Service.

---

## 🔮 Next Steps
- Add authentication & security
- Add more tools to the MCP server
- Enable autoscaling for OKE workloads

