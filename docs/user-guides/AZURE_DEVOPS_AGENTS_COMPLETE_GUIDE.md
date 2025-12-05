# Azure DevOps Agents Complete Guide

Comprehensive guide for deploying and managing Azure DevOps self-hosted agents using the `code3tech.devtools.azure_devops_agents` role.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Agent Types Explained](#agent-types-explained)
- [Production Deployment](#production-deployment)
- [Advanced Features](#advanced-features)
- [Security Best Practices](#security-best-practices)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

## Overview

The `azure_devops_agents` role provides enterprise-grade deployment of Azure DevOps self-hosted agents on Linux servers. It supports three agent types, multiple agents per host, and advanced features like auto-creation of resources and pipeline permissions.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Agent** | Deploy N agents on the same host with isolated directories |
| **Three Agent Types** | Self-hosted, Deployment Group, and Environment agents |
| **Auto-Create** | Automatically create Deployment Groups and Environments |
| **Open Access** | Configure pipeline permissions for environments |
| **Service Verification** | Ensures all services are enabled and running |
| **Agent Removal** | Clean unregistration and removal of agents |
| **Tag Updates** | Update agent tags via REST API without reconfiguration |
| **Input Validation** | Comprehensive validation with clear error messages |

### Supported Platforms

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04, 24.04, 25.04 |
| **Debian** | 11, 12, 13 |
| **RHEL/Rocky/Alma** | 9, 10 |

## Architecture

### Multi-Agent Directory Structure

```
/opt/azure-devops-agents/              # Base path (configurable)
├── .downloads/                        # Shared agent packages
│   └── vsts-agent-linux-x64-4.X.X.tar.gz
├── build-agent-01/                    # Agent 1
│   ├── config.sh                      # Configuration script
│   ├── run.sh                         # Manual run script
│   ├── svc.sh                         # Service management
│   ├── .credentials                   # OAuth credentials
│   ├── .agent                         # Agent configuration
│   ├── .service                       # Service name file
│   └── _work/                         # Pipeline work directory
├── deploy-agent-01/                   # Agent 2
│   └── ...
└── env-agent-01/                      # Agent 3
    └── ...
```

### Systemd Services

Each agent runs as an independent systemd service:

```bash
# Service naming convention
vsts.agent.{organization}.{agent-name}.service

# Example services
vsts.agent.myorg.build-agent-01.service
vsts.agent.myorg.deploy-agent-01.service
vsts.agent.myorg.env-agent-01.service
```

### Process Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Validation    │───▶│  Prerequisites  │───▶│  Download Agent │
│                 │    │  (packages)     │    │  (cached)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auto-Create    │───▶│  Configure &    │───▶│  Install        │
│  Resources      │    │  Register       │    │  Service        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Set Pipeline   │───▶│  Verify         │
│  Permissions    │    │  Services       │
└─────────────────┘    └─────────────────┘
```

## Prerequisites

### Azure DevOps Requirements

1. **Organization**: An Azure DevOps organization (e.g., `https://dev.azure.com/myorg`)

2. **Personal Access Token (PAT)** with appropriate scopes:

   | Agent Type | Required Scope |
   |------------|----------------|
   | Self-hosted | Agent Pools (Read & manage) |
   | Deployment Group | Deployment Groups (Read & manage) |
   | Environment | Environment (Read & manage) |

3. **Resources** (created manually or auto-created):
   - Agent Pools (for self-hosted agents)
   - Projects (for deployment-group and environment agents)
   - Deployment Groups or Environments

### Creating a PAT

1. Go to Azure DevOps → User Settings → Personal Access Tokens
2. Click "New Token"
3. Configure:
   - **Name**: `ansible-agent-deployment`
   - **Expiration**: Choose appropriate duration
   - **Scopes**: Select required scopes based on agent types
4. Copy and securely store the token

### Ansible Requirements

```yaml
# requirements.yml
collections:
  - name: code3tech.devtools
    version: ">=1.1.0"
```

```bash
# Install collection
ansible-galaxy collection install -r requirements.yml
```

## Quick Start

### 1. Create Vault File for PAT

```bash
# Create encrypted vault file
ansible-vault create vars/azure_secrets.yml
```

Content:
```yaml
vault_azure_devops_pat: "your-pat-token-here"
```

### 2. Create Inventory

```ini
# inventory.ini
[agent_servers]
server1.example.com
server2.example.com

[agent_servers:vars]
ansible_user=deploy
ansible_become=true
```

### 3. Create Playbook

```yaml
# install-agents.yml
---
- name: Deploy Azure DevOps agents
  hosts: agent_servers
  become: true

  vars_files:
    - vars/azure_secrets.yml

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorganization"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    azure_devops_agents_list:
      - name: "build-agent"
        type: "self-hosted"
        pool: "Linux-Pool"
        tags:
          - "docker"
          - "linux"

  roles:
    - code3tech.devtools.azure_devops_agents
```

### 4. Run Playbook

```bash
ansible-playbook install-agents.yml -i inventory.ini --ask-vault-pass
```

## Agent Types Explained

### Self-Hosted Agents (Agent Pools)

**Purpose**: General-purpose build and release agents.

**Use Cases**:
- CI/CD pipelines (build, test, package)
- Multi-project shared agents
- Org-level resource pooling

**Configuration**:
```yaml
azure_devops_agents_list:
  - name: "build-agent-01"
    type: "self-hosted"
    pool: "Linux-Pool"           # Agent pool name (must exist)
    replace: true                # Replace existing agent
    work_dir: "_work"            # Work directory name
    tags:
      - "docker"
      - "nodejs"
      - "linux"
```

**Azure DevOps Location**: Organization Settings → Agent Pools

### Deployment Group Agents

**Purpose**: Target servers for Classic Release pipelines.

**Use Cases**:
- Classic Release deployments
- Multi-stage deployment targeting
- Server-based deployments (IIS, services)

**Configuration**:
```yaml
azure_devops_agents_list:
  - name: "web-server-01"
    type: "deployment-group"
    project: "WebApplication"           # Project name
    deployment_group: "Production-Web"  # Deployment group name
    auto_create: true                   # Create if doesn't exist
    replace: true
    tags:
      - "web"
      - "nginx"
      - "production"
```

**Azure DevOps Location**: Project → Pipelines → Deployment Groups

### Environment Agents

**Purpose**: Target VMs for YAML pipelines with Environments.

**Use Cases**:
- YAML multi-stage pipelines
- Kubernetes-style deployments
- Environment-based approvals and checks

**Configuration**:
```yaml
azure_devops_agents_list:
  - name: "api-server-01"
    type: "environment"
    project: "WebApplication"        # Project name
    environment: "production"        # Environment name
    auto_create: true                # Create if doesn't exist
    open_access: true                # Allow all pipelines
    replace: true
    tags:
      - "api"
      - "dotnet"
      - "production"
```

**Azure DevOps Location**: Project → Pipelines → Environments

### Comparison Table

| Feature | Self-Hosted | Deployment Group | Environment |
|---------|-------------|------------------|-------------|
| **Pipeline Type** | All | Classic Release | YAML |
| **Scope** | Organization | Project | Project |
| **Auto-Create** | ❌ (pools pre-exist) | ✅ | ✅ |
| **Open Access** | N/A | ❌ | ✅ |
| **Tag Update API** | ❌ | ✅ | ✅ |
| **Multi-Project** | ✅ | ❌ | ❌ |

## Production Deployment

### Production Playbook Template

```yaml
---
# playbooks/azure_devops_agents/install-production.yml
- name: Deploy Azure DevOps agents - Production
  hosts: agent_servers
  become: true

  vars_files:
    - vars/azure_secrets.yml

  vars:
    # Azure DevOps Configuration
    azure_devops_agents_url: "https://dev.azure.com/{{ azure_org }}"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    # Agent Configuration
    azure_devops_agents_version: ""  # Empty = latest
    azure_devops_agents_base_path: "/opt/azure-devops-agents"
    azure_devops_agents_user: "azagent"
    azure_devops_agents_group: "azagent"

    # Service Configuration
    azure_devops_agents_run_as_service: true
    azure_devops_agents_service_enabled: true
    azure_devops_agents_service_state: started

    # Agent List (from inventory or group_vars)
    azure_devops_agents_list: "{{ agent_config }}"

  pre_tasks:
    - name: Validate time synchronization
      ansible.builtin.command: timedatectl status
      changed_when: false
      register: time_status

    - name: Display time status
      ansible.builtin.debug:
        var: time_status.stdout_lines

  roles:
    - code3tech.devtools.azure_devops_agents

  post_tasks:
    - name: Verify agent connectivity
      ansible.builtin.uri:
        url: "{{ azure_devops_agents_url }}/_apis/projects?api-version=7.0"
        headers:
          Authorization: "Basic {{ ('' ~ ':' ~ azure_devops_agents_pat) | b64encode }}"
        status_code: 200
      delegate_to: localhost
      run_once: true
```

### Inventory with Agent Configuration

```yaml
# inventory/production/hosts.yml
all:
  children:
    build_servers:
      hosts:
        build01.prod.example.com:
        build02.prod.example.com:
      vars:
        agent_config:
          - name: "build-agent"
            type: "self-hosted"
            pool: "Linux-Production"
            tags:
              - "docker"
              - "production"

    deployment_servers:
      hosts:
        web01.prod.example.com:
        web02.prod.example.com:
      vars:
        agent_config:
          - name: "deploy-agent"
            type: "deployment-group"
            project: "WebApp"
            deployment_group: "Production-Servers"
            auto_create: true
            tags:
              - "web"
              - "production"

    environment_servers:
      hosts:
        api01.prod.example.com:
        api02.prod.example.com:
      vars:
        agent_config:
          - name: "env-agent"
            type: "environment"
            project: "WebApp"
            environment: "production"
            auto_create: true
            open_access: false  # Require explicit authorization
            tags:
              - "api"
              - "production"
```

### Running Production Deployment

```bash
# Deploy to all servers
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i inventory/production/hosts.yml \
  --ask-vault-pass

# Deploy to specific group
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i inventory/production/hosts.yml \
  --limit build_servers \
  --ask-vault-pass

# Dry run (check mode)
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i inventory/production/hosts.yml \
  --check --diff \
  --ask-vault-pass
```

## Advanced Features

### Auto-Create Resources

Automatically create Deployment Groups and Environments if they don't exist:

```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "NewProject"
    deployment_group: "NewDeploymentGroup"
    auto_create: true  # ✅ Creates deployment group via REST API

  - name: "env-agent"
    type: "environment"
    project: "NewProject"
    environment: "staging"
    auto_create: true  # ✅ Creates environment via REST API
```

### Open Access for Environments

Allow all pipelines to use an environment without explicit authorization:

```yaml
azure_devops_agents_list:
  # Development - open to all
  - name: "dev-agent"
    type: "environment"
    project: "WebApp"
    environment: "development"
    auto_create: true
    open_access: true  # ✅ Any pipeline can deploy

  # Production - restricted
  - name: "prod-agent"
    type: "environment"
    project: "WebApp"
    environment: "production"
    auto_create: true
    open_access: false  # ❌ Requires explicit authorization
```

> **Note**: `open_access` is only available for Environment agents. Deployment Groups use a different authorization model.

### Tag Updates Without Reconfiguration

Update agent tags via REST API without stopping or reconfiguring the agent:

```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "WebApp"
    deployment_group: "Production"
    update_tags: true  # ✅ Update tags via API
    tags:
      - "web"
      - "nginx"
      - "new-capability"  # Added tag
```

### Agent Removal

Remove agents cleanly with proper unregistration:

```yaml
# Remove specific agents
azure_devops_agents_list:
  - name: "old-agent"
    type: "self-hosted"
    pool: "Legacy-Pool"
    state: absent  # ✅ Unregister and remove

# Or remove ALL agents from host
azure_devops_agents_state: "absent"
```

### Proxy Configuration

Deploy agents behind a corporate proxy:

```yaml
azure_devops_agents_url: "https://dev.azure.com/myorg"
azure_devops_agents_pat: "{{ vault_pat }}"

azure_devops_agents_proxy_url: "http://proxy.corp.example.com:8080"
azure_devops_agents_proxy_user: "{{ vault_proxy_user }}"
azure_devops_agents_proxy_password: "{{ vault_proxy_password }}"
azure_devops_agents_proxy_bypass: "localhost,127.0.0.1,*.internal.example.com"

azure_devops_agents_list:
  - name: "internal-agent"
    type: "self-hosted"
    pool: "Internal-Pool"
```

## Security Best Practices

### 1. PAT Token Management

**Always use Ansible Vault**:

```bash
# Create vault
ansible-vault create vars/azure_secrets.yml

# Edit vault
ansible-vault edit vars/azure_secrets.yml

# View vault
ansible-vault view vars/azure_secrets.yml
```

**Vault password file for CI/CD**:

```bash
# Create password file (add to .gitignore!)
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass

# Use in playbook
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

### 2. PAT Scope Minimization

Create dedicated PATs with minimal scope:

| Deployment Type | Recommended Scopes |
|-----------------|-------------------|
| Build agents only | Agent Pools (Read & manage) |
| Deploy agents only | Deployment Groups (Read & manage) |
| Environment agents | Environment (Read & manage) |
| All types | All above scopes |

### 3. Agent User Isolation

The role creates a dedicated `azagent` user:

- System user with no login shell
- Owns only agent directories
- Cannot run as root (Azure DevOps restriction)
- Minimal system privileges

### 4. Network Security

**Outbound Requirements**:

| Destination | Port | Purpose |
|-------------|------|---------|
| `dev.azure.com` | 443 | Azure DevOps API |
| `vstsagentpackage.azureedge.net` | 443 | Agent packages |
| `download.agent.dev.azure.com` | 443 | Agent downloads |

**Firewall rules** (if needed):

```bash
# Allow outbound HTTPS to Azure DevOps
sudo ufw allow out 443/tcp
```

### 5. Secret Management in Pipelines

Never hardcode secrets in pipeline YAML. Use Azure DevOps variable groups or Azure Key Vault:

```yaml
# pipeline.yml
variables:
  - group: production-secrets  # Variable group with secrets

steps:
  - script: |
      echo "Using secret: $(MY_SECRET)"
    env:
      MY_SECRET: $(mySecretVariable)  # Map secret to env var
```

## Monitoring and Maintenance

### Check Agent Status

```bash
# List all agent services
systemctl list-units 'vsts.agent.*'

# Check specific agent
systemctl status vsts.agent.myorg.build-agent

# View agent logs
journalctl -u vsts.agent.myorg.build-agent -f
```

### Agent Diagnostics

```bash
# Agent directory
cd /opt/azure-devops-agents/build-agent

# View diagnostic logs
ls -la _diag/
tail -f _diag/Agent_*.log

# Check agent configuration
cat .agent | jq .
```

### Update Agents

The Azure DevOps agent auto-updates by default. To force a specific version:

```yaml
azure_devops_agents_version: "4.264.2"  # Pin to specific version
```

### Rotate PAT Tokens

1. Create new PAT in Azure DevOps
2. Update Ansible vault:
   ```bash
   ansible-vault edit vars/azure_secrets.yml
   ```
3. Re-run playbook to reconfigure agents:
   ```bash
   ansible-playbook install-agents.yml --ask-vault-pass
   ```

## Troubleshooting

### Common Issues

#### Agent Registration Fails

**Symptom**: `VS30063: You are not authorized to access https://dev.azure.com/myorg`

**Solution**:
1. Verify PAT token is valid and not expired
2. Check PAT has required scopes
3. Ensure network connectivity to Azure DevOps

```bash
# Test connectivity
curl -I https://dev.azure.com/myorg

# Test PAT
curl -u :YOUR_PAT https://dev.azure.com/myorg/_apis/projects?api-version=7.0
```

#### Service Won't Start

**Symptom**: Service fails to start or crashes immediately

**Solution**:
```bash
# Check service status
systemctl status vsts.agent.myorg.agent-name

# View full logs
journalctl -u vsts.agent.myorg.agent-name --no-pager

# Check agent logs
cat /opt/azure-devops-agents/agent-name/_diag/Agent_*.log
```

#### Deployment Group Not Found

**Symptom**: `Deployment Group 'X' not found in project 'Y'`

**Solution**: Enable auto-create:
```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "MyProject"
    deployment_group: "Production"
    auto_create: true  # Add this
```

#### curl-minimal Conflict (Rocky Linux)

**Symptom**: Package conflict with `curl-minimal` on Rocky Linux

**Solution**: The role handles this automatically with `allowerasing: true`. If manual fix needed:
```bash
sudo dnf install curl --allowerasing
```

#### Invalid Agent Name

**Symptom**: Agent name contains invalid characters

**Solution**: The role automatically sanitizes hostnames (replaces `.` with `-`). Manual naming:
```yaml
azure_devops_agents_list:
  - name: "custom-agent-name"  # Use simple alphanumeric names
    type: "self-hosted"
    pool: "Default"
```

### Diagnostic Commands

```bash
# Check agent service status
systemctl status 'vsts.agent.*'

# View all agent logs
journalctl -u 'vsts.agent.*' --since today

# Test Azure DevOps connectivity
curl -sf https://dev.azure.com/myorg/_apis/projects?api-version=7.0 \
  -u :YOUR_PAT | jq .

# Check agent configuration
cat /opt/azure-devops-agents/agent-name/.agent | jq .

# Verify agent user
id azagent
ls -la /opt/azure-devops-agents/
```

## Reference

### All Role Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `azure_devops_agents_url` | string | **required** | Azure DevOps organization URL |
| `azure_devops_agents_pat` | string | **required** | Personal Access Token |
| `azure_devops_agents_list` | list | **required** | List of agents to configure |
| `azure_devops_agents_state` | string | `present` | Global state: present/absent |
| `azure_devops_agents_version` | string | `""` | Agent version (empty = latest) |
| `azure_devops_agents_base_path` | string | `/opt/azure-devops-agents` | Base directory |
| `azure_devops_agents_user` | string | `azagent` | Agent user |
| `azure_devops_agents_group` | string | `azagent` | Agent group |
| `azure_devops_agents_create_user` | bool | `true` | Create user if missing |
| `azure_devops_agents_run_as_service` | bool | `true` | Install as systemd service |
| `azure_devops_agents_service_enabled` | bool | `true` | Enable service on boot |
| `azure_devops_agents_service_state` | string | `started` | Service state |
| `azure_devops_agents_accept_tee_eula` | bool | `true` | Accept TEE EULA |
| `azure_devops_agents_delete_on_remove` | bool | `true` | Delete directory on removal |

### Agent List Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Agent name |
| `type` | string | Yes | `self-hosted`, `deployment-group`, `environment` |
| `state` | string | No | `present` (default) or `absent` |
| `pool` | string | For self-hosted | Agent pool name |
| `project` | string | For DG/Env | Azure DevOps project name |
| `deployment_group` | string | For DG | Deployment group name |
| `environment` | string | For Env | Environment name |
| `auto_create` | bool | No | Create resource if missing |
| `open_access` | bool | No | Allow all pipelines (env only) |
| `replace` | bool | No | Replace existing agent |
| `update_tags` | bool | No | Update tags via API |
| `work_dir` | string | No | Work directory name |
| `tags` | list | No | Agent tags/capabilities |

### API Endpoints Used

| Operation | Endpoint |
|-----------|----------|
| Create Deployment Group | `POST /{project}/_apis/distributedtask/deploymentgroups` |
| Create Environment | `POST /{project}/_apis/pipelines/environments` |
| Set Pipeline Permissions | `PATCH /{project}/_apis/pipelines/pipelinepermissions/environment/{id}` |
| Update DG Agent Tags | `PATCH /{project}/_apis/distributedtask/deploymentgroups/{dgId}/targets/{targetId}` |
| Update Env Agent Tags | `PATCH /{project}/_apis/pipelines/environments/{envId}/providers/virtualmachines/{vmId}` |

---

[← Back to User Guides](README.md)

## Related Documentation

- [Role README](../../roles/azure_devops_agents/README.md) - Quick reference
- [Example Playbooks](../../playbooks/azure_devops_agents/) - Ready-to-use playbooks
- [Variables Reference](../reference/VARIABLES.md) - All collection variables

## External Links

- [Azure DevOps Self-hosted Linux Agents](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent)
- [Deployment Groups](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/deployment-groups/)
- [Environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments)
- [Agent Authentication](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agent-authentication-options)
