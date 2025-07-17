
![k8s-pilot-ci](https://github.com/user-attachments/assets/e2bc58d2-5ede-448b-bf4f-a3bb2c02cea4)


[![smithery badge](https://smithery.ai/badge/@bourbonkk/k8s-pilot)](https://smithery.ai/server/@bourbonkk/k8s-pilot) [![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/8645910c-340b-4f56-a03e-2c90d115a76f)

**The Central Pilot for Your Kubernetes Fleets ✈️✈️**

`k8s_pilot` is a lightweight, centralized control plane server for managing **multiple Kubernetes clusters** at once.  
With powerful tools and intuitive APIs, you can observe and control all your clusters from one cockpit.

---

## 🚀 Overview

- 🔄 Supports **multi-cluster context switching**
- 🔧 Enables **CRUD operations** on most common Kubernetes resources
- 🔒 **Readonly mode** for safe cluster inspection
- ⚙️ Powered by [MCP](https://modelcontextprotocol.io/) for Claude AI and beyond

---

## 🧰 Prerequisites

- Python **3.13** or higher
- [`uv`](https://github.com/astral-sh/uv) package manager
- Access to Kubernetes clusters (`~/.kube/config` or in-cluster config)

```bash
# Install uv (if not installed)

# For MacOS
brew install uv

# For Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

```bash
# Clone the repository
git clone https://github.com/bourbonkk/k8s-pilot.git
cd k8s-pilot

# Launch with uv + MCP
uv run --with mcp[cli] mcp run k8s_pilot.py
```

## Usage

### Normal Mode (Full Access)
```bash
# Start with full read/write access
uv run --with mcp[cli] mcp run k8s_pilot.py
```

### Readonly Mode (Safe Inspection)
```bash
# Start in readonly mode - only read operations allowed
uv run --with mcp[cli] python k8s_pilot.py --readonly
```

### Command Line Options
```bash
# Show help
uv run --with mcp[cli] python k8s_pilot.py --help
```

## Readonly Mode

The `--readonly` flag enables a safety mode that prevents any write operations to your Kubernetes clusters. This is perfect for:

- **Cluster inspection** without risk of accidental changes
- **Audit scenarios** where you need to view but not modify
- **Learning environments** where you want to explore safely
- **Production monitoring** with zero risk of modifications

### Protected Operations (Blocked in Readonly Mode)
- `pod_create`, `pod_update`, `pod_delete`
- `deployment_create`, `deployment_update`, `deployment_delete`
- `service_create`, `service_update`, `service_delete`
- `configmap_create`, `configmap_update`, `configmap_delete`
- `secret_create`, `secret_update`, `secret_delete`
- `namespace_create`, `namespace_delete`
- All other create/update/delete operations

### Allowed Operations (Always Available)
- `pod_list`, `pod_detail`, `pod_logs`
- `deployment_list`, `deployment_get`
- `service_list`, `service_get`
- `configmap_list`, `configmap_get`
- `secret_list`, `secret_get`
- `namespace_list`, `namespace_get`
- All other list/get operations

## Usage with Claude Desktop

Use this config to run k8s_pilot MCP server from within Claude:

```json
{
  "mcpServers": {
    "k8s_pilot": {
      "command": "uv",
      "args": [
        "--directory",
        "<path-to-cloned-repo>/k8s-pilot",
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "k8s_pilot.py"
      ]
    }
  }
}
```

For readonly mode, use this configuration:

```json
{
  "mcpServers": {
    "k8s_pilot_readonly": {
      "command": "uv",
      "args": [
        "--directory",
        "<path-to-cloned-repo>/k8s-pilot",
        "run",
        "--with",
        "mcp[cli]",
        "python",
        "k8s_pilot.py",
        "--readonly"
      ]
    }
  }
}
```

Replace <path-to-cloned-repo> with the actual directory where you cloned the repo.

## Scenario
Create a Deployment using the nginx:latest image in the pypy namespace, and also create a Service that connects to it.
![deploy와 서비스생성(영어](https://github.com/user-attachments/assets/eddc4ddf-ead9-47f2-aabc-e4e9e80a1e83)


## Key Features

### Multi-Cluster Management

- Seamlessly interact with multiple Kubernetes clusters
- Perform context-aware operations
- Easily switch between clusters via MCP prompts

### Resource Control

- View, create, update, delete:
    - Deployments, Services, Pods
    - ConfigMaps, Secrets, Ingresses
    - StatefulSets, DaemonSets
    - Roles, ClusterRoles
    - PersistentVolumes & Claims

### Namespace Operations

- Create/delete namespaces
- List all resources in a namespace
- Manage labels and resource quotas

### Node Management

- View node details and conditions
- Cordon/uncordon, label/taint nodes
- List pods per node

# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
