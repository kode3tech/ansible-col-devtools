# Part 2: Prerequisites & Setup

Before deploying Azure DevOps agents, you need to prepare your environment. This guide walks you through all the requirements step by step.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Azure DevOps Requirements](#azure-devops-requirements)
- [Creating a Personal Access Token](#creating-a-personal-access-token)
- [Installing the Ansible Collection](#installing-the-ansible-collection)
- [Creating Vault for Secrets](#creating-vault-for-secrets)
- [Verification](#verification)
- [Next Steps](#next-steps)

## System Requirements

### Target Hosts (Where Agents Run)

| Requirement | Specification |
|-------------|---------------|
| **OS** | Ubuntu 22.04+, Debian 11+, RHEL 9+ |
| **CPU** | 2+ cores recommended |
| **RAM** | 2GB minimum, 4GB+ recommended |
| **Disk** | 10GB minimum for agent + workspace |
| **Network** | Outbound HTTPS (443) to Azure DevOps |

### Required Packages (Auto-Installed)

The role automatically installs these packages:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Required Packages                             │
├─────────────────┬───────────────────────────────────────────────┤
│ Package         │ Purpose                                       │
├─────────────────┼───────────────────────────────────────────────┤
│ curl            │ Download agent package                        │
│ tar             │ Extract agent archive                         │
│ jq              │ JSON parsing for API responses                │
│ libicu          │ .NET Core ICU library                         │
│ git             │ Source code checkout                          │
└─────────────────┴───────────────────────────────────────────────┘
```

### Control Node (Where Ansible Runs)

| Requirement | Version |
|-------------|---------|
| **Ansible** | >= 2.15 |
| **Python** | >= 3.9 |

## Azure DevOps Requirements

### 1. Organization

You need an Azure DevOps organization. If you don't have one:

1. Go to https://dev.azure.com
2. Sign in with your Microsoft account
3. Create a new organization

Your organization URL will be: `https://dev.azure.com/YOUR_ORG_NAME`

### 2. Resources (Pre-existing or Auto-Created)

Depending on agent type, you need:

| Agent Type | Required Resource | Can Auto-Create? |
|------------|-------------------|------------------|
| Self-hosted | Agent Pool | ❌ Create manually |
| Deployment Group | Deployment Group | ✅ Yes |
| Environment | Environment | ✅ Yes |

### Creating an Agent Pool (For Self-Hosted Agents)

```
Azure DevOps → Organization Settings → Agent pools → Add pool

┌────────────────────────────────────────────────────────────────┐
│ Add agent pool                                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Pool type: ● Self-hosted  ○ Azure virtual machine scale set   │
│                                                                │
│ Name: [ Linux-Pool                            ]                │
│                                                                │
│ Description: [ Linux build agents             ]                │
│                                                                │
│ ☑ Grant access permission to all pipelines                    │
│                                                                │
│ ☑ Auto-provision this agent pool in all projects              │
│                                                                │
│                               [Cancel]  [Create]               │
└────────────────────────────────────────────────────────────────┘
```

## Creating a Personal Access Token

A PAT (Personal Access Token) authenticates the agent with Azure DevOps.

### Step-by-Step Guide

**Step 1: Access Token Settings**

```
Azure DevOps → User Settings (top right) → Personal Access Tokens
```

**Step 2: Create New Token**

Click "New Token" and fill in:

```
┌────────────────────────────────────────────────────────────────┐
│ Create a new personal access token                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Name: [ ansible-agent-deployment              ]                │
│                                                                │
│ Organization: [ My Organization ▼ ]                            │
│               ○ All accessible organizations                   │
│               ● My Organization                                │
│                                                                │
│ Expiration: [ 90 days ▼ ]                                     │
│             ○ 30 days                                          │
│             ● 90 days                                          │
│             ○ 180 days                                         │
│             ○ 1 year                                           │
│             ○ Custom defined                                   │
│                                                                │
│ Scopes: ○ Full access                                         │
│         ● Custom defined                                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Step 3: Select Scopes**

Choose scopes based on the agent types you'll deploy:

```
┌────────────────────────────────────────────────────────────────┐
│ Scopes (Custom defined)                                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ▼ Agent Pools                                                  │
│   ☑ Read & manage                  ← For self-hosted agents   │
│                                                                │
│ ▼ Deployment Groups                                            │
│   ☑ Read & manage                  ← For deployment groups    │
│                                                                │
│ ▼ Environment                                                  │
│   ☑ Read & manage                  ← For environment agents   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### PAT Scopes Reference

| Agent Type | Required Scope | Permission Level |
|------------|----------------|------------------|
| Self-hosted | Agent Pools | Read & manage |
| Deployment Group | Deployment Groups | Read & manage |
| Environment | Environment | Read & manage |
| All types | All above | Read & manage |

> ⚠️ **Security Tip**: Create separate PATs for different purposes. Don't use a full-access token.

**Step 4: Copy and Save Token**

```
┌────────────────────────────────────────────────────────────────┐
│ Success!                                                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Copy the token now. You won't be able to see it again!         │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 7g3h5k2m8n9p1q4r6s0t2u5v7w9x1y3z5a7b9c1d3e5f7g9h1j3k5l │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                    [Copy]      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

> 🔐 **IMPORTANT**: Store this token securely! You cannot view it again after closing this dialog.

## Installing the Ansible Collection

### Method 1: From Ansible Galaxy (Recommended)

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Verify installation
ansible-galaxy collection list | grep code3tech
```

### Method 2: From requirements.yml

Create `requirements.yml`:

```yaml
---
collections:
  - name: code3tech.devtools
    version: ">=1.1.0"
```

Install:

```bash
ansible-galaxy collection install -r requirements.yml
```

### Verify Installation

```bash
# List installed collections
ansible-galaxy collection list

# Expected output includes:
# Collection          Version
# ------------------- -------
# code3tech.devtools  1.2.0
```

## Creating Vault for Secrets

Never store PAT tokens in plain text! Use Ansible Vault.

### Step 1: Create Vault File

```bash
# Create encrypted vault file
ansible-vault create vars/azure_secrets.yml
```

### Step 2: Add Secrets

When the editor opens, add:

```yaml
---
# Azure DevOps Personal Access Token
# Scopes: Agent Pools, Deployment Groups, Environment (Read & manage)
vault_azure_devops_pat: "your-pat-token-here"

# Optional: Proxy credentials (if behind corporate proxy)
# vault_proxy_user: "domain\\username"
# vault_proxy_password: "proxy-password"
```

### Step 3: Create Vault Password File (Optional)

For CI/CD automation:

```bash
# Create password file
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore
echo ".vault_pass" >> .gitignore
```

### Using Vault in Playbooks

```bash
# Interactive password prompt
ansible-playbook playbook.yml --ask-vault-pass

# Using password file
ansible-playbook playbook.yml --vault-password-file .vault_pass

# Using environment variable
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
ansible-playbook playbook.yml
```

## Verification

### Verify Collection Installation

```bash
ansible-galaxy collection list code3tech.devtools
```

### Verify Vault Access

```bash
# View vault contents (prompts for password)
ansible-vault view vars/azure_secrets.yml
```

### Test Azure DevOps Connectivity

```bash
# Test PAT authentication
curl -s -u ":YOUR_PAT" \
  "https://dev.azure.com/YOUR_ORG/_apis/projects?api-version=7.0" | jq .
```

Expected output:

```json
{
  "count": 2,
  "value": [
    {
      "id": "...",
      "name": "MyProject",
      "state": "wellFormed"
    }
  ]
}
```

### Verify Target Host Connectivity

```bash
# Test SSH connection
ansible all -i "target-host.example.com," -m ping

# Expected output:
# target-host.example.com | SUCCESS => {
#     "ping": "pong"
# }
```

## Checklist

Before proceeding, verify:

- [ ] Target hosts meet system requirements
- [ ] Azure DevOps organization is accessible
- [ ] Agent Pool created (for self-hosted agents)
- [ ] PAT token created with correct scopes
- [ ] Ansible collection installed
- [ ] Vault file created with PAT token
- [ ] Network connectivity verified

## Next Steps

Your environment is ready! Proceed to:

➡️ **[Part 3: Basic Installation](03-basic-installation.md)** - Deploy your first agent step by step.

---

## Quick Reference

### Documentation Map

```
1. Introduction → [2. Prerequisites] → 3. Basic Install → ...
```

### Essential Commands

```bash
# Install collection
ansible-galaxy collection install code3tech.devtools

# Create vault
ansible-vault create vars/azure_secrets.yml

# Test Azure DevOps API
curl -u ":YOUR_PAT" "https://dev.azure.com/ORG/_apis/projects?api-version=7.0"
```

---

[← Previous: Introduction](01-introduction.md) | [Back to Guide Index](README.md) | [Next: Basic Installation →](03-basic-installation.md)
