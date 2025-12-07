# Ansible Role: Azure DevOps Agents

Install and configure Azure DevOps self-hosted agents on Linux servers. This role supports **multiple agents per host** with different types: self-hosted (Agent Pools), deployment groups, and environments.

## ✨ Key Features

- 🎯 **Multi-Agent Support**: Deploy N agents on the same host, each with isolated directories
- 🔄 **Multiple Agent Types**: Self-hosted, Deployment Group, and Environment agents
- 🚀 **Auto-Create Resources**: Automatically create Deployment Groups and Environments via REST API
- 🔓 **Open Access**: Configure pipeline permissions for environments (YAML pipelines)
- ✅ **Service Verification**: Ensures all agent services are enabled and running
- 🗑️ **Agent Removal**: Unregister and remove agents from Azure DevOps
- 🏷️ **Tag Updates**: Update agent tags via REST API without reconfiguration
- 🐧 **Multi-Platform**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
- ⚙️ **Systemd Integration**: Automatic service management for each agent
- 🔐 **Security**: Dedicated non-root user for agent processes
- 📝 **Input Validation**: Comprehensive validation with clear error messages

📖 **Complete Guide**: [Azure DevOps Agents Complete Guide](../../docs/user-guides/azure-devops-agents/) - 8-part modular documentation with detailed explanations, diagrams, and production examples.

## 📋 Table of Contents

- [Requirements](#requirements)
- [Supported Distributions](#supported-distributions)
- [Role Variables](#role-variables)
- [Agent Types](#agent-types)
- [Auto-Create Resources](#auto-create-resources)
- [Open Access for Environments](#open-access-for-environments)
- [Input Validation](#input-validation)
- [Service Verification](#service-verification)
- [Agent State Management](#agent-state-management)
- [Tag Updates](#tag-updates)
- [Example Playbooks](#example-playbooks)
- [Multi-Agent Architecture](#multi-agent-architecture)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [License](#license)
- [Author Information](#author-information)

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- Azure DevOps organization with appropriate permissions
- Personal Access Token (PAT) with required scopes

### PAT Required Scopes

| Agent Type | Required Scope |
|------------|----------------|
| Self-hosted | Agent Pools (Read & manage) |
| Deployment Group | Deployment Groups (Read & manage) |
| Environment | Environment (Read & manage) |

## Supported Distributions

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/CentOS/Rocky/AlmaLinux** | 9, 10 |

## Role Variables

### Required Variables

```yaml
# Azure DevOps organization URL
azure_devops_agents_url: "https://dev.azure.com/myorganization"

# Personal Access Token (use Ansible Vault!)
azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

# List of agents to configure
azure_devops_agents_list:
  - name: "agent-01"
    type: "self-hosted"
    pool: "Default"
```

### Optional Variables

```yaml
# Global state: 'present' (default) or 'absent' (remove all agents)
azure_devops_agents_state: "present"

# Agent version (empty = latest)
azure_devops_agents_version: ""

# Base directory for all agents
azure_devops_agents_base_path: "/opt/azure-devops-agents"

# User/group for running agents
azure_devops_agents_user: "azagent"
azure_devops_agents_group: "azagent"

# Create user if doesn't exist
azure_devops_agents_create_user: true

# Run as systemd service
azure_devops_agents_run_as_service: true

# Service configuration
azure_devops_agents_service_enabled: true
azure_devops_agents_service_state: started

# Accept TEE EULA (required for TFVC)
azure_devops_agents_accept_tee_eula: true

# Delete agent directory after removal (when state: absent)
azure_devops_agents_delete_on_remove: true
```

### Proxy Settings (Optional)

```yaml
azure_devops_agents_proxy_url: "http://proxy.company.com:8080"
azure_devops_agents_proxy_user: "proxyuser"
azure_devops_agents_proxy_password: "{{ vault_proxy_password }}"
azure_devops_agents_proxy_bypass: "localhost,127.0.0.1"
```

## Agent Types

### 1. Self-Hosted Agent (Agent Pool)

Standard build/release agent registered in an Agent Pool.

```yaml
azure_devops_agents_list:
  - name: "build-agent-01"
    type: "self-hosted"
    pool: "Linux-Pool"        # Agent pool name
    replace: true             # Replace if exists
    work_dir: "_work"         # Work directory
    tags:                     # Capability tags
      - "docker"
      - "nodejs"
```

### 2. Deployment Group Agent

Agent for Classic Release pipelines using Deployment Groups.

```yaml
azure_devops_agents_list:
  - name: "deploy-agent-01"
    type: "deployment-group"
    project: "MyProject"              # Azure DevOps project
    deployment_group: "Production"    # Deployment group name
    auto_create: true                 # Create if doesn't exist
    replace: true
    tags:
      - "web"
      - "linux"
```

### 3. Environment Agent

Agent for YAML pipelines using Environments.

```yaml
azure_devops_agents_list:
  - name: "env-agent-01"
    type: "environment"
    project: "MyProject"          # Azure DevOps project
    environment: "production"     # Environment name
    auto_create: true             # Create if doesn't exist
    open_access: true             # Allow all pipelines to use
    replace: true
    tags:
      - "api"
      - "backend"
```

## Auto-Create Resources

The role can automatically create Deployment Groups and Environments if they don't exist in Azure DevOps.

### Enabling Auto-Create

Add `auto_create: true` to your agent configuration:

```yaml
azure_devops_agents_list:
  # Auto-create deployment group
  - name: "deploy-agent-01"
    type: "deployment-group"
    project: "MyProject"
    deployment_group: "NewProductionGroup"
    auto_create: true  # ✅ Creates deployment group if missing
    tags:
      - "production"

  # Auto-create environment
  - name: "env-agent-01"
    type: "environment"
    project: "MyProject"
    environment: "staging"
    auto_create: true  # ✅ Creates environment if missing
    tags:
      - "staging"
```

### How It Works

| Resource Type | Creation Method | API Endpoint |
|---------------|-----------------|--------------|
| Deployment Group | REST API | `POST /{project}/_apis/distributedtask/deploymentgroups` |
| Environment | REST API | `POST /{project}/_apis/pipelines/environments` |

### PAT Permissions Required

For auto-create to work, your PAT needs additional permissions:

| Resource | Required Scope |
|----------|----------------|
| Deployment Group | **Deployment Groups (Read & manage)** |
| Environment | **Environment (Read & manage)** |

### Auto-Create Disabled (Default)

By default, `auto_create: false`, and the role will fail if the resource doesn't exist:

```
TASK [azure_devops_agents : Register agent] ****
fatal: [server1]: FAILED! =>
  msg: "Deployment Group 'Production' not found in project 'MyProject'"
```

## Open Access for Environments

Environments support the `open_access` feature, which allows **all pipelines** in the project to use the environment without explicit authorization.

### Enabling Open Access

```yaml
azure_devops_agents_list:
  - name: "env-agent-01"
    type: "environment"
    project: "MyProject"
    environment: "development"
    auto_create: true
    open_access: true  # ✅ All pipelines can use this environment
    tags:
      - "dev"
```

### How It Works

When `open_access: true`, the role:

1. Creates the environment (if `auto_create: true`)
2. Calls the Pipeline Permissions API to authorize all pipelines:

```
PATCH /{project}/_apis/pipelines/pipelinepermissions/environment/{environmentId}
{
  "pipelines": [],
  "allPipelines": {
    "authorized": true,
    "authorizedBy": null,
    "authorizedOn": null
  }
}
```

### ⚠️ Deployment Groups: Open Access Not Supported

**Important**: The `open_access` feature is **NOT available for Deployment Groups**.

Deployment Groups use a different authorization model and the Pipeline Permissions API doesn't support `allPipelines` for this resource type.

| Agent Type | `open_access` Support |
|------------|----------------------|
| **environment** | ✅ Supported |
| **deployment-group** | ❌ Not supported (Azure DevOps limitation) |
| **self-hosted** | N/A (uses Agent Pools) |

### Use Cases for Open Access

| Environment Type | `open_access` | Notes |
|------------------|---------------|-------|
| **development** | `true` | All devs can deploy |
| **staging** | `true` | CI/CD can deploy freely |
| **production** | `false` | Require explicit approval |

### Example: Development vs Production

```yaml
azure_devops_agents_list:
  # Development - open access
  - name: "dev-agent"
    type: "environment"
    project: "WebApp"
    environment: "development"
    auto_create: true
    open_access: true  # Any pipeline can deploy

  # Production - restricted
  - name: "prod-agent"
    type: "environment"
    project: "WebApp"
    environment: "production"
    auto_create: true
    open_access: false  # Requires explicit pipeline authorization
```

## Input Validation

The role includes comprehensive input validation that runs before any configuration:

### Validation Rules

| Rule | Description |
|------|-------------|
| **URL required** | `azure_devops_agents_url` must be set |
| **PAT required** | `azure_devops_agents_pat` must be set |
| **Agent list required** | `azure_devops_agents_list` must have at least one agent |
| **Valid agent type** | Type must be `self-hosted`, `deployment-group`, or `environment` |
| **Pool required** | Self-hosted agents must have `pool` defined |
| **Project required** | Deployment-group and environment agents must have `project` |
| **Resource required** | Deployment-group needs `deployment_group`, environment needs `environment` |
| **open_access validation** | `open_access` only valid for environment agents |

### Validation Errors

Errors are displayed with clear ASCII-box formatting:

```
TASK [azure_devops_agents : Fail with validation errors] ****
fatal: [server1]: FAILED! =>
  msg: |-
    ╔════════════════════════════════════════════════════════════════╗
    ║           AZURE DEVOPS AGENTS - VALIDATION ERRORS              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ The following configuration errors were found:                 ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ ✗ Agent 'web-agent': Type 'deployment-group' requires          ║
    ║   'deployment_group' to be defined                             ║
    ║                                                                ║
    ║ ✗ Agent 'api-agent': 'open_access' is only valid for           ║
    ║   type 'environment', not 'deployment-group'                   ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ Please fix these errors and run the playbook again.            ║
    ╚════════════════════════════════════════════════════════════════╝

## Service Verification

At the end of every successful run, the role verifies that **all agent services are properly configured**:

### What Gets Verified

1. **Service exists**: Checks that systemd service files were created
2. **Service enabled**: Verifies services are enabled to start on boot
3. **Service running**: Confirms all agents are actively running

### Verification Output

```
TASK [azure_devops_agents : Verify agent services] ****
ok: [server1] => {
    "msg": [
        "Service Verification Summary:",
        "  ✓ vsts.agent.myorg.build-agent - enabled: true, running: true",
        "  ✓ vsts.agent.myorg.deploy-agent - enabled: true, running: true",
        "  ✓ vsts.agent.myorg.env-agent - enabled: true, running: true"
    ]
}
```

### Verification Failure

If any service is not properly configured, the role will:

1. **Display detailed status** for all services
2. **Fail the playbook** with actionable error message
3. **Log troubleshooting commands** for investigation

```
TASK [azure_devops_agents : Fail if services not running] ****
fatal: [server1]: FAILED! =>
  msg: |-
    ╔════════════════════════════════════════════════════════════════╗
    ║         AZURE DEVOPS AGENTS - SERVICE VERIFICATION FAILED      ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ The following services are not properly configured:            ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ ✗ vsts.agent.myorg.build-agent - enabled: true, running: false ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ Troubleshooting:                                               ║
    ║   sudo systemctl status vsts.agent.myorg.build-agent           ║
    ║   sudo journalctl -u vsts.agent.myorg.build-agent              ║
    ╚════════════════════════════════════════════════════════════════╝
```

## Agent State Management

The role supports both installation and removal of agents using the `state` variable.

### Global State

Use `azure_devops_agents_state` to control all agents:

```yaml
# Remove ALL agents from the host
azure_devops_agents_state: "absent"
```

### Per-Agent State

Control individual agents with the `state` property:

```yaml
azure_devops_agents_list:
  # This agent will be installed/configured
  - name: "build-agent-01"
    type: "self-hosted"
    pool: "Linux-Pool"
    state: present  # Default if not specified

  # This agent will be REMOVED
  - name: "old-agent"
    type: "self-hosted"
    pool: "Legacy-Pool"
    state: absent  # Will unregister and remove
```

### Removal Process

When an agent is marked for removal (`state: absent`), the role will:

1. **Stop the systemd service** (if running)
2. **Uninstall the service** (`svc.sh uninstall`)
3. **Unregister from Azure DevOps** (`config.sh remove`)
4. **Delete the agent directory** (if `azure_devops_agents_delete_on_remove: true`)

### Example: Decommissioning Agents

```yaml
---
- name: Remove Azure DevOps agents
  hosts: old_build_servers
  become: true

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    # Option 1: Remove specific agents
    azure_devops_agents_list:
      - name: "agent-to-remove"
        type: "self-hosted"
        pool: "Default"
        state: absent

    # Option 2: Remove ALL agents from host
    # azure_devops_agents_state: "absent"

  roles:
    - code3tech.devtools.azure_devops_agents
```

## Tag Updates

The role supports updating agent tags **without reconfiguring** the entire agent. This is useful when you need to add or modify tags on existing agents.

### How It Works

| Agent Type | Tag Update Method | Notes |
|------------|-------------------|-------|
| **deployment-group** | ✅ REST API | Updates tags via Azure DevOps API |
| **environment** | ✅ REST API | Updates VM resource tags via API |
| **self-hosted** | ⚠️ Not supported | Uses capabilities, requires `replace: true` |

### Update Tags Example

```yaml
azure_devops_agents_list:
  # Update tags on existing deployment group agent
  - name: "deploy-agent-01"
    type: "deployment-group"
    project: "MyProject"
    deployment_group: "Production"
    update_tags: true  # Enable tag update via API
    tags:
      - "web"
      - "nginx"
      - "new-tag"  # New tag to add

  # Update tags on existing environment agent
  - name: "env-agent-01"
    type: "environment"
    project: "MyProject"
    environment: "production"
    update_tags: true
    tags:
      - "api"
      - "backend"
      - "updated-tag"
```

### Tag Update vs Reconfiguration

| Scenario | Use `update_tags: true` | Use `replace: true` |
|----------|-------------------------|---------------------|
| Add/remove tags only | ✅ Fast, no downtime | ❌ Overkill |
| Change pool/environment | ❌ Not possible | ✅ Required |
| Change agent name | ❌ Not possible | ✅ Required |
| Self-hosted capabilities | ❌ Not supported | ✅ Required |

### Example: Update Tags Only

```yaml
---
- name: Update agent tags without reconfiguration
  hosts: agent_servers
  become: true

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    azure_devops_agents_list:
      - name: "deploy-agent-01"
        type: "deployment-group"
        project: "WebApp"
        deployment_group: "Production-Servers"
        update_tags: true
        tags:
          - "web"
          - "linux"
          - "docker"  # New tag

  roles:
    - code3tech.devtools.azure_devops_agents
```

**Note**: The `update_tags` feature requires the agent to already be configured. If the agent doesn't exist, it will be skipped.

## Example Playbooks

### Basic: Single Self-Hosted Agent

```yaml
---
- name: Install Azure DevOps agent
  hosts: build_servers
  become: true

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"
    azure_devops_agents_list:
      - name: "linux-agent-01"
        type: "self-hosted"
        pool: "Default"

  roles:
    - code3tech.devtools.azure_devops_agents
```

### Advanced: Multiple Agents per Host

```yaml
---
- name: Deploy multiple Azure DevOps agents
  hosts: agent_servers
  become: true

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    azure_devops_agents_list:
      # Self-hosted agent for builds
      - name: "build-agent"
        type: "self-hosted"
        pool: "Linux-Builds"
        tags:
          - "docker"
          - "nodejs"

      # Deployment group agent for releases
      - name: "deploy-agent"
        type: "deployment-group"
        project: "WebApp"
        deployment_group: "Production-Servers"
        tags:
          - "web"
          - "nginx"

      # Environment agent for YAML pipelines
      - name: "env-agent"
        type: "environment"
        project: "WebApp"
        environment: "production"
        tags:
          - "api"

  roles:
    - code3tech.devtools.azure_devops_agents
```

### With Proxy Configuration

```yaml
---
- name: Install agent behind proxy
  hosts: internal_servers
  become: true

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    azure_devops_agents_proxy_url: "http://proxy.internal:8080"
    azure_devops_agents_proxy_user: "{{ vault_proxy_user }}"
    azure_devops_agents_proxy_password: "{{ vault_proxy_password }}"

    azure_devops_agents_list:
      - name: "internal-agent"
        type: "self-hosted"
        pool: "Internal-Pool"

  roles:
    - code3tech.devtools.azure_devops_agents
```

## Multi-Agent Architecture

When deploying multiple agents on the same host, the role creates an isolated directory structure:

```
/opt/azure-devops-agents/          # Base path
├── .downloads/                    # Shared agent package downloads
│   └── vsts-agent-linux-x64-X.X.X.tar.gz
├── build-agent/                   # Agent 1 (self-hosted)
│   ├── config.sh
│   ├── run.sh
│   ├── svc.sh
│   ├── _work/                     # Agent work directory
│   └── ...
├── deploy-agent/                  # Agent 2 (deployment-group)
│   ├── config.sh
│   ├── run.sh
│   ├── svc.sh
│   ├── _work/
│   └── ...
└── env-agent/                     # Agent 3 (environment)
    ├── config.sh
    ├── run.sh
    ├── svc.sh
    ├── _work/
    └── ...
```

### Systemd Services

Each agent runs as an independent systemd service:

```bash
# Service naming convention
vsts.agent.{organization}.{agent-name}.service

# Examples
vsts.agent.myorg.build-agent.service
vsts.agent.myorg.deploy-agent.service
vsts.agent.myorg.env-agent.service

# Management commands
sudo systemctl status vsts.agent.myorg.build-agent
sudo systemctl restart vsts.agent.myorg.build-agent
```

## Security Considerations

### ⚠️ PAT Token Security

**ALWAYS use Ansible Vault for the PAT token!**

```bash
# Create encrypted vault file
ansible-vault create vars/azure_secrets.yml

# Content
vault_azure_devops_pat: "your-pat-token-here"
```

```yaml
# In playbook
vars_files:
  - vars/azure_secrets.yml

vars:
  azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"
```

### Agent User Isolation

The role creates a dedicated `azagent` user:
- System user with no login shell access
- Owns only the agent directories
- Runs agent processes with minimal privileges
- Cannot run as root (Azure DevOps agent restriction)

### Best Practices

1. **Minimal PAT Scope**: Create PATs with only required permissions
2. **PAT Expiration**: Set short expiration dates and rotate regularly
3. **Network Security**: Use private agent pools for sensitive workloads
4. **Secrets in Pipelines**: Use Azure DevOps secret variables, not hardcoded values

## Testing

This role includes Molecule tests:

```bash
cd roles/azure_devops_agents
molecule test
```

**Note**: Full agent registration requires valid Azure DevOps credentials. Molecule tests verify:
- User and group creation
- Directory structure
- Prerequisite packages
- File permissions

## Troubleshooting

### Agent Registration Fails

```bash
# Check agent logs
tail -f /opt/azure-devops-agents/<agent-name>/_diag/*.log

# Verify connectivity
curl -I https://dev.azure.com/<organization>
```

### Service Won't Start

```bash
# Check service status
sudo systemctl status vsts.agent.<org>.<agent-name>

# View service logs
sudo journalctl -u vsts.agent.<org>.<agent-name> -f
```

### Reconfigure Agent

```bash
# Stop and unconfigure
cd /opt/azure-devops-agents/<agent-name>
sudo ./svc.sh stop
./config.sh remove

# Re-run playbook with replace: true
```

## Dependencies

None.

## License

MIT

## Author Information

This role was created by the **Code3Tech DevOps Team**.

- GitHub: [code3tech](https://github.com/kode3tech)
- Repository: [ansible-col-devtools](https://github.com/kode3tech/ansible-col-devtools)

## References

- [Azure DevOps Self-hosted Linux Agents](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent)
- [Deployment Groups](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/deployment-groups/)
- [Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments)
- [Agent Authentication Options](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agent-authentication-options)
