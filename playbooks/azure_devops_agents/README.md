# Azure DevOps Agents Playbooks

Example playbooks for the `azure_devops_agents` role.

## Available Playbooks

| Playbook | Description |
|----------|-------------|
| [install-production.yml](install-production.yml) | ⭐ **Recommended** - Production deployment with time sync, vault, and verification |
| [install-single-agent.yml](install-single-agent.yml) | Basic installation of a single self-hosted agent |
| [install-multi-agent.yml](install-multi-agent.yml) | Deploy multiple agents (different types) on the same host |
| [install-deployment-group.yml](install-deployment-group.yml) | Configure deployment group agents for Classic Release pipelines |

## Prerequisites

1. **Azure DevOps Organization** with appropriate permissions
2. **Personal Access Token (PAT)** with required scopes:
   - Agent Pools (Read & manage) - for self-hosted agents
   - Deployment Groups (Read & manage) - for deployment group agents
   - Environment (Read & manage) - for environment agents

3. **Create a vault file** with your PAT:

```bash
# Create encrypted vault
ansible-vault create vars/azure_secrets.yml

# Add content:
vault_azure_devops_pat: "your-pat-token-here"
vault_azure_devops_url: "https://dev.azure.com/your-organization"
```

## Usage

### Production Deployment (Recommended)

The production playbook includes:
- ✅ Time synchronization verification
- ✅ Vault-based credential management
- ✅ Azure DevOps connectivity validation
- ✅ Service verification post-deployment

```bash
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i your_inventory \
  --ask-vault-pass \
  -e "azure_org=your-organization"
```

### Single Agent

```bash
ansible-playbook playbooks/azure_devops_agents/install-single-agent.yml \
  -i your_inventory \
  --ask-vault-pass \
  -e "azure_devops_pool=MyPool"
```

### Multiple Agents

```bash
ansible-playbook playbooks/azure_devops_agents/install-multi-agent.yml \
  -i your_inventory \
  --ask-vault-pass
```

### Deployment Group Agents

```bash
ansible-playbook playbooks/azure_devops_agents/install-deployment-group.yml \
  -i your_inventory \
  --ask-vault-pass \
  -e "azure_devops_project=MyProject" \
  -e "azure_devops_deployment_group=Production"
```

## Advanced Features

### Auto-Create Resources

Enable automatic creation of Deployment Groups and Environments:

```yaml
azure_devops_agents_list:
  - name: "deploy-agent"
    type: "deployment-group"
    project: "MyProject"
    deployment_group: "Production"
    auto_create: true  # Creates if doesn't exist
```

### Open Access for Environments

Allow all pipelines to use an environment without authorization:

```yaml
azure_devops_agents_list:
  - name: "env-agent"
    type: "environment"
    project: "MyProject"
    environment: "development"
    auto_create: true
    open_access: true  # All pipelines can deploy
```

### Remove Agents

Unregister and remove agents cleanly:

```yaml
azure_devops_agents_list:
  - name: "old-agent"
    type: "self-hosted"
    pool: "Legacy-Pool"
    state: absent  # Removes the agent
```

## Customization

Override variables via command line:

```bash
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i your_inventory \
  --ask-vault-pass \
  -e "azure_devops_agents_version=4.264.2" \
  -e "azure_devops_agents_base_path=/opt/agents"
```

## Related Documentation

- [Role Documentation](../../roles/azure_devops_agents/README.md) - Quick reference
- [Complete Guide](../../docs/user-guides/AZURE_DEVOPS_AGENTS_COMPLETE_GUIDE.md) - Comprehensive documentation
- [Variables Reference](../../docs/reference/VARIABLES.md) - All collection variables
- [Azure DevOps Self-hosted Agents](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent)

---

[← Back to Playbooks](../README.md)
