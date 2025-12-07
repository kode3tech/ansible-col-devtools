# Part 3: Basic Installation

This guide walks you through deploying your first Azure DevOps self-hosted agent step by step. By the end, you'll have a working agent ready to run pipelines.

## 📋 Table of Contents

- [Overview](#overview)
- [Preparing the Environment](#preparing-the-environment)
- [Creating the Playbook](#creating-the-playbook)
- [Running the Playbook](#running-the-playbook)
- [Verifying the Agent](#verifying-the-agent)
- [Running Your First Pipeline](#running-your-first-pipeline)
- [Next Steps](#next-steps)

## Overview

In this guide, we'll deploy a single self-hosted agent to an Agent Pool. This is the simplest scenario and a great starting point.

### What We'll Create

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Overview                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Azure DevOps                      Target Host                  │
│  ───────────                       ───────────                  │
│                                                                 │
│  Organization: myorg               Server: agent01.example.com  │
│  Agent Pool: Linux-Pool                                         │
│                                    ┌─────────────────────────┐  │
│  ┌─────────────────┐               │ /opt/azure-devops-agents│  │
│  │ Linux-Pool      │◄─────────────►│ └── build-agent/        │  │
│  │                 │   HTTPS       │     └── [agent files]   │  │
│  │ • build-agent   │               │                         │  │
│  └─────────────────┘               │ Service:                │  │
│                                    │ vsts.agent.myorg.       │  │
│                                    │   build-agent.service   │  │
│                                    └─────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Preparing the Environment

### Step 1: Create Project Directory

```bash
mkdir -p azure-agents-deployment
cd azure-agents-deployment
```

### Step 2: Create Inventory File

Create `inventory.ini`:

```ini
# inventory.ini
[agent_servers]
agent01.example.com

[agent_servers:vars]
ansible_user=deploy
ansible_become=true
ansible_python_interpreter=/usr/bin/python3
```

> 💡 **Tip**: Replace `agent01.example.com` with your actual server hostname or IP.

### Step 3: Create Vault File

```bash
ansible-vault create vars/azure_secrets.yml
```

Add your PAT token:

```yaml
---
vault_azure_devops_pat: "your-pat-token-here"
```

### Step 4: Verify Prerequisites

```bash
# Test SSH connection
ansible agent_servers -i inventory.ini -m ping

# Expected output:
# agent01.example.com | SUCCESS => {"ping": "pong"}
```

## Creating the Playbook

### Basic Playbook

Create `install-agent.yml`:

```yaml
---
# install-agent.yml
# Deploy a single Azure DevOps self-hosted agent

- name: Deploy Azure DevOps Agent
  hosts: agent_servers
  become: true

  vars_files:
    - vars/azure_secrets.yml

  vars:
    # Azure DevOps Configuration
    azure_devops_agents_url: "https://dev.azure.com/myorganization"
    azure_devops_agents_pat: "{{ vault_azure_devops_pat }}"

    # Agent Configuration
    azure_devops_agents_list:
      - name: "build-agent"           # Agent name in Azure DevOps
        type: "self-hosted"           # Agent type
        pool: "Linux-Pool"            # Target agent pool
        tags:                         # Agent capabilities/tags
          - "linux"
          - "docker"

  roles:
    - code3tech.devtools.azure_devops_agents
```

### Understanding the Configuration

```yaml
azure_devops_agents_list:
  - name: "build-agent"        # ← How agent appears in Azure DevOps
    type: "self-hosted"        # ← Type: self-hosted, deployment-group, environment
    pool: "Linux-Pool"         # ← Agent pool (must exist in Azure DevOps)
    tags:                      # ← Capabilities shown in Azure DevOps
      - "linux"                #   Used for job routing (demands)
      - "docker"
```

### File Structure

Your project should look like:

```
azure-agents-deployment/
├── inventory.ini
├── install-agent.yml
└── vars/
    └── azure_secrets.yml      # Encrypted with ansible-vault
```

## Running the Playbook

### First Run (Dry Run)

Always test with `--check` first:

```bash
ansible-playbook install-agent.yml \
  -i inventory.ini \
  --ask-vault-pass \
  --check --diff
```

### Production Run

```bash
ansible-playbook install-agent.yml \
  -i inventory.ini \
  --ask-vault-pass
```

### Expected Output

```
PLAY [Deploy Azure DevOps Agent] **********************************************

TASK [Gathering Facts] ********************************************************
ok: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Validate required variables] ***
ok: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Include OS-specific variables] *
ok: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Install required packages] *****
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Create agent user] *************
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Download Azure DevOps agent] ***
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Configure agent] ***************
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Install agent service] *********
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Start agent service] ***********
changed: [agent01.example.com]

TASK [code3tech.devtools.azure_devops_agents : Verify agent services] *********
ok: [agent01.example.com]

PLAY RECAP ********************************************************************
agent01.example.com        : ok=10   changed=6    unreachable=0    failed=0
```

## Verifying the Agent

### On the Target Host

```bash
# SSH to the target host
ssh deploy@agent01.example.com

# Check agent service status
sudo systemctl status vsts.agent.myorganization.build-agent

# Expected output:
# ● vsts.agent.myorganization.build-agent.service
#      Loaded: loaded
#      Active: active (running)
```

### In Azure DevOps

1. Go to **Organization Settings** → **Agent pools**
2. Click on your pool (**Linux-Pool**)
3. Go to **Agents** tab

```
┌────────────────────────────────────────────────────────────────┐
│ Linux-Pool > Agents                                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Name          │ Status │ Version │ Capabilities          │  │
│ ├───────────────┼────────┼─────────┼───────────────────────┤  │
│ │ build-agent   │ 🟢 Online│ 4.264.0 │ linux, docker        │  │
│ └───────────────┴────────┴─────────┴───────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Troubleshooting Verification

If the agent doesn't appear:

```bash
# Check agent logs
sudo journalctl -u vsts.agent.myorganization.build-agent -f

# Check agent configuration
cat /opt/azure-devops-agents/build-agent/.agent | jq .

# Verify network connectivity
curl -I https://dev.azure.com/myorganization
```

## Running Your First Pipeline

### Create a Simple Pipeline

In your Azure DevOps project, create `azure-pipelines.yml`:

```yaml
# azure-pipelines.yml
trigger:
  - main

pool: Linux-Pool    # ← Your agent pool

steps:
  - script: |
      echo "Hello from self-hosted agent!"
      echo "Hostname: $(hostname)"
      echo "User: $(whoami)"
      echo "Working directory: $(pwd)"
    displayName: 'Agent Information'

  - script: |
      echo "Pipeline Variables:"
      echo "Build.BuildId: $(Build.BuildId)"
      echo "Build.SourceBranch: $(Build.SourceBranch)"
    displayName: 'Pipeline Variables'
```

### Run the Pipeline

1. Commit and push `azure-pipelines.yml`
2. Go to **Pipelines** → **New pipeline**
3. Select your repository
4. The pipeline will automatically use your **Linux-Pool**

### Expected Result

```
┌────────────────────────────────────────────────────────────────┐
│ Pipeline Run #1                                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Job: Job                               Status: ✅ Succeeded     │
│                                                                │
│ ├── ✅ Initialize job                  0s                      │
│ ├── ✅ Checkout repository             2s                      │
│ ├── ✅ Agent Information               1s                      │
│ │       Hello from self-hosted agent!                         │
│ │       Hostname: agent01                                     │
│ │       User: azagent                                         │
│ │       Working directory: /opt/azure-devops-agents/          │
│ │                          build-agent/_work/1/s              │
│ ├── ✅ Pipeline Variables              0s                      │
│ └── ✅ Finalize job                    0s                      │
│                                                                │
│ Agent: build-agent                     Pool: Linux-Pool        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Customization Options

### Adding More Tags

```yaml
azure_devops_agents_list:
  - name: "build-agent"
    type: "self-hosted"
    pool: "Linux-Pool"
    tags:
      - "linux"
      - "docker"
      - "nodejs"        # ← Add capabilities
      - "python"
      - "arm64"         # ← Architecture tag
```

### Custom Installation Path

```yaml
vars:
  azure_devops_agents_base_path: "/home/azagent/agents"  # Custom path
```

### Custom Agent User

```yaml
vars:
  azure_devops_agents_user: "builduser"
  azure_devops_agents_group: "buildgroup"
```

## Cleanup (If Needed)

To remove the agent:

```yaml
# remove-agent.yml
---
- name: Remove Azure DevOps Agent
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
        state: absent           # ← Remove agent

  roles:
    - code3tech.devtools.azure_devops_agents
```

Run with:

```bash
ansible-playbook remove-agent.yml -i inventory.ini --ask-vault-pass
```

## Next Steps

Congratulations! You've deployed your first Azure DevOps agent. Now explore:

➡️ **[Part 4: Agent Types](04-agent-types.md)** - Learn about Deployment Groups and Environments.

---

## Quick Reference

### Documentation Map

```
1. Introduction → 2. Prerequisites → [3. Basic Install] → 4. Agent Types → ...
```

### Essential Commands

```bash
# Deploy agent
ansible-playbook install-agent.yml -i inventory.ini --ask-vault-pass

# Check service
systemctl status vsts.agent.*.service

# View logs
journalctl -u vsts.agent.* -f
```

### Files Created on Target Host

```
/opt/azure-devops-agents/
└── build-agent/
    ├── _diag/           # Diagnostic logs
    ├── _work/           # Pipeline workspaces
    ├── bin/             # Agent binaries
    ├── .agent           # Agent configuration
    ├── .credentials     # OAuth credentials
    └── .service         # Service name file
```

---

[← Previous: Prerequisites](02-prerequisites.md) | [Back to Guide Index](README.md) | [Next: Agent Types →](04-agent-types.md)
