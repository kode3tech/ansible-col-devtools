# Part 5: Advanced Features

This guide covers advanced features of the Azure DevOps agents role, including auto-creation, open access, tag updates, proxy configuration, and maintenance operations.

## 📋 Table of Contents

- [Auto-Create Resources](#auto-create-resources)
- [Open Access for Environments](#open-access-for-environments)
- [Tag Updates via API](#tag-updates-via-api)
- [Agent Removal](#agent-removal)
- [Proxy Configuration](#proxy-configuration)
- [Multi-Agent per Host](#multi-agent-per-host)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Next Steps](#next-steps)

## Auto-Create Resources

The role can automatically create Deployment Groups and Environments if they don't exist.

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    Auto-Create Flow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Check if resource exists (GET API)                         │
│     │                                                           │
│     ├─ YES → Proceed to agent registration                     │
│     │                                                           │
│     └─ NO + auto_create: true                                  │
│        │                                                        │
│        └─► Create resource via REST API (POST)                 │
│            │                                                    │
│            └─► Proceed to agent registration                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Group Auto-Create

```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "NewProject"
    deployment_group: "NewDeploymentGroup"
    auto_create: true    # ✅ Creates if doesn't exist
    tags:
      - "web"
      - "nginx"
```

**What gets created:**

```
Azure DevOps API Call:
POST https://dev.azure.com/{org}/{project}/_apis/distributedtask/deploymentgroups

Response:
{
  "id": 1,
  "name": "NewDeploymentGroup",
  "pool": { ... }
}
```

### Environment Auto-Create

```yaml
azure_devops_agents_list:
  - name: "env-agent"
    type: "environment"
    project: "NewProject"
    environment: "staging"
    auto_create: true    # ✅ Creates if doesn't exist
    tags:
      - "api"
      - "dotnet"
```

**What gets created:**

```
Azure DevOps API Call:
POST https://dev.azure.com/{org}/{project}/_apis/pipelines/environments

Response:
{
  "id": 1,
  "name": "staging",
  "resources": []
}
```

### Best Practices

```yaml
# Development - auto-create for flexibility
- name: "dev-agent"
  type: "environment"
  project: "WebApp"
  environment: "development"
  auto_create: true       # ✅ OK for dev

# Production - explicitly create, document dependencies
- name: "prod-agent"
  type: "environment"
  project: "WebApp"
  environment: "production"
  auto_create: false      # ❌ Create manually with proper approvals
```

## Open Access for Environments

Control which pipelines can deploy to an environment without explicit authorization.

### Understanding Pipeline Permissions

```
┌─────────────────────────────────────────────────────────────────┐
│              Pipeline Permissions for Environments               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  open_access: true                                              │
│  ───────────────────                                            │
│  ┌─────────────┐                                                │
│  │ Environment │◄────── Any pipeline can deploy                │
│  │ development │                                                │
│  └─────────────┘                                                │
│       ▲                                                         │
│       │                                                         │
│  Pipeline A ✅  Pipeline B ✅  Pipeline C ✅                    │
│                                                                 │
│  open_access: false (default)                                   │
│  ────────────────────────────                                   │
│  ┌─────────────┐                                                │
│  │ Environment │◄────── Only authorized pipelines              │
│  │ production  │                                                │
│  └─────────────┘                                                │
│       ▲                                                         │
│       │                                                         │
│  Pipeline A ✅  Pipeline B ❌  Pipeline C ❌                    │
│  (authorized)   (blocked)      (blocked)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
azure_devops_agents_list:
  # Development - open to all
  - name: "dev-agent"
    type: "environment"
    project: "WebApp"
    environment: "development"
    auto_create: true
    open_access: true     # ✅ Any pipeline can deploy

  # Staging - open for testing
  - name: "staging-agent"
    type: "environment"
    project: "WebApp"
    environment: "staging"
    auto_create: true
    open_access: true     # ✅ Any pipeline can deploy

  # Production - restricted
  - name: "prod-agent"
    type: "environment"
    project: "WebApp"
    environment: "production"
    auto_create: true
    open_access: false    # ❌ Requires explicit authorization
```

### How It Works

When `open_access: true`, the role calls:

```
PATCH https://dev.azure.com/{org}/{project}/_apis/pipelines/pipelinepermissions/environment/{id}

Body:
{
  "allPipelines": {
    "authorized": true,
    "authorizedBy": null,
    "authorizedOn": null
  }
}
```

> ⚠️ **Note**: `open_access` is only available for Environment agents, not Deployment Groups.

## Tag Updates via API

Update agent tags without stopping or reconfiguring the agent.

### Use Cases

- Add new capabilities to existing agents
- Update tags for deployment targeting
- Change server classification (e.g., move from staging to production)

### Configuration

```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "WebApp"
    deployment_group: "Production"
    update_tags: true     # ✅ Update tags via API
    tags:
      - "web"
      - "nginx"
      - "new-capability"  # ← Added new tag
```

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tag Update Flow                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Agent is already registered and running                    │
│                                                                 │
│  2. Playbook runs with update_tags: true                       │
│                                                                 │
│  3. Role finds agent ID via API                                │
│     GET /_apis/distributedtask/deploymentgroups/{id}/targets   │
│                                                                 │
│  4. Role updates tags via API                                  │
│     PATCH /_apis/distributedtask/deploymentgroups/{id}/targets/{targetId}
│                                                                 │
│  5. Agent continues running - no restart needed!               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Supported Agent Types

| Agent Type | Tag Update API |
|------------|----------------|
| Self-hosted | ❌ Not supported (use reconfigure) |
| Deployment Group | ✅ Supported |
| Environment | ✅ Supported |

## Agent Removal

Remove agents cleanly with proper unregistration.

### Remove Specific Agents

```yaml
azure_devops_agents_list:
  - name: "old-agent"
    type: "self-hosted"
    pool: "Legacy-Pool"
    state: absent         # ← Remove this agent
```

### Remove All Agents from Host

```yaml
azure_devops_agents_state: "absent"  # Remove ALL agents
```

### Removal Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Removal Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Stop agent service                                         │
│     systemctl stop vsts.agent.*.service                        │
│                                                                 │
│  2. Uninstall service                                          │
│     ./svc.sh uninstall                                         │
│                                                                 │
│  3. Unconfigure agent (unregister from Azure DevOps)          │
│     ./config.sh remove --auth pat --token $PAT                 │
│                                                                 │
│  4. Delete agent directory (if azure_devops_agents_delete_on_remove)
│     rm -rf /opt/azure-devops-agents/agent-name                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Removal Playbook Example

```yaml
---
# remove-agents.yml
- name: Remove Azure DevOps Agents
  hosts: agent_servers
  become: true

  vars_files:
    - vars/azure_secrets.yml

  vars:
    azure_devops_agents_url: "https://dev.azure.com/myorg"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"
    azure_devops_agents_delete_on_remove: true  # Delete directories

    azure_devops_agents_list:
      - name: "old-build-agent"
        type: "self-hosted"
        pool: "Legacy-Pool"
        state: absent

      - name: "old-deploy-agent"
        type: "deployment-group"
        project: "OldProject"
        deployment_group: "Legacy"
        state: absent

  roles:
    - code3tech.devtools.azure_devops_agents
```

## Proxy Configuration

Deploy agents behind a corporate proxy.

### Configuration

```yaml
azure_devops_agents_url: "https://dev.azure.com/myorg"
azure_devops_agents_pat: "{{ vault_pat }}"

# Proxy settings
azure_devops_agents_proxy_url: "http://proxy.corp.example.com:8080"
azure_devops_agents_proxy_user: "{{ vault_proxy_user }}"
azure_devops_agents_proxy_password: "{{ vault_proxy_password }}"
azure_devops_agents_proxy_bypass: "localhost,127.0.0.1,*.internal.example.com"

azure_devops_agents_list:
  - name: "internal-agent"
    type: "self-hosted"
    pool: "Internal-Pool"
```

### How Proxy is Configured

The role creates `.proxy` file in the agent directory:

```
/opt/azure-devops-agents/agent-name/.proxy
```

Content:

```
http://proxy.corp.example.com:8080
```

And `.proxybypass`:

```
localhost,127.0.0.1,*.internal.example.com
```

### Verify Proxy Configuration

```bash
# Check proxy config
cat /opt/azure-devops-agents/agent-name/.proxy

# Test connectivity through proxy
curl -x http://proxy:8080 https://dev.azure.com/myorg
```

## Multi-Agent per Host

Deploy multiple agents on a single server.

### Configuration

```yaml
azure_devops_agents_list:
  # Build agent
  - name: "build-agent"
    type: "self-hosted"
    pool: "Linux-Pool"
    tags: ["docker", "build"]

  # Deploy agent
  - name: "deploy-agent"
    type: "deployment-group"
    project: "WebApp"
    deployment_group: "Production"
    tags: ["web", "deploy"]

  # Environment agent
  - name: "env-agent"
    type: "environment"
    project: "WebApp"
    environment: "production"
    tags: ["api", "env"]
```

### Directory Structure

```
/opt/azure-devops-agents/
├── .downloads/           # Shared download cache
│   └── vsts-agent-linux-x64-4.264.0.tar.gz
├── build-agent/          # Agent 1
│   ├── _work/
│   └── ...
├── deploy-agent/         # Agent 2
│   ├── _work/
│   └── ...
└── env-agent/            # Agent 3
    ├── _work/
    └── ...
```

### Services

```bash
# All services
systemctl list-units 'vsts.agent.*'

# Output:
# vsts.agent.myorg.build-agent.service   loaded active running
# vsts.agent.myorg.deploy-agent.service  loaded active running
# vsts.agent.myorg.env-agent.service     loaded active running
```

### Resource Considerations

| Agents | Recommended RAM | Recommended CPU |
|--------|-----------------|-----------------|
| 1 | 2 GB | 2 cores |
| 2-3 | 4 GB | 4 cores |
| 4+ | 8 GB | 8 cores |

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

The Azure DevOps agent auto-updates by default. To pin a specific version:

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

### Cleanup Work Directories

Pipeline work directories can grow over time:

```bash
# Check disk usage
du -sh /opt/azure-devops-agents/*/work/

# Clean old workspaces (careful!)
# Best done through Azure DevOps pipeline settings
```

### Health Check Playbook

```yaml
---
# health-check.yml
- name: Check Azure DevOps Agent Health
  hosts: agent_servers
  become: true

  tasks:
    - name: Get all agent services
      ansible.builtin.shell: systemctl list-units 'vsts.agent.*' --no-legend
      register: agent_services
      changed_when: false

    - name: Display agent services
      ansible.builtin.debug:
        var: agent_services.stdout_lines

    - name: Check each service is running
      ansible.builtin.systemd:
        name: "{{ item.split()[0] }}"
        state: started
      loop: "{{ agent_services.stdout_lines }}"
      when: agent_services.stdout_lines | length > 0

    - name: Check disk usage
      ansible.builtin.shell: df -h /opt/azure-devops-agents
      register: disk_usage
      changed_when: false

    - name: Display disk usage
      ansible.builtin.debug:
        var: disk_usage.stdout_lines
```

## Next Steps

Learn how to deploy agents in production with best practices:

➡️ **[Part 6: Production Deployment](06-production-deployment.md)** - Templates, inventory patterns, and CI/CD integration.

---

## Quick Reference

### Documentation Map

```
1. Introduction → ... → 4. Agent Types → [5. Advanced Features] → ...
```

### Feature Quick Reference

```yaml
# Auto-create resources
auto_create: true

# Open access for environments
open_access: true

# Update tags via API
update_tags: true

# Remove agent
state: absent

# Proxy configuration
azure_devops_agents_proxy_url: "http://proxy:8080"
```

---

[← Previous: Agent Types](04-agent-types.md) | [Back to Guide Index](README.md) | [Next: Production Deployment →](06-production-deployment.md)
