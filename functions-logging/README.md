## OCI Serverless Functions — Logging Samples

Samples on creating serverless functions on Oracle Cloud Infrastructure (OCI) that write logs to OCI Logging for utilities, analytics, monitoring, troubleshooting, etc.

- **Language**: Python (Fn Project runtime)
- **Infra as Code**: Terraform
- **Auth**: Resource Principals (no static keys)
- **Logging**: Logging Ingestion API

---

## Features

- **Sample functions** that emit data/logs to OCI Logging
- **Direct ingestion** via Logging Ingestion API/SDKs
- **Configurable** via environment variables or config files
- **Terraform** to provision Functions, Logging, networking, and IAM

---

## Repository Structure

```markdown
functions-logging/
├─ function/                    # Python sources (e.g., log_<usecase>.py)
│  ├─ func.yaml                 # Fn function definition
│  ├─ requirements.txt          # Python deps
│  ├─ config.json               # Sample runtime config
│  └─ README.md                 # Function-level docs/examples
└─ terraform/                   # Terraform for infra (Functions App, Logs, IAM, VCN)
   ├─ main.tf
   ├─ variables.tf
   └─ README.md
```

---

## Prerequisites

- OCI tenancy with permissions to create Functions, Logging, IAM, and Networking
- Region enabled for OCI Functions and Logging
- Docker and Fn CLI (`fn version`)
- Terraform v1.3+ (`terraform version`)
- Python 3.11+ (for local testing)

Optional:
- OCI CLI for troubleshooting

---

## How It Works

- Functions run with **Resource Principals** to securely call OCI services.
- Functions send logs to a target **Log** in a **Log Group** using the **Logging Ingestion API**.
- Configuration is passed via environment variables or JSON/INI files.

---

## Quick Start

### 1) Provision infrastructure (Terraform)

From `functions-logging/terraform`:

```bash
terraform init
terraform plan -out tf.plan \
  -var compartment_ocid="ocid1.compartment.oc1..example" \
  -var region="us-ashburn-1"
terraform apply tf.plan
```

Creates:
- Functions Application (in your VCN/subnet)
- Log Group and Log
- IAM dynamic groups and policies
- Networking (if included)

Terraform outputs include resource OCIDs (e.g., Log OCID).

### 2) Configure the function

From `functions-logging/function`, set variables (examples):

```bash
export LOG_ID="ocid1.log.oc1..example"
export MESSAGE_SIZE="256"           # optional
export CONFIG_FILE="config.json"    # optional
```

Or set values inside `config.json` and export `CONFIG_FILE`.

### 3) Build and deploy

```bash
cd function
fn create app <your-app-name> --annotation oracle.com/oci/subnetIds='["<subnet_ocid>"]'
fn deploy --app <your-app-name>
```

Ensure IAM policy allows Resource Principals to write to your Log (see IAM).

### 4) Invoke

```bash
fn invoke <your-app-name> <function-name> -b '{}'
```

View logs: Console → Logging → Log Groups → your Log.

---

## Configuration

- **Environment variables**
  - `LOG_ID`: Target Log OCID (required)
  - `MESSAGE_SIZE`: Size of generated message (optional)
  - Function-specific vars (see `function/README.md`)

- **Config file**
  - JSON (`config.json`), INI, CSV or other formats
  - Point to the file via `CONFIG_FILE=/path/to/config.json`

Environment variables take precedence.

---

## IAM Policies (examples)

Grant least privilege in the compartment hosting the Log:

```
Allow dynamic-resource-principal to use log-content in compartment <compartment_name_or_ocid>
```

If the function also needs to create/configure logging resources:

```
Allow dynamic-resource-principal to manage log-content in compartment <compartment_name_or_ocid>
```

---

## Local Development

```bash
cd function
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Example: run a simple local check (adjust to your handler)
python - <<'PY'
# Example scaffold; replace with your actual handler import/call
print("Local environment ready. Deploy to test with Resource Principals.")
PY
```

Notes:
- Resource Principals aren’t available locally; if calling OCI SDKs locally, use a config-based signer (see OCI SDK docs).
- Prefer deploying and invoking for end-to-end verification.

---

## Troubleshooting

- **Auth errors**: Verify the function’s dynamic group and IAM policies allow access to your Log.
- **No logs visible**: Confirm `LOG_ID` and region; check function execution logs in Functions Console.
- **Fn build issues**: Ensure Docker is running; try `fn --verbose deploy`.
- **Terraform errors**: Check credentials, region, and privileges for Functions/Logging/Networking.

---

## Cleaning Up

```bash
# Remove function/app
fn list apps
fn delete app <your-app-name>

# Destroy infra
cd terraform
terraform destroy
```

---

## License

Copyright (c) 2025 Oracle and/or its affiliates.

The Universal Permissive License (UPL), Version 1.0

Subject to the condition set forth below, permission is hereby granted to any
person obtaining a copy of this software, associated documentation and/or data
(collectively the "Software"), free of charge and under any and all copyright
rights in the Software, and any and all patent rights owned or freely
licensable by each licensor hereunder covering either (i) the unmodified
Software as contributed to or provided by such licensor, or (ii) the Larger
Works (as defined below), to deal in both

(a) the Software, and
(b) any piece of software and/or hardware listed in the lrgrwrks.txt file if
one is included with the Software (each a "Larger Work" to which the Software
is contributed by such licensors),

without restriction, including without limitation the rights to copy, create
derivative works of, display, perform, and distribute the Software and make,
use, sell, offer for sale, import, export, have made, and have sold the
Software and the Larger Work(s), and to sublicense the foregoing rights on
either these or other terms.

This license is subject to the following condition:
The above copyright notice and either this complete permission notice or at
a minimum a reference to the UPL must be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
