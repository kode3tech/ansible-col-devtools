# Part 4: Agent Types

Azure DevOps supports three distinct agent types, each designed for different deployment scenarios. This guide explains when and how to use each type.

## 📋 Table of Contents

- [Overview](#overview)
- [Self-Hosted Agents (Agent Pools)](#self-hosted-agents-agent-pools)
- [Deployment Group Agents](#deployment-group-agents)
- [Environment Agents](#environment-agents)
- [Comparison Table](#comparison-table)
- [Choosing the Right Type](#choosing-the-right-type)
- [Next Steps](#next-steps)

## Overview

### The Three Agent Types

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

## Self-Hosted Agents (Agent Pools)

### What Are They?

Self-hosted agents are general-purpose build agents that belong to an **Agent Pool** at the organization level. They can be shared across all projects.

### Use Cases

- ✅ CI/CD pipelines (build, test, package)
- ✅ Multi-project shared agents
- ✅ General-purpose automation
- ✅ Organization-wide resource pooling

### Configuration

```yaml
azure_devops_agents_list:
  - name: "build-agent-01"
    type: "self-hosted"           # Agent type
    pool: "Linux-Pool"            # Agent pool name (must exist)
    replace: true                 # Replace existing agent with same name
    work_dir: "_work"             # Work directory name (default: _work)
    tags:                         # Agent capabilities
      - "docker"
      - "nodejs"
      - "linux"
```

### Where They Appear in Azure DevOps

```
Organization Settings → Agent Pools → [Your Pool] → Agents

┌────────────────────────────────────────────────────────────────┐
│ Organization Settings                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Pipelines                                                     │
│  ├── Agent pools          ← Self-hosted agents are here       │
│  │   ├── Azure Pipelines    (Microsoft-hosted)                │
│  │   ├── Default            (Self-hosted)                     │
│  │   └── Linux-Pool         (Self-hosted) ← Your pool         │
│  │       └── Agents                                           │
│  │           └── build-agent-01  🟢 Online                    │
│  └── ...                                                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Example Pipeline (YAML)

```yaml
# azure-pipelines.yml
trigger:
  - main

pool: Linux-Pool    # Reference the agent pool

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - script: echo "Building on $(Agent.MachineName)"
```

### Example Pipeline (Classic)

```
Pipeline → Agent pool: Linux-Pool
```

## Deployment Group Agents

### What Are They?

Deployment Group agents are **target servers** for Classic Release pipelines. They're project-scoped and designed for multi-machine deployments.

### Use Cases

- ✅ Classic Release pipelines
- ✅ Multi-stage deployment targeting
- ✅ Rolling deployments across multiple servers
- ✅ IIS, Windows Services, or Linux service deployments

### Configuration

```yaml
azure_devops_agents_list:
  - name: "web-server-01"
    type: "deployment-group"      # Agent type
    project: "WebApplication"     # Azure DevOps project name
    deployment_group: "Production-Web"  # Deployment group name
    auto_create: true             # Create group if doesn't exist
    replace: true                 # Replace existing agent
    tags:                         # Server tags for targeting
      - "web"
      - "nginx"
      - "production"
```

### Where They Appear in Azure DevOps

```
Project → Pipelines → Deployment Groups → [Your Group] → Targets

┌────────────────────────────────────────────────────────────────┐
│ WebApplication (Project)                                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Pipelines                                                     │
│  ├── Pipelines                                                 │
│  ├── Releases                                                  │
│  ├── Library                                                   │
│  └── Deployment groups       ← Deployment group agents here   │
│      └── Production-Web                                        │
│          └── Targets                                           │
│              ├── web-server-01  🟢 Online  [web, nginx, prod]  │
│              └── web-server-02  🟢 Online  [web, nginx, prod]  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Auto-Create Feature

The role can automatically create Deployment Groups:

```yaml
azure_devops_agents_list:
  - name: "web-server"
    type: "deployment-group"
    project: "MyProject"
    deployment_group: "NewDeploymentGroup"
    auto_create: true    # ✅ Creates via REST API if doesn't exist
```

### Example Classic Release Pipeline

```
Release Pipeline → Stages:
├── Dev
│   └── Agent job: Linux-Pool
├── Staging
│   └── Deployment group job: Staging-Web
└── Production
    └── Deployment group job: Production-Web
        └── Target filter: web, production
```

### Rolling Deployment

Classic Releases support rolling deployments across Deployment Groups:

```yaml
# Multiple servers in the group
azure_devops_agents_list:
  - name: "web-server-01"
    type: "deployment-group"
    project: "WebApp"
    deployment_group: "Production"
    tags: ["web", "zone-a"]

  - name: "web-server-02"
    type: "deployment-group"
    project: "WebApp"
    deployment_group: "Production"
    tags: ["web", "zone-b"]
```

## Environment Agents

### What Are They?

Environment agents are target VMs for **YAML multi-stage pipelines**. They're the modern approach, replacing Classic Release Deployment Groups.

### Use Cases

- ✅ YAML multi-stage pipelines (recommended)
- ✅ Kubernetes-style deployment strategies
- ✅ Environment-based approvals and checks
- ✅ Modern GitOps workflows

### Configuration

```yaml
azure_devops_agents_list:
  - name: "api-server-01"
    type: "environment"           # Agent type
    project: "WebApplication"     # Azure DevOps project name
    environment: "production"     # Environment name
    auto_create: true             # Create environment if doesn't exist
    open_access: true             # Allow all pipelines to use this env
    replace: true                 # Replace existing agent
    tags:                         # VM resource tags
      - "api"
      - "dotnet"
      - "production"
```

### Where They Appear in Azure DevOps

```
Project → Pipelines → Environments → [Your Environment] → Resources

┌────────────────────────────────────────────────────────────────┐
│ WebApplication (Project)                                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Pipelines                                                     │
│  ├── Pipelines                                                 │
│  ├── Environments            ← Environment agents here        │
│  │   ├── development                                           │
│  │   ├── staging                                               │
│  │   └── production                                            │
│  │       └── Resources (Virtual machines)                      │
│  │           ├── api-server-01  🟢 Online  [api, dotnet]       │
│  │           └── api-server-02  🟢 Online  [api, dotnet]       │
│  └── Library                                                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Auto-Create Feature

The role can automatically create Environments:

```yaml
azure_devops_agents_list:
  - name: "api-server"
    type: "environment"
    project: "MyProject"
    environment: "staging"
    auto_create: true    # ✅ Creates via REST API if doesn't exist
```

### Open Access Feature

Allow all pipelines to deploy to this environment without explicit authorization:

```yaml
azure_devops_agents_list:
  # Development - open to all pipelines
  - name: "dev-server"
    type: "environment"
    project: "WebApp"
    environment: "development"
    open_access: true     # ✅ Any pipeline can deploy

  # Production - requires explicit authorization
  - name: "prod-server"
    type: "environment"
    project: "WebApp"
    environment: "production"
    open_access: false    # ❌ Pipelines must be authorized
```

### Example YAML Pipeline with Environments

```yaml
# azure-pipelines.yml
trigger:
  - main

stages:
  - stage: Build
    pool: Linux-Pool
    jobs:
      - job: BuildJob
        steps:
          - script: echo "Building..."

  - stage: DeployDev
    dependsOn: Build
    jobs:
      - deployment: DeployDev
        environment: development      # ← Environment name
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo "Deploying to dev..."

  - stage: DeployProd
    dependsOn: DeployDev
    jobs:
      - deployment: DeployProd
        environment: production       # ← Environment with approvals
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo "Deploying to prod..."
```

### Environment Checks and Approvals

Environments support powerful governance features:

```
Environment: production
├── Approvals
│   └── Required approvers: [team-leads]
├── Checks
│   ├── Business hours: Mon-Fri 9AM-5PM
│   ├── Branch control: main only
│   └── Required template: deployment-template.yml
└── Resources
    ├── api-server-01
    └── api-server-02
```

## Comparison Table

| Feature | Self-Hosted | Deployment Group | Environment |
|---------|-------------|------------------|-------------|
| **Scope** | Organization | Project | Project |
| **Pipeline Type** | All (YAML, Classic) | Classic Release only | YAML only |
| **Auto-Create** | ❌ (pools pre-exist) | ✅ | ✅ |
| **Open Access** | N/A | ❌ | ✅ |
| **Tag Update API** | ❌ | ✅ | ✅ |
| **Multi-Project** | ✅ | ❌ | ❌ |
| **Approvals/Checks** | ❌ | Limited | ✅ Full |
| **Recommended For** | Builds | Legacy deployments | Modern deployments |

## Choosing the Right Type

### Decision Tree

```
┌─ What do you need?
│
├─ BUILD agents (compile, test, package)?
│  └─► Self-Hosted (Agent Pool)
│
├─ DEPLOYMENT targets?
│  │
│  ├─ Using Classic Release pipelines?
│  │  └─► Deployment Group
│  │
│  └─ Using YAML pipelines?
│     └─► Environment
│
└─ BOTH build and deploy?
   └─► Self-Hosted for builds + Environment for deployments
```

### Recommendation Summary

| Scenario | Recommended Type |
|----------|-----------------|
| CI/CD builds | Self-Hosted |
| New projects (YAML pipelines) | Environment |
| Existing Classic Releases | Deployment Group |
| Migrating to YAML | Transition from DG to Environment |
| Multi-project builds | Self-Hosted |
| Single-project deployments | Environment |

## Mixed Configuration Example

Deploy all three types to the same host:

```yaml
azure_devops_agents_list:
  # Build agent for CI
  - name: "build-agent"
    type: "self-hosted"
    pool: "Linux-Pool"
    tags: ["docker", "linux"]

  # Deployment Group for Classic Releases
  - name: "deploy-agent"
    type: "deployment-group"
    project: "LegacyApp"
    deployment_group: "Production"
    auto_create: true
    tags: ["web", "legacy"]

  # Environment for YAML pipelines
  - name: "env-agent"
    type: "environment"
    project: "ModernApp"
    environment: "production"
    auto_create: true
    open_access: false
    tags: ["api", "modern"]
```

Result on the host:

```
/opt/azure-devops-agents/
├── build-agent/     ← Self-hosted
├── deploy-agent/    ← Deployment Group
└── env-agent/       ← Environment

Services:
├── vsts.agent.myorg.build-agent.service
├── vsts.agent.myorg.deploy-agent.service
└── vsts.agent.myorg.env-agent.service
```

## Next Steps

Now that you understand the agent types, learn about advanced features:

➡️ **[Part 5: Advanced Features](05-advanced-features.md)** - Auto-create, open-access, tag updates, proxy, and more.

---

## Quick Reference

### Documentation Map

```
1. Introduction → 2. Prerequisites → 3. Basic Install → [4. Agent Types] → ...
```

### Type Quick Reference

```yaml
# Self-Hosted (pool required)
- name: "agent"
  type: "self-hosted"
  pool: "PoolName"

# Deployment Group (project + group required)
- name: "agent"
  type: "deployment-group"
  project: "ProjectName"
  deployment_group: "GroupName"
  auto_create: true

# Environment (project + environment required)
- name: "agent"
  type: "environment"
  project: "ProjectName"
  environment: "EnvName"
  auto_create: true
  open_access: true
```

---

[← Previous: Basic Installation](03-basic-installation.md) | [Back to Guide Index](README.md) | [Next: Advanced Features →](05-advanced-features.md)
