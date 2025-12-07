# Part 7: Security Best Practices

Security is critical when deploying Azure DevOps agents. This guide covers PAT token management, agent isolation, network security, and hardening recommendations.

## 📋 Table of Contents

- [Security Overview](#security-overview)
- [PAT Token Management](#pat-token-management)
- [Agent User Isolation](#agent-user-isolation)
- [Network Security](#network-security)
- [Secret Management in Pipelines](#secret-management-in-pipelines)
- [Hardening Recommendations](#hardening-recommendations)
- [Security Checklist](#security-checklist)
- [Next Steps](#next-steps)

## Security Overview

### Attack Surface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Azure DevOps Agent Attack Surface                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                         ┌─────────────────┐           │
│  │ Ansible Control │                         │ Azure DevOps    │           │
│  │ Node            │                         │ (Cloud)         │           │
│  └────────┬────────┘                         └────────┬────────┘           │
│           │                                           │                     │
│           │ 1. PAT in transit                        │                     │
│           │ 2. SSH keys                              │                     │
│           │ 3. Vault password                        │ 4. Agent comms      │
│           │                                           │                     │
│           ▼                                           ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │                    Target Host                               │           │
│  │  ┌─────────────────────────────────────────────────────┐    │           │
│  │  │ Agent Process                                        │    │           │
│  │  │ • 5. Credentials on disk (.credentials)             │    │           │
│  │  │ • 6. Pipeline secrets in memory                     │    │           │
│  │  │ • 7. Source code access                             │    │           │
│  │  │ • 8. Network access (internal resources)            │    │           │
│  │  └─────────────────────────────────────────────────────┘    │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
│  Security Controls:                                                         │
│  ═══════════════════                                                        │
│  1. Ansible Vault (encrypted at rest)                                      │
│  2. SSH key authentication                                                  │
│  3. Vault password protection                                               │
│  4. TLS 1.2+ (encrypted in transit)                                        │
│  5. File permissions (600)                                                  │
│  6. Process isolation                                                       │
│  7. Repository permissions                                                  │
│  8. Network segmentation                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## PAT Token Management

### Never Store PATs in Plain Text

```yaml
# ❌ WRONG - Never do this!
azure_devops_agents_pat: "7g3h5k2m8n9p1q4r6s0t2u5v7w9x1y3z"

# ✅ CORRECT - Use Ansible Vault
azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"
```

### Creating Encrypted Vault

```bash
# Create new vault file
ansible-vault create vars/azure_secrets.yml

# Edit existing vault
ansible-vault edit vars/azure_secrets.yml

# View vault contents
ansible-vault view vars/azure_secrets.yml

# Change vault password
ansible-vault rekey vars/azure_secrets.yml
```

### Vault File Structure

```yaml
# vars/azure_secrets.yml (encrypted)
---
# Azure DevOps PAT
# Scopes: Agent Pools, Deployment Groups, Environment (Read & manage)
# Created: 2024-01-15
# Expires: 2024-04-15
vault_azure_devops_pat: "your-pat-token-here"

# Optional: Proxy credentials
vault_proxy_user: "domain\\username"
vault_proxy_password: "proxy-password"
```

### Vault Password Management

**For interactive use:**

```bash
# Prompt for password
ansible-playbook playbook.yml --ask-vault-pass
```

**For CI/CD automation:**

```bash
# Create password file (secure permissions!)
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore
echo ".vault_pass" >> .gitignore

# Use in playbook
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

**Using environment variable:**

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook playbook.yml
```

### PAT Scope Minimization

Create dedicated PATs with minimal scope:

```
┌────────────────────────────────────────────────────────────────┐
│ PAT Scope Recommendations                                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Deployment Type        │ Recommended Scopes                   │
│ ───────────────────────┼────────────────────────────────────   │
│ Build agents only      │ Agent Pools (Read & manage)          │
│ Deployment groups only │ Deployment Groups (Read & manage)    │
│ Environments only      │ Environment (Read & manage)          │
│ All types              │ All above scopes                     │
│                                                                │
│ ⚠️  Avoid "Full access" - always use custom scopes            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### PAT Rotation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PAT Rotation Process                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Create New PAT                2. Update Vault                          │
│     ↓                                ↓                                      │
│  Azure DevOps →                   ansible-vault edit                        │
│  Personal Access Tokens →         vars/azure_secrets.yml                    │
│  New Token                                                                  │
│                                                                             │
│  3. Reconfigure Agents            4. Verify                                │
│     ↓                                ↓                                      │
│  ansible-playbook                 Check Azure DevOps →                      │
│  install-agents.yml               Agent pools/environments                  │
│  --ask-vault-pass                                                           │
│                                                                             │
│  5. Revoke Old PAT                                                         │
│     ↓                                                                       │
│  Azure DevOps →                                                             │
│  Personal Access Tokens →                                                   │
│  Revoke                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### PAT Expiration Monitoring

```yaml
# Document PAT expiration in vault
---
# PAT Information
# Token Name: ansible-agent-deployment
# Created: 2024-01-15
# Expires: 2024-04-15
# Scopes: Agent Pools, Deployment Groups, Environment
# Owner: devops-team@example.com
vault_azure_devops_pat: "your-token"
```

Set calendar reminders for PAT rotation before expiration!

## Agent User Isolation

### Dedicated Agent User

The role creates a dedicated `azagent` user:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent User Configuration                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User: azagent                                                  │
│  ├── Type: System user                                          │
│  ├── Shell: /usr/sbin/nologin (no interactive login)           │
│  ├── Home: /opt/azure-devops-agents                             │
│  └── Groups: azagent only                                       │
│                                                                 │
│  Ownership:                                                     │
│  ├── /opt/azure-devops-agents/     → azagent:azagent           │
│  ├── Agent binaries                → azagent:azagent           │
│  └── Work directories              → azagent:azagent           │
│                                                                 │
│  Cannot:                                                        │
│  ├── Login interactively (SSH)                                  │
│  ├── Run as root (Azure DevOps restriction)                     │
│  ├── Access other user directories                              │
│  └── Modify system files                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Custom Agent User

```yaml
# Use custom user/group
azure_devops_agents_user: "builduser"
azure_devops_agents_group: "buildgroup"
azure_devops_agents_create_user: true  # Create if doesn't exist
```

### File Permissions

```bash
# Agent directory permissions
drwxr-x--- azagent azagent /opt/azure-devops-agents/

# Sensitive files
-rw------- azagent azagent .credentials
-rw------- azagent azagent .agent

# Work directories
drwxr-x--- azagent azagent _work/
```

### Adding Agent to Groups (If Needed)

For Docker access:

```yaml
# Add agent user to docker group
- name: Add agent user to docker group
  ansible.builtin.user:
    name: "{{ azure_devops_agents_user }}"
    groups: docker
    append: true
```

> ⚠️ **Warning**: Adding to docker group grants root-equivalent access. Use with caution.

## Network Security

### Outbound Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│               Required Outbound Connections                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Destination                      │ Port │ Purpose              │
│  ─────────────────────────────────┼──────┼──────────────────────│
│  dev.azure.com                    │ 443  │ Azure DevOps API     │
│  *.dev.azure.com                  │ 443  │ Azure DevOps API     │
│  vstsagentpackage.azureedge.net   │ 443  │ Agent packages       │
│  download.agent.dev.azure.com     │ 443  │ Agent downloads      │
│  login.microsoftonline.com        │ 443  │ Authentication       │
│  management.azure.com             │ 443  │ Azure Management     │
│                                                                 │
│  Optional (based on usage):                                     │
│  ─────────────────────────────────┼──────┼──────────────────────│
│  github.com                       │ 443  │ GitHub repos         │
│  *.blob.core.windows.net          │ 443  │ Azure Storage        │
│  *.docker.io                      │ 443  │ Docker Hub           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Firewall Configuration

```bash
# UFW (Ubuntu/Debian)
# Allow outbound HTTPS (typically already allowed)
sudo ufw allow out 443/tcp

# iptables
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
```

### No Inbound Ports Required

```
┌─────────────────────────────────────────────────────────────────┐
│                    Communication Model                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Azure DevOps (Cloud)              Agent (On-Premises)          │
│                                                                 │
│  ┌─────────────────┐               ┌─────────────────┐          │
│  │ Job Queue       │◄──────────────│ Agent polls for │          │
│  │                 │   HTTPS (443) │ jobs (outbound) │          │
│  │                 │   Long-poll   │                 │          │
│  └─────────────────┘               └─────────────────┘          │
│                                                                 │
│  ✅ Agent initiates ALL connections (outbound only)            │
│  ✅ No inbound ports needed                                     │
│  ✅ Works behind NAT/firewall                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Network Segmentation

```
┌─────────────────────────────────────────────────────────────────┐
│              Recommended Network Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ DMZ / Agent Network                                      │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ Build Agent  │  │ Build Agent  │  │ Deploy Agent │   │   │
│  │  │ (build-01)   │  │ (build-02)   │  │ (deploy-01)  │   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │   │
│  │         │                 │                 │            │   │
│  └─────────┼─────────────────┼─────────────────┼────────────┘   │
│            │                 │                 │                 │
│            │ ← Only HTTPS outbound to internet                  │
│            ▼                 ▼                 ▼                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Internal Network                                         │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ Database     │  │ Internal     │  │ Artifact     │   │   │
│  │  │ Server       │  │ Registry     │  │ Storage      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Secret Management in Pipelines

### Never Hardcode Secrets

```yaml
# ❌ WRONG - Never do this in pipelines!
steps:
  - script: |
      curl -u admin:P@ssw0rd123 http://internal-api/deploy

# ✅ CORRECT - Use variable groups
variables:
  - group: production-secrets

steps:
  - script: |
      curl -u $(API_USER):$(API_PASSWORD) http://internal-api/deploy
    env:
      API_PASSWORD: $(apiPassword)  # Secret variable
```

### Variable Groups with Azure Key Vault

```yaml
# azure-pipelines.yml
variables:
  - group: production-secrets      # Regular variable group
  - group: keyvault-production     # Linked to Azure Key Vault

steps:
  - script: |
      echo "Using secret from Key Vault"
    env:
      DB_PASSWORD: $(database-password)  # From Key Vault
```

### Service Connections

Use service connections instead of credentials in pipelines:

```yaml
# Use Azure service connection
- task: AzureCLI@2
  inputs:
    azureSubscription: 'Production-Azure'  # Service connection
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: 'az account show'
```

## Hardening Recommendations

### 1. Limit Agent Capabilities

```yaml
# Only install what's needed
azure_devops_agents_list:
  - name: "minimal-agent"
    type: "self-hosted"
    pool: "Minimal-Pool"
    tags:
      - "basic"
    # Don't add docker, sudo, etc. unless needed
```

### 2. Use Separate Agents for Sensitive Workloads

```
Production Deployments → Dedicated "production" pool
Development Builds     → Shared "development" pool
Security Scanning      → Isolated "security" pool
```

### 3. Regular Updates

```yaml
# Pin to latest version (auto-update enabled by default)
azure_devops_agents_version: ""  # Empty = latest

# Or pin to specific version for stability
azure_devops_agents_version: "4.264.2"
```

### 4. Audit Logging

```bash
# Enable audit logging
sudo auditctl -w /opt/azure-devops-agents -p wa -k azure-agents

# View audit logs
sudo ausearch -k azure-agents
```

### 5. SELinux/AppArmor

```bash
# SELinux (RHEL/CentOS)
# Agent runs in unconfined context by default
# Custom policies can be created for tighter control

# AppArmor (Ubuntu/Debian)
# Consider creating AppArmor profile for agent process
```

### 6. Resource Limits

```yaml
# Create systemd override for resource limits
- name: Create systemd override directory
  ansible.builtin.file:
    path: /etc/systemd/system/vsts.agent.{{ org }}.{{ agent.name }}.service.d
    state: directory

- name: Set resource limits
  ansible.builtin.copy:
    content: |
      [Service]
      MemoryMax=4G
      CPUQuota=200%
    dest: /etc/systemd/system/vsts.agent.{{ org }}.{{ agent.name }}.service.d/limits.conf
```

## Security Checklist

### Pre-Deployment

- [ ] PAT stored in Ansible Vault (not plain text)
- [ ] PAT has minimal required scopes
- [ ] PAT expiration documented and monitored
- [ ] Vault password stored securely
- [ ] SSH keys use strong encryption (ed25519)
- [ ] Target hosts updated and patched

### Agent Configuration

- [ ] Dedicated agent user (non-root)
- [ ] Agent user has no interactive shell
- [ ] Agent directories have proper permissions
- [ ] Docker group membership reviewed (if applicable)
- [ ] No unnecessary sudo permissions

### Network Security

- [ ] Outbound-only firewall rules
- [ ] No inbound ports exposed
- [ ] Network segmentation in place
- [ ] Proxy configured (if required)
- [ ] TLS 1.2+ enforced

### Pipeline Security

- [ ] Secrets in variable groups (not YAML)
- [ ] Service connections for external access
- [ ] Branch policies on main/production
- [ ] Approval gates for production environments
- [ ] Audit logging enabled

### Ongoing Maintenance

- [ ] PAT rotation schedule established
- [ ] Regular security updates applied
- [ ] Agent logs reviewed periodically
- [ ] Access reviews conducted
- [ ] Incident response plan documented

## Next Steps

Learn to troubleshoot common issues:

➡️ **[Part 8: Troubleshooting](08-troubleshooting.md)** - Common errors, diagnostics, and reference tables.

---

## Quick Reference

### Documentation Map

```
... → 6. Production Deployment → [7. Security] → 8. Troubleshooting
```

### Security Commands

```bash
# Create vault
ansible-vault create vars/azure_secrets.yml

# Edit vault
ansible-vault edit vars/azure_secrets.yml

# Check file permissions
ls -la /opt/azure-devops-agents/

# View agent user
id azagent

# Check service status
systemctl status vsts.agent.*
```

---

[← Previous: Production Deployment](06-production-deployment.md) | [Back to Guide Index](README.md) | [Next: Troubleshooting →](08-troubleshooting.md)
