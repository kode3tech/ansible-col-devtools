# Part 4: Runner Scopes Explained

> 🎬 **Video Tutorial Section**: Understanding scopes is crucial for proper runner architecture. This section explains each scope in detail with real-world examples and complete playbooks.

## 📋 Table of Contents

- [Understanding Scopes](#understanding-scopes)
- [Organization Scope](#organization-scope)
- [Repository Scope](#repository-scope)
- [Enterprise Scope](#enterprise-scope)
- [Choosing the Right Scope](#choosing-the-right-scope)
- [Multi-Scope Deployment](#multi-scope-deployment)
- [Scope Comparison Table](#scope-comparison-table)

---

## Understanding Scopes

### What is a Scope?

The **scope** determines WHERE your runner can be used:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Scope Hierarchy                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌─────────────────────────────────┐                  │
│                    │         ENTERPRISE              │                  │
│                    │  (All orgs in enterprise)       │                  │
│                    │                                 │                  │
│                    │   ┌─────────────────────────┐   │                  │
│                    │   │     ORGANIZATION        │   │                  │
│                    │   │  (All repos in org)     │   │                  │
│                    │   │                         │   │                  │
│                    │   │   ┌─────────────────┐   │   │                  │
│                    │   │   │   REPOSITORY    │   │   │                  │
│                    │   │   │  (Single repo)  │   │   │                  │
│                    │   │   └─────────────────┘   │   │                  │
│                    │   │                         │   │                  │
│                    │   └─────────────────────────┘   │                  │
│                    │                                 │                  │
│                    └─────────────────────────────────┘                  │
│                                                                          │
│   Scope Level:     Broadest ◄──────────────────────► Narrowest         │
│   Access Control:  Least Restrictive ◄──────────► Most Restrictive     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Quick Scope Reference

| Scope | Availability | Use Case | PAT Scope Required |
|-------|--------------|----------|-------------------|
| **Repository** | Single repo only | Dedicated runner for one project | `repo` |
| **Organization** | All repos in org | Shared runners across projects | `admin:org` |
| **Enterprise** | All orgs in enterprise | Central runner management | `admin:enterprise` |

---

## Organization Scope

### When to Use Organization Scope

**Organization scope** is the most common choice because:

- ✅ Runners can serve ANY repository in the organization
- ✅ Easier to manage (one set of runners for all projects)
- ✅ Cost-effective (runners are shared)
- ✅ Can be restricted using Runner Groups

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Organization Scope                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Organization: mycompany                                               │
│   ─────────────────────────                                              │
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│   │ frontend    │  │ backend     │  │ mobile      │                    │
│   │ repo        │  │ repo        │  │ repo        │                    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                    │
│          │                │                │                            │
│          └────────────────┼────────────────┘                            │
│                           │                                              │
│                           ▼                                              │
│                  ┌─────────────────┐                                    │
│                  │ Organization    │                                    │
│                  │ Runners         │                                    │
│                  │                 │                                    │
│                  │ • runner-01     │                                    │
│                  │ • runner-02     │                                    │
│                  │ • runner-03     │                                    │
│                  └─────────────────┘                                    │
│                                                                          │
│   ✅ All repos can use the same runners                                 │
│   ✅ Runners managed in ONE place                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Complete Organization Playbook

```yaml
---
# =============================================================================
# organization-runners.yml
# Deploy runners at Organization scope
# =============================================================================
# SCENARIO: You want runners that can serve any repository in your org
# 
# PREREQUISITES:
# - GitHub organization (not personal account)
# - PAT with admin:org scope
# - Owner or Admin role in organization
# =============================================================================

- name: Deploy Organization-Level GitHub Actions Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    # Your GitHub PAT - must have admin:org scope
    github_actions_runners_token: "{{ vault_github_token }}"

    # =========================================================================
    # SCOPE CONFIGURATION
    # =========================================================================
    # Set scope to organization
    github_actions_runners_scope: "organization"
    # ↑ This tells the role to register runners at org level

    # Your organization name (as it appears in github.com/ORG_NAME)
    github_actions_runners_organization: "mycompany"
    # ↑ Example: If your org URL is github.com/mycompany, use "mycompany"

    # =========================================================================
    # RUNNER CONFIGURATION
    # =========================================================================
    github_actions_runners_list:
      # General purpose runner
      - name: "org-runner-01"
        labels:
          - "general"
          - "docker"

      # Runner for Node.js projects
      - name: "org-runner-nodejs"
        labels:
          - "nodejs"
          - "npm"
          - "yarn"

      # Runner for Python projects
      - name: "org-runner-python"
        labels:
          - "python"
          - "pip"
          - "poetry"

  roles:
    - code3tech.devtools.github_actions_runners

# =============================================================================
# USAGE IN WORKFLOWS
# =============================================================================
# After deployment, any repo in "mycompany" can use these runners:
#
# jobs:
#   build:
#     runs-on: [self-hosted, linux]           # Any org runner
#     # OR
#     runs-on: [self-hosted, nodejs]          # Specific to Node.js runner
#     # OR  
#     runs-on: [self-hosted, python]          # Specific to Python runner
# =============================================================================
```

### Where to Find Organization Runners in GitHub

```
github.com/organizations/YOUR_ORG/settings/actions/runners
              ↑
              Your organization name

Navigation:
1. Go to github.com/orgs/YOUR_ORG
2. Click "Settings" 
3. Click "Actions" in left sidebar
4. Click "Runners"
```

---

## Repository Scope

### When to Use Repository Scope

**Repository scope** is best when:

- 🔒 Runner should ONLY be used by one repository
- 🔐 Need strict isolation between projects
- 🎯 Dedicated resources for critical repository
- 🚫 Don't want other repos accidentally using this runner

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Repository Scope                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Organization: mycompany                                               │
│   ─────────────────────────                                              │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Repository: mycompany/critical-app                             │   │
│   │                                                                  │   │
│   │  ┌───────────────────────────────────────────────────────────┐  │   │
│   │  │  Repository Runner                                        │  │   │
│   │  │  • dedicated-runner-01                                    │  │   │
│   │  │                                                           │  │   │
│   │  │  ✅ ONLY this repo can use this runner                   │  │   │
│   │  │  ❌ Other repos CANNOT use this runner                   │  │   │
│   │  └───────────────────────────────────────────────────────────┘  │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Repository: mycompany/other-app                                │   │
│   │                                                                  │   │
│   │  ❌ Cannot use dedicated-runner-01                              │   │
│   │  ✅ Can use organization runners (if available)                │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Complete Repository Playbook

```yaml
---
# =============================================================================
# repository-runners.yml
# Deploy runners at Repository scope
# =============================================================================
# SCENARIO: You want a dedicated runner for a specific repository
#           that cannot be used by any other repository
# 
# PREREQUISITES:
# - Repository in a GitHub organization or personal account
# - PAT with repo scope
# - Admin access to the repository
# =============================================================================

- name: Deploy Repository-Level GitHub Actions Runner
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    # Your GitHub PAT - must have repo scope
    github_actions_runners_token: "{{ vault_github_token }}"

    # =========================================================================
    # SCOPE CONFIGURATION
    # =========================================================================
    # Set scope to repository
    github_actions_runners_scope: "repository"
    # ↑ This tells the role to register runners at repo level

    # The repository in "owner/repo" format
    github_actions_runners_repository: "mycompany/critical-app"
    # ↑ IMPORTANT: Use "owner/repo" format, NOT just "repo"
    #   For org: "organization-name/repository-name"
    #   For personal: "username/repository-name"

    # =========================================================================
    # RUNNER CONFIGURATION
    # =========================================================================
    github_actions_runners_list:
      # Dedicated runner for this repository
      - name: "critical-app-runner"
        labels:
          - "dedicated"
          - "critical"
          - "fast"

  roles:
    - code3tech.devtools.github_actions_runners

# =============================================================================
# USAGE IN WORKFLOWS
# =============================================================================
# Only the repository "mycompany/critical-app" can use this runner:
#
# # In mycompany/critical-app/.github/workflows/build.yml:
# jobs:
#   build:
#     runs-on: [self-hosted, dedicated, critical]
#     steps:
#       - uses: actions/checkout@v4
#       - run: echo "Running on dedicated runner!"
#
# # In mycompany/other-repo/.github/workflows/build.yml:
# jobs:
#   build:
#     runs-on: [self-hosted, dedicated]
#     # ❌ This will be QUEUED FOREVER because other-repo
#     #    cannot use the critical-app runner!
# =============================================================================
```

### Multiple Repositories with Dedicated Runners

You can deploy different runners for different repositories:

```yaml
---
- name: Deploy Repository-Specific Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "repository"

    # =========================================================================
    # Deploy runners for MULTIPLE repositories
    # =========================================================================
    # Note: Each runner is registered to a SPECIFIC repository
    github_actions_runners_list:
      # Runner for frontend app
      - name: "frontend-runner"
        repository: "mycompany/frontend-app"    # Override global setting
        labels:
          - "frontend"
          - "nodejs"

      # Runner for backend API
      - name: "backend-runner"
        repository: "mycompany/backend-api"     # Different repo
        labels:
          - "backend"
          - "java"

      # Runner for mobile app
      - name: "mobile-runner"
        repository: "mycompany/mobile-app"      # Yet another repo
        labels:
          - "mobile"
          - "react-native"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Where to Find Repository Runners in GitHub

```
github.com/OWNER/REPO/settings/actions/runners
           ↑     ↑
           │     Repository name
           Owner (org or user)

Navigation:
1. Go to your repository
2. Click "Settings" 
3. Click "Actions" in left sidebar
4. Click "Runners"
```

---

## Enterprise Scope

### When to Use Enterprise Scope

**Enterprise scope** is for large organizations that:

- 🏢 Have GitHub Enterprise Cloud or Server
- 📊 Need runners available across MULTIPLE organizations
- 🎛️ Want centralized runner management
- 🔐 Need enterprise-wide policies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Enterprise Scope                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Enterprise: my-enterprise                                             │
│   ─────────────────────────                                              │
│                                                                          │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │                                                                │     │
│   │   ┌─────────────────┐  ┌─────────────────┐                    │     │
│   │   │ Organization A  │  │ Organization B  │                    │     │
│   │   │ • frontend      │  │ • mobile        │                    │     │
│   │   │ • backend       │  │ • analytics     │                    │     │
│   │   └────────┬────────┘  └────────┬────────┘                    │     │
│   │            │                    │                              │     │
│   │            └─────────┬──────────┘                              │     │
│   │                      │                                         │     │
│   │                      ▼                                         │     │
│   │            ┌─────────────────┐                                 │     │
│   │            │ Enterprise      │                                 │     │
│   │            │ Runners         │                                 │     │
│   │            │                 │                                 │     │
│   │            │ • ent-runner-01 │                                 │     │
│   │            │ • ent-runner-02 │                                 │     │
│   │            └─────────────────┘                                 │     │
│   │                                                                │     │
│   └───────────────────────────────────────────────────────────────┘     │
│                                                                          │
│   ✅ All orgs in enterprise can use the same runners                   │
│   ✅ Centralized management                                             │
│   ✅ Enterprise-wide runner groups                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Complete Enterprise Playbook

```yaml
---
# =============================================================================
# enterprise-runners.yml
# Deploy runners at Enterprise scope
# =============================================================================
# SCENARIO: You have GitHub Enterprise and want runners available
#           across all organizations in your enterprise
# 
# PREREQUISITES:
# - GitHub Enterprise Cloud or Server
# - PAT with admin:enterprise scope
# - Enterprise owner role
# =============================================================================

- name: Deploy Enterprise-Level GitHub Actions Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    # Your GitHub PAT - must have admin:enterprise scope
    github_actions_runners_token: "{{ vault_github_token }}"

    # =========================================================================
    # SCOPE CONFIGURATION
    # =========================================================================
    # Set scope to enterprise
    github_actions_runners_scope: "enterprise"
    # ↑ This tells the role to register runners at enterprise level

    # Your enterprise slug (from the URL)
    github_actions_runners_enterprise: "my-enterprise"
    # ↑ Find this in: github.com/enterprises/YOUR_ENTERPRISE_SLUG
    #   The slug is the part after /enterprises/

    # =========================================================================
    # RUNNER CONFIGURATION
    # =========================================================================
    github_actions_runners_list:
      # Enterprise-wide general runner
      - name: "enterprise-runner-01"
        labels:
          - "enterprise"
          - "shared"
        runner_group: "all-orgs"    # Enterprise runner group

      # Enterprise runner for production
      - name: "enterprise-runner-prod"
        labels:
          - "enterprise"
          - "production"
        runner_group: "production"   # Restricted runner group

  roles:
    - code3tech.devtools.github_actions_runners

# =============================================================================
# USAGE IN WORKFLOWS
# =============================================================================
# Any repository in any organization within the enterprise can use these:
#
# jobs:
#   build:
#     runs-on: [self-hosted, enterprise]
# =============================================================================
```

### Enterprise Runner Groups

Enterprise runner groups work similarly to organization groups:

```yaml
# Define enterprise runner groups
github_actions_runners_groups:
  # Open to all organizations
  - name: "all-orgs"
    visibility: "all"
    allows_public_repos: false

  # Restricted to specific organizations
  - name: "production"
    visibility: "selected"
    selected_organizations:       # Note: organizations, not repositories
      - "org-production"
      - "org-infrastructure"
    allows_public_repos: false
```

### Where to Find Enterprise Runners in GitHub

```
github.com/enterprises/YOUR_ENTERPRISE/settings/actions/runners
                       ↑
                       Your enterprise slug

Navigation:
1. Go to github.com/enterprises/YOUR_ENTERPRISE
2. Click "Settings"
3. Click "Actions" → "Runners"
```

---

## Choosing the Right Scope

### Decision Flowchart

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Scope Decision Flowchart                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   START                                                                  │
│     │                                                                    │
│     ▼                                                                    │
│   ┌─────────────────────────────────────────┐                           │
│   │ Do you have GitHub Enterprise?          │                           │
│   └──────────────────┬──────────────────────┘                           │
│                      │                                                   │
│         ┌───YES──────┴───────NO───────┐                                 │
│         ▼                             ▼                                  │
│   ┌─────────────────────┐   ┌─────────────────────────────────┐        │
│   │ Do you need runners │   │ Do you have a GitHub            │        │
│   │ across MULTIPLE     │   │ Organization?                   │        │
│   │ organizations?      │   └───────────────┬─────────────────┘        │
│   └──────────┬──────────┘                   │                           │
│              │                   ┌───YES────┴────NO────┐                │
│     ┌──YES───┴───NO───┐          ▼                     ▼                │
│     ▼                 ▼    ┌───────────────┐   ┌───────────────┐       │
│  ┌──────────┐  ┌──────────┐│ Do you need   │   │ Use REPOSITORY│       │
│  │ENTERPRISE│  │Use ORG   ││ runners       │   │ scope         │       │
│  │ scope    │  │ or REPO  ││ shared across │   │               │       │
│  │          │  │ scope    ││ repos?        │   │ (personal     │       │
│  └──────────┘  └──────────┘└───────┬───────┘   │  account)     │       │
│                                    │            └───────────────┘       │
│                        ┌───YES─────┴─────NO───┐                         │
│                        ▼                      ▼                          │
│               ┌─────────────────┐   ┌─────────────────┐                 │
│               │ Use             │   │ Use REPOSITORY  │                 │
│               │ ORGANIZATION    │   │ scope           │                 │
│               │ scope           │   │                 │                 │
│               │                 │   │ (dedicated      │                 │
│               │ (shared runners)│   │  runners)       │                 │
│               └─────────────────┘   └─────────────────┘                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Decision Matrix

| Question | If YES | If NO |
|----------|--------|-------|
| Need runners for multiple orgs? | Enterprise | Organization or Repository |
| Need runners shared across repos? | Organization | Repository |
| Need dedicated runner for one repo? | Repository | Organization |
| Using personal GitHub account? | Repository | N/A (need org) |
| Have GitHub Enterprise? | Can use Enterprise | Organization or Repository |

### Real-World Scenario Examples

#### Scenario 1: Small Company (5 repos, 1 team)

```yaml
# RECOMMENDATION: Organization scope
# WHY: All repos are in one org, shared runners work best

github_actions_runners_scope: "organization"
github_actions_runners_organization: "smallcompany"
github_actions_runners_list:
  - name: "shared-runner-01"
  - name: "shared-runner-02"
```

#### Scenario 2: Critical Production App

```yaml
# RECOMMENDATION: Repository scope for production, Organization for others
# WHY: Production needs dedicated resources

# Dedicated production runner
github_actions_runners_scope: "repository"
github_actions_runners_repository: "company/production-app"
github_actions_runners_list:
  - name: "prod-dedicated-runner"
    labels:
      - "production"
      - "dedicated"
```

#### Scenario 3: Large Enterprise (Multiple Organizations)

```yaml
# RECOMMENDATION: Enterprise scope with groups
# WHY: Central management, can restrict by org

github_actions_runners_scope: "enterprise"
github_actions_runners_enterprise: "big-corp"
github_actions_runners_groups:
  - name: "all-orgs"
    visibility: "all"
  - name: "finance-only"
    visibility: "selected"
    selected_organizations:
      - "finance-org"
```

---

## Multi-Scope Deployment

### Mixing Scopes in One Playbook

You can deploy runners at different scopes in the same playbook:

```yaml
---
- name: Deploy Multi-Scope Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  tasks:
    # =========================================================================
    # TASK 1: Deploy Organization Runners
    # =========================================================================
    - name: Deploy organization runners
      ansible.builtin.include_role:
        name: code3tech.devtools.github_actions_runners
      vars:
        github_actions_runners_token: "{{ vault_github_token }}"
        github_actions_runners_scope: "organization"
        github_actions_runners_organization: "mycompany"
        github_actions_runners_list:
          - name: "org-runner-{{ inventory_hostname }}"
            labels:
              - "organization"
              - "shared"

    # =========================================================================
    # TASK 2: Deploy Repository Runners (Dedicated)
    # =========================================================================
    - name: Deploy dedicated repository runner
      ansible.builtin.include_role:
        name: code3tech.devtools.github_actions_runners
      vars:
        github_actions_runners_token: "{{ vault_github_token }}"
        github_actions_runners_scope: "repository"
        github_actions_runners_repository: "mycompany/critical-app"
        github_actions_runners_list:
          - name: "critical-dedicated-{{ inventory_hostname }}"
            labels:
              - "dedicated"
              - "critical"
```

---

## Scope Comparison Table

| Feature | Repository | Organization | Enterprise |
|---------|------------|--------------|------------|
| **Availability** | Single repo | All repos in org | All orgs in enterprise |
| **Runner Groups** | ❌ Not available | ✅ Available | ✅ Available |
| **Access Control** | Implicit (repo only) | Via Groups | Via Groups |
| **Management Location** | Repo Settings | Org Settings | Enterprise Settings |
| **PAT Scope Needed** | `repo` | `admin:org` | `admin:enterprise` |
| **GitHub Plan** | Free and above | Free and above | Enterprise only |
| **Best For** | Dedicated runners | Shared runners | Central management |
| **Isolation** | Maximum | Configurable | Configurable |

---

## Summary

| Scope | When to Use | Key Variable |
|-------|-------------|--------------|
| **Repository** | Dedicated runner for one repo | `github_actions_runners_repository` |
| **Organization** | Shared runners across repos | `github_actions_runners_organization` |
| **Enterprise** | Runners across multiple orgs | `github_actions_runners_enterprise` |

---

**Next Section**: [Part 5: Labels & Runner Groups](05-labels-and-groups.md) →

← **Previous Section**: [Part 3: Basic Installation](03-basic-installation.md)

---

[← Back to User Guides](../README.md)
