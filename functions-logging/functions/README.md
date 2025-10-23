# Log Generator (OCI Function)

Small Oracle Cloud Infrastructure (OCI) Function that generates synthetic log messages and sends them to an OCI Logging Log (via Logging Ingestion).

This repository contains a Python function (`function/logen.py`) that can be deployed to OCI Functions (Fn Project runtime). It's useful for load testing, demoing log pipelines, or populating a logging destination with synthetic data.

## What it does

- Generates N random log messages of a configurable size.
- Sends the messages to an OCI Logging Log OCID using the Logging Ingestion API.
- Configurable via `config.json`, `config.ini`, or environment variables.

## Repository layout

- function/
  - `logen.py` — main function implementation
  - `func.yaml` — function metadata (runtime, entrypoint, memory)
  - `config.json` — example JSON config
  - `config.ini` — example INI config
  - `requirements.txt` — Python dependencies
- terraform/ — example Terraform to provision infrastructure (optional)

## Prerequisites

- Python 3.11-compatible runtime for local testing (optional).
- OCI tenancy with Logging service and a target Log created.
- If running as an OCI Function, the function must have a Resource Principal with permission to write to the target Log; the function uses Resource Principals for auth.
- The function uses the `oci` SDK and `fdk` (Fn Project) runtime packages — listed in `function/requirements.txt`.

## Configuration

Configuration can be provided in three ways (priority order):

1. A config file specified by the `CONFIG_FILE` environment variable (defaults to `config.json` in the function folder).
   - Supports JSON (`*.json`) or INI (`*.ini`) formats. If the extension is unknown the code will attempt JSON first then INI.
2. Environment variables (override file values):
   - `NUM_MESSAGES` — number of log messages to generate (integer). Default: 10.
   - `MESSAGE_SIZE` — size (in characters) of each generated message (integer). Default: 256.
   - `LOG_ID` — OCID of the target Logging Log to send messages to (string). No default — required.

Example JSON (`function/config.json`):

{
    "num_messages": 10000,
    "message_size": 512,
    "log_id": "ocid1.log.oc1..."
}

Example INI (`function/config.ini`):

[DEFAULT]
num_messages = 50
message_size = 512
log_id = <target log ocid>

Notes on validation enforced by the function:

- `log_id` is required and must be supplied either in the config file or via `LOG_ID` env var.
- `num_messages` must be an integer > 0 and is limited by code to a maximum of 100000 (to avoid accidental huge runs).
- `message_size` must be an integer > 0 and is limited to 100000 characters.

If any validation fails the function returns a 400 with an explanatory message.

## Running locally for quick tests

The function is written for the Fn Project / Oracle Functions runtime. For a quick local test you can run the handler directly (not through Fn):

1. Create a Python virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r function/requirements.txt
```

2. Set environment variables (example):

```bash
export NUM_MESSAGES=5
export MESSAGE_SIZE=64
export LOG_ID="ocid1.log.oc1.yourlogocid"
export CONFIG_FILE="function/config.json" # optional
```

3. Run a small shim to call the handler (example):

```python
# quick-run.py
from fdk import response
from function.logen import handler

# ctx may be a simple object; fdk.Response accepts a ctx param but for local invocation
# we can pass None for ctx and handle the response object.
resp = handler(None)
print(resp.data)

```

Or call the handler from an interactive Python session after setting env vars.

Warning: The function expects to authenticate to OCI via Resource Principals when deployed. Local runs will not have Resource Principals; the `oci` SDK may also support local configuration via API keys but the current code uses Resource Principals (get_resource_principals_signer()).

## Deploying as an OCI Function (Fn)

This function uses `func.yaml` and the Fn Project Python runtime. A minimal deployment flow:

1. Install and configure the Fn CLI and the OCI Functions service.
2. Build the function image and deploy it (examples using `fn`):

```bash
cd function
fn deploy --app <your-app-name>
```

3. Ensure the Function's IAM role (or Resource Principal policy) grants Logging ingestion permissions to the target Log. Example policy (replace tenancy/compartment/log OCIDs appropriately):

Allow dynamic-resource-principal to manage log-content in compartment <compartment_ocid>

4. Trigger the function via an HTTP request or the Fn invoke command:

```bash
fn invoke <app> log-gen -b '{}'
```

If deployment uses a different entrypoint or Python version, verify `func.yaml` matches the environment in `function/func.yaml`.

## Terraform

The `terraform/` folder contains example Terraform files to provision infrastructure. Review and adapt them to your tenancy/compartment before applying.

### What the Terraform provisions

- An OCI Functions Application (`oci_functions_application`) to host the function.
- A Logging Log Group and a Custom Log (`oci_logging_log_group`, `oci_logging_log`).
- An Artifacts Container Repository to store container images (`oci_artifacts_container_repository`).
- A Dynamic Group and IAM Policies that allow functions (dynamic group) to access the container repo and to write/manage logs.

### Required variables

The Terraform module expects the variables defined in `terraform/variables.tf`. At minimum you should provide:

- `tenancy_ocid` — your tenancy OCID
- `user_ocid` — the user OCID used for Terraform (if using API key auth)
- `fingerprint` — the API key fingerprint for the user
- `private_key_path` — path to your private key for API key auth
- `region` — OCI region (example: `us-ashburn-1`)
- `compartment_ocid` — compartment to host functions and logs
- `subnet_id` — subnet OCID where the function application will be created

You can provide these values with a `terraform.tfvars` file placed in the `terraform/` folder, or by exporting environment variables before running Terraform.

Example `terraform/terraform.tfvars`:

```hcl
tenancy_ocid     = "ocid1.tenancy.oc1..aaaa..."
user_ocid        = "ocid1.user.oc1..aaaa..."
fingerprint      = "12:34:56:78:9a:bc:de:ff"
private_key_path = "/home/you/.oci/oci_api_key.pem"
region           = "us-ashburn-1"
compartment_ocid = "ocid1.compartment.oc1..aaaa..."
subnet_id        = "ocid1.subnet.oc1..aaaa..."
```

### Initialize and apply

From the repository root:

```bash
cd terraform
terraform init
terraform plan -out plan.tfplan
terraform apply plan.tfplan
```

Terraform will create the resources and print outputs; see `terraform/outputs.tf` for the exported values.

### Useful outputs

- `log_generator_group_id` — OCID of the log group
- `log_generator_log_id` — OCID of the custom log (use this as `LOG_ID` in the function)
- `log_generator_repo_id` — container repository OCID (where to push images)
- `log_generator_repo_name` — container repository name
- `log_generator_func_app_id` — OCID of the Functions Application

Use `log_generator_log_id` as the `LOG_ID` configuration for the function so logs are ingested into the created custom log.

### IAM / Policy notes

The Terraform creates a dynamic group and two sample policies that:

- Allow the dynamic group to manage/read container repositories in the compartment (so functions can pull/push images if necessary).
- Allow the dynamic group to manage log-groups and log-content in the compartment (enables write access to the Logging service from functions).

Review the generated policies and tighten them according to your tenancy's security requirements. In production you may want to scope policies to specific resources rather than the whole compartment.

### Next steps after Terraform

1. Build and push the function image to the container repository (OCI Registry) created by Terraform. The `func deploy` flow will do this if configured to use the repo.
2. Deploy the function to the created Functions Application (via Fn CLI or CI/CD) and set `LOG_ID` to the `log_generator_log_id` output.

## Troubleshooting Terraform

- If `terraform apply` fails due to permissions, ensure the credentials you provided (user/API key) have the necessary IAM privileges to create the listed resources.
- If the dynamic group doesn't match deployed functions, double-check the `matching_rule` in `terraform/main.tf` and make sure the functions are created in the same compartment.


## Troubleshooting

- "Config file not found": The code falls back to defaults and environment variables; provide `CONFIG_FILE` or export the env vars.
- "Invalid JSON/INI": Make sure `config.json` is valid JSON or `config.ini` follows INI format.
- "OCI client error": When running in OCI Functions the function must have a Resource Principal with appropriate Logging permissions. Locally, Resource Principals aren't available.
- Large message runs can take long or hit API limits; the function limits are in place to avoid accidental overloads.

## Notes and potential improvements

- The function currently uses Resource Principals (OCI's server-side auth). If you want to test locally, modify `create_oci_client()` to fall back to a config-based signer (API key) when Resource Principals are unavailable.
- For very large volumes consider batching / rate-limiting or using a queuing approach.


