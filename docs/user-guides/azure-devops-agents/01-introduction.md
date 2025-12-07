# Part 1: Introduction & Architecture

Welcome to the complete guide for deploying Azure DevOps self-hosted agents! This first part covers the foundational concepts you need to understand before deployment.

## 📋 Table of Contents

- [What is Azure DevOps?](#what-is-azure-devops)
- [Understanding Agents](#understanding-agents)
- [Why Self-Hosted Agents?](#why-self-hosted-agents)
- [Agent Architecture](#agent-architecture)
- [Role Overview](#role-overview)
- [Supported Platforms](#supported-platforms)
- [Next Steps](#next-steps)

## What is Azure DevOps?

Azure DevOps is Microsoft's comprehensive DevOps platform that provides:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Azure DevOps Services                        │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────┤
│   Boards    │    Repos    │  Pipelines  │ Test Plans  │ Artifacts  │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────┤
│ Work Items  │    Git      │   CI/CD     │   Testing   │  Packages  │
│   Sprints   │   TFVC      │   Builds    │ Automation  │   Feeds    │
│   Backlogs  │   PRs       │  Releases   │  Exploratory│   NuGet    │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────┘
```

**Pipelines** is where agents come in - they execute your CI/CD workflows.

## Understanding Agents

### What is an Agent?

An agent is a compute resource that runs your pipeline jobs. Think of it as a worker that:

1. **Listens** for jobs from Azure DevOps
2. **Downloads** your source code
3. **Executes** pipeline steps (build, test, deploy)
4. **Reports** results back to Azure DevOps

### Microsoft-Hosted vs Self-Hosted

```
┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
│       Microsoft-Hosted Agents       │    │        Self-Hosted Agents           │
├─────────────────────────────────────┤    ├─────────────────────────────────────┤
│ ✅ No infrastructure to manage      │    │ ✅ Full control over environment    │
│ ✅ Always up-to-date                │    │ ✅ Persistent state between jobs    │
│ ✅ Fresh VM for each job            │    │ ✅ Access to private networks       │
│                                     │    │ ✅ Custom tools and dependencies    │
│ ❌ Limited customization            │    │ ✅ Cost-effective for high volume   │
│ ❌ No private network access        │    │ ✅ No minute limits                 │
│ ❌ Minute limits (free tier)        │    │                                     │
│ ❌ Longer queue times (peak hours)  │    │ ❌ You manage infrastructure        │
│ ❌ No state persistence             │    │ ❌ You handle updates               │
└─────────────────────────────────────┘    └─────────────────────────────────────┘
```

## Why Self-Hosted Agents?

### Use Case 1: Private Network Access

```
┌──────────────────┐         ┌──────────────────┐
│   Azure DevOps   │         │  Your Network    │
│   (Cloud)        │         │  (Private)       │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │  Pipeline  │  │────X────│  │  Database  │  │
│  └────────────┘  │  Can't  │  │  Server    │  │
│                  │  reach  │  └────────────┘  │
│ MS-Hosted Agent  │         │                  │
└──────────────────┘         └──────────────────┘

        ↓ Solution: Self-Hosted Agent ↓

┌──────────────────┐         ┌──────────────────────────────────┐
│   Azure DevOps   │         │  Your Network (Private)          │
│   (Cloud)        │         │                                  │
│                  │         │  ┌────────────┐   ┌────────────┐ │
│  ┌────────────┐  │◄───────►│  │ Self-Hosted│──►│  Database  │ │
│  │  Pipeline  │  │ HTTPS   │  │   Agent    │   │  Server    │ │
│  └────────────┘  │ (443)   │  └────────────┘   └────────────┘ │
│                  │         │                                  │
└──────────────────┘         └──────────────────────────────────┘
```

### Use Case 2: Custom Tools & Dependencies

When your build requires:
- Specific SDK versions
- Licensed software (Oracle, SAP)
- Hardware dongles
- GPU compute
- Proprietary build tools

### Use Case 3: Cost Optimization

| Scenario | Microsoft-Hosted | Self-Hosted |
|----------|-----------------|-------------|
| 100 builds/month | Free tier OK | Overkill |
| 1000 builds/month | ~$150/month | 1 VM: ~$20/month |
| 5000 builds/month | ~$750/month | 2-3 VMs: ~$60/month |

### Use Case 4: Compliance & Security

- Air-gapped environments
- Regulatory requirements (data residency)
- Custom security policies
- Audit logging requirements

## Agent Architecture

### Three Agent Types in Azure DevOps

Azure DevOps supports three distinct agent types, each serving different purposes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Azure DevOps Agent Types                            │
├─────────────────────────┬───────────────────────┬───────────────────────────┤
│     Self-Hosted         │   Deployment Group    │      Environment          │
│     (Agent Pools)       │                       │                           │
├─────────────────────────┼───────────────────────┼───────────────────────────┤
│ • Organization scope    │ • Project scope       │ • Project scope           │
│ • All pipeline types    │ • Classic Release     │ • YAML pipelines          │
│ • Build & Release       │ • Multi-stage deploy  │ • Modern approach         │
│ • Shared across projects│ • Target servers      │ • K8s-style deployments   │
├─────────────────────────┼───────────────────────┼───────────────────────────┤
│ Location:               │ Location:             │ Location:                 │
│ Org Settings →          │ Project → Pipelines → │ Project → Pipelines →     │
│ Agent Pools             │ Deployment Groups     │ Environments              │
└─────────────────────────┴───────────────────────┴───────────────────────────┘
```

### Directory Structure

Each agent runs in its own isolated directory:

```
/opt/azure-devops-agents/              # Base path (configurable)
├── .downloads/                        # Shared agent packages (cached)
│   └── vsts-agent-linux-x64-4.X.X.tar.gz
│
├── build-agent-01/                    # Self-hosted agent
│   ├── config.sh                      # Configuration script
│   ├── run.sh                         # Manual run script
│   ├── svc.sh                         # Service management
│   ├── .credentials                   # OAuth credentials (encrypted)
│   ├── .agent                         # Agent configuration JSON
│   ├── .service                       # Systemd service name
│   ├── bin/                           # Agent binaries
│   ├── externals/                     # Node.js, etc.
│   └── _work/                         # Pipeline work directory
│       ├── 1/                         # Job 1 workspace
│       │   ├── s/                     # Source code
│       │   ├── a/                     # Artifacts
│       │   └── b/                     # Binaries
│       └── 2/                         # Job 2 workspace
│
├── deploy-agent-01/                   # Deployment group agent
│   └── ...
│
└── env-agent-01/                      # Environment agent
    └── ...
```

### Systemd Service Integration

Each agent runs as an independent systemd service:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Systemd Services                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  vsts.agent.myorg.build-agent-01.service     ← Self-hosted       │
│  ├── User: azagent                                               │
│  ├── WorkingDirectory: /opt/azure-devops-agents/build-agent-01   │
│  └── ExecStart: ./runsvc.sh                                      │
│                                                                  │
│  vsts.agent.myorg.deploy-agent-01.service    ← Deployment Group  │
│  ├── User: azagent                                               │
│  ├── WorkingDirectory: /opt/azure-devops-agents/deploy-agent-01  │
│  └── ExecStart: ./runsvc.sh                                      │
│                                                                  │
│  vsts.agent.myorg.env-agent-01.service       ← Environment       │
│  ├── User: azagent                                               │
│  ├── WorkingDirectory: /opt/azure-devops-agents/env-agent-01     │
│  └── ExecStart: ./runsvc.sh                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Communication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Communication Flow                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  Azure DevOps (Cloud)                    Your Infrastructure
  ════════════════════                    ═══════════════════════

  ┌─────────────────┐                     ┌─────────────────────┐
  │  Pipeline Job   │                     │  Self-Hosted Agent  │
  │  Queue          │◄────── HTTPS ──────►│                     │
  └─────────────────┘     (Outbound       │  ┌───────────────┐  │
                          from agent)     │  │ Agent Process │  │
  ┌─────────────────┐                     │  │               │  │
  │  Source Code    │◄────── HTTPS ───────│  │  • Poll jobs  │  │
  │  (Repos)        │                     │  │  • Run tasks  │  │
  └─────────────────┘                     │  │  • Upload logs│  │
                                          │  └───────────────┘  │
  ┌─────────────────┐                     │                     │
  │  Artifacts      │◄────── HTTPS ───────│  Firewall: Only     │
  │  Storage        │                     │  OUTBOUND 443       │
  └─────────────────┘                     └─────────────────────┘

  Note: Agent initiates ALL connections (outbound only)
        No inbound ports required!
```

## Role Overview

### What This Role Does

The `code3tech.devtools.azure_devops_agents` role automates:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Validation    │───►│  Prerequisites  │───►│  Download Agent │
│                 │    │  (packages)     │    │  (cached)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auto-Create    │───►│  Configure &    │───►│  Install        │
│  Resources      │    │  Register       │    │  Service        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
         ┌────────────────────────────────────────────┘
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Set Pipeline   │───►│  Verify         │
│  Permissions    │    │  Services       │
└─────────────────┘    └─────────────────┘
```

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Agent** | Deploy N agents on the same host with isolated directories |
| **Three Agent Types** | Self-hosted, Deployment Group, and Environment agents |
| **Auto-Create** | Automatically create Deployment Groups and Environments via API |
| **Open Access** | Configure pipeline permissions for environments |
| **Service Verification** | Ensures all services are enabled and running |
| **Agent Removal** | Clean unregistration and removal of agents |
| **Tag Updates** | Update agent tags via REST API without reconfiguration |
| **Input Validation** | Comprehensive validation with clear error messages |

## Supported Platforms

### Operating Systems

| Distribution | Versions | Status |
|--------------|----------|--------|
| **Ubuntu** | 22.04, 24.04, 25.04 | ✅ Tested |
| **Debian** | 11, 12, 13 | ✅ Tested |
| **RHEL/Rocky/Alma** | 9, 10 | ✅ Tested |

### Azure DevOps Versions

| Version | Support |
|---------|---------|
| Azure DevOps Services (cloud) | ✅ Full |
| Azure DevOps Server 2022 | ✅ Full |
| Azure DevOps Server 2020 | ✅ Full |
| TFS 2018 | ⚠️ Limited |

### Requirements

- **Ansible**: >= 2.15
- **Python**: >= 3.9 (on control node)
- **Network**: Outbound HTTPS (443) to Azure DevOps
- **Privileges**: Root or sudo on target hosts

## Next Steps

Now that you understand the concepts, proceed to:

➡️ **[Part 2: Prerequisites & Setup](02-prerequisites.md)** - Prepare your environment with PAT tokens and Ansible configuration.

---

## Quick Reference

### Documentation Map

```
You are here: [1. Introduction] → 2. Prerequisites → 3. Basic Install → ...
```

### Key Terminology

| Term | Definition |
|------|------------|
| **Agent** | Process that runs pipeline jobs |
| **Agent Pool** | Collection of self-hosted agents (org-level) |
| **Deployment Group** | Collection of target servers (project-level, Classic) |
| **Environment** | Collection of target resources (project-level, YAML) |
| **PAT** | Personal Access Token for authentication |

---

[← Back to Guide Index](README.md) | [Next: Prerequisites →](02-prerequisites.md)
