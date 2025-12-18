# Part 4: Runner Types (Scopes)

## 📋 Table of Contents

- [Understanding Runner Types](#understanding-runner-types)
- [Instance Runners (Admin)](#instance-runners-admin)
- [Group Runners](#group-runners)
- [Project Runners](#project-runners)
- [Choosing the Right Type](#choosing-the-right-type)
- [Multi-Type Deployment](#multi-type-deployment)
- [Type Comparison Table](#type-comparison-table)

---

## Understanding Runner Types

### What is a Runner Type?

The **runner type** determines WHERE your runner can be used:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Runner Type Hierarchy                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌─────────────────────────────────┐                  │
│                    │      INSTANCE RUNNER            │                  │
│                    │  (All projects in GitLab)       │                  │
│                    │  🔑 Requires: Admin token       │                  │
│                    │                                 │                  │
│                    │   ┌─────────────────────────┐   │                  │
│                    │   │     GROUP RUNNER        │   │                  │
│                    │   │  (All projects in group)│   │                  │
│                    │   │  🔑 Requires: Group PAT │   │                  │
│                    │   │                         │   │                  │
│                    │   │   ┌─────────────────┐   │   │                  │
│                    │   │   │ PROJECT RUNNER  │   │   │                  │
│                    │   │   │ (Single project)│   │   │                  │
│                    │   │   │ 🔑 Project PAT  │   │   │                  │
│                    │   │   └─────────────────┘   │   │                  │
│                    │   │                         │   │                  │
│                    │   └─────────────────────────┘   │                  │
│                    │                                 │                  │
│                    └─────────────────────────────────┘                  │
│                                                                          │
│   Scope:           Broadest ◄──────────────────────► Narrowest         │
│   Sharing:         Most Shared ◄───────────────────► Least Shared      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Quick Type Reference

| Type | Scope | PAT Required | Use Case |
|------|-------|--------------|----------|
| **Instance** | Entire GitLab instance | Admin token | Shared infrastructure runners |
| **Group** | All projects in group | Group owner/maintainer | Team/department runners |
| **Project** | Single project only | Project maintainer | Dedicated project runners |

---

## Instance Runners (Admin)

### When to Use Instance Runners

**Instance runners** are for administrators managing GitLab infrastructure:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Instance Runner Scope                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GitLab Instance (self-hosted)                                         │
│   ─────────────────────────────                                          │
│                                                                          │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│   │  Group 1     │  │  Group 2     │  │  Group 3     │                 │
│   │              │  │              │  │              │                 │
│   │ • Project A  │  │ • Project D  │  │ • Project G  │                 │
│   │ • Project B  │  │ • Project E  │  │ • Project H  │                 │
│   │ • Project C  │  │ • Project F  │  │ • Project I  │                 │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│          │                 │                 │                          │
│          └─────────────────┼─────────────────┘                          │
│                            │                                             │
│                            ▼                                             │
│                  ┌─────────────────┐                                    │
│                  │ Instance Runners│                                    │
│                  │                 │                                    │
│                  │ • shared-01     │                                    │
│                  │ • shared-02     │                                    │
│                  │ • shared-03     │                                    │
│                  └─────────────────┘                                    │
│                                                                          │
│   ✅ ALL projects can use these runners                                 │
│   ✅ Centrally managed by GitLab administrators                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Use when:**
- Managing self-hosted GitLab instance
- Want shared runners for all users
- Central infrastructure team
- Cost optimization (shared resources)

**⚠️ Note:** Instance runners only available on self-hosted GitLab (not gitlab.com)

### Instance Runner Configuration

```yaml
---
- name: Deploy Instance Runners (Admin Only)
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/admin_secrets.yml

  vars:
    gitlab_ci_runners_api_token: "{{ vault_admin_token }}"
    gitlab_ci_runners_api_runner_type: "instance_type"
    gitlab_ci_runners_gitlab_url: "https://gitlab.yourcompany.com"
    
    gitlab_ci_runners_runners_list:
      - name: "shared-runner-01"
        tags:
          - shared
          - docker
          - linux

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

---

## Group Runners

### When to Use Group Runners

**Group runners** are the most common choice:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Group Runner Scope                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Group: backend-team                                                   │
│   ─────────────────────                                                  │
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│   │ api-service │  │ worker      │  │ database    │                    │
│   │ repo        │  │ repo        │  │ migrations  │                    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                    │
│          │                │                │                            │
│          └────────────────┼────────────────┘                            │
│                           │                                              │
│                           ▼                                              │
│                  ┌─────────────────┐                                    │
│                  │ Group Runners   │                                    │
│                  │                 │                                    │
│                  │ • backend-01    │                                    │
│                  │ • backend-02    │                                    │
│                  └─────────────────┘                                    │
│                                                                          │
│   ✅ All repos in backend-team can use these runners                    │
│   ✅ Not available to other groups                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Use when:**
- Team/department-level runners
- Share runners across team projects
- Control who can use runners
- Most flexible option

### Group Runner Configuration

```yaml
---
- name: Deploy Group Runners
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/gitlab_secrets.yml

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "backend-team"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    # Auto-create group if it doesn't exist
    gitlab_ci_runners_auto_create_group: true
    gitlab_ci_runners_group_visibility: "private"
    
    gitlab_ci_runners_runners_list:
      - name: "backend-runner-01"
        tags:
          - docker
          - backend
          - linux
      
      - name: "backend-runner-02"
        tags:
          - docker
          - backend
          - linux

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Real-World Example: Multi-Team Setup

```yaml
# Deploy runners for multiple teams
gitlab_ci_runners_runners_list:
  # Backend team
  - name: "backend-runner-01"
    api_runner_type: "group_type"
    api_group_full_path: "backend-team"
    tags: [docker, backend, linux]
  
  # Frontend team
  - name: "frontend-runner-01"
    api_runner_type: "group_type"
    api_group_full_path: "frontend-team"
    tags: [docker, frontend, nodejs, linux]
  
  # DevOps team (deployment runners)
  - name: "deploy-runner-01"
    api_runner_type: "group_type"
    api_group_full_path: "devops-team"
    tags: [shell, deploy, production]
```

---

## Project Runners

### When to Use Project Runners

**Project runners** are dedicated to a single project:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Project Runner Scope                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Project: critical-payment-api                                         │
│   ───────────────────────────────                                        │
│                                                                          │
│   ┌─────────────────────────────────┐                                   │
│   │ Payment API Repo                │                                   │
│   │                                 │                                   │
│   │ • Sensitive payment processing  │                                   │
│   │ • PCI-DSS compliance required   │                                   │
│   │ • Dedicated resources needed    │                                   │
│   └─────────────┬───────────────────┘                                   │
│                 │                                                        │
│                 ▼                                                        │
│       ┌─────────────────┐                                               │
│       │ Project Runners │                                               │
│       │                 │                                               │
│       │ • payment-01    │ ← ONLY for payment API                        │
│       │ • payment-02    │ ← ONLY for payment API                        │
│       └─────────────────┘                                               │
│                                                                          │
│   ✅ ONLY this project can use these runners                            │
│   ✅ Complete isolation from other projects                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Use when:**
- High-security projects (payments, healthcare)
- Compliance requirements (PCI-DSS, HIPAA)
- Dedicated hardware needed (GPUs, large RAM)
- Complete project isolation required

### Project Runner Configuration

```yaml
---
- name: Deploy Project Runners
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/project_secrets.yml

  vars:
    gitlab_ci_runners_api_token: "{{ vault_project_api_token }}"
    gitlab_ci_runners_api_runner_type: "project_type"
    gitlab_ci_runners_api_project_id: "12345678"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    gitlab_ci_runners_list:
      - name: "payment-api-runner"
        tags:
          - docker
          - payment
          - secure
          - linux
        locked: true  # Lock to this project only

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

---

## Choosing the Right Type

### Decision Matrix

| Scenario | Recommended Type | Why? |
|----------|------------------|------|
| **Team with 5-10 projects** | Group | Share runners across team, easy management |
| **Single critical project** | Project | Complete isolation, dedicated resources |
| **Company-wide shared runners** | Instance | Cost-effective, centralized management |
| **Multi-team organization** | Group per team | Balance sharing and isolation |
| **High-security project** | Project | Compliance, complete control |
| **Rapid prototyping** | Group | Flexible, easy to set up |

### Cost Comparison

```
Scenario: 3 teams, each with 5 projects (15 total projects)

┌─────────────────┬──────────────┬─────────────┬──────────────┐
│ Approach        │ Runners      │ Servers     │ Complexity   │
├─────────────────┼──────────────┼─────────────┼──────────────┤
│ All Project     │ 15 runners   │ 15 servers  │ 🔴 High      │
│ (1 per project) │              │ $750/month  │              │
├─────────────────┼──────────────┼─────────────┼──────────────┤
│ All Group       │ 3 runners    │ 3 servers   │ 🟢 Low       │
│ (1 per team)    │              │ $150/month  │              │
├─────────────────┼──────────────┼─────────────┼──────────────┤
│ All Instance    │ 2 runners    │ 2 servers   │ 🟢 Low       │
│ (shared)        │              │ $100/month  │              │
└─────────────────┴──────────────┴─────────────┴──────────────┘
```

**Recommendation:** Start with **Group runners** for most teams.

---

## Multi-Type Deployment

### Hybrid Architecture

You can deploy different types on the same host:

```yaml
---
- name: Deploy Multi-Type Runners
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/gitlab_secrets.yml

  vars:
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    
    gitlab_ci_runners_list:
      # Group runner for general use
      - name: "team-runner"
        api_runner_type: "group_type"
        api_group_full_path: "backend-team"
        tags: [docker, general, linux]
      
      # Project runner for sensitive project
      - name: "payment-runner"
        api_runner_type: "project_type"
        api_project_id: "12345678"
        tags: [docker, payment, secure, linux]
        locked: true

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

---

## Type Comparison Table

| Feature | Instance | Group | Project |
|---------|----------|-------|---------|
| **Scope** | Entire GitLab | Group projects | Single project |
| **Availability** | Self-hosted only | gitlab.com + self-hosted | gitlab.com + self-hosted |
| **PAT Required** | Admin | Group owner/maintainer | Project maintainer |
| **Sharing** | All projects | Group projects | Project only |
| **Isolation** | Low | Medium | High |
| **Management** | Central | Team-level | Project-level |
| **Cost** | Most shared | Balanced | Dedicated |
| **Security** | Moderate | Good | Highest |
| **Flexibility** | High | High | Low |

---

## Next Steps

Now that you understand runner types:

- **[Part 5: Advanced Features](05-advanced-features.md)** - Tag management, access control
- **[Part 6: Production Deployment](06-production-deployment.md)** - Production patterns

---

[← Back to Guide Index](README.md)
