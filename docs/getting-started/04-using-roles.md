# Using Collection Roles

Comprehensive guide to all 6 roles in the **code3tech.devtools** collection.

## 📋 Table of Contents

- [Available Roles](#available-roles)
- [Docker Role](#docker-role)
- [Podman Role](#podman-role)
- [Azure DevOps Agents](#azure-devops-agents)
- [GitHub Actions Runners](#github-actions-runners)
- [GitLab CI Runners](#gitlab-ci-runners)
- [asdf Version Manager](#asdf-version-manager)
- [Combining Multiple Roles](#combining-multiple-roles)

---

## Available Roles

| Role | Purpose | Use Case |
|------|---------|----------|
| **docker** | Docker Engine | Container runtime for applications |
| **podman** | Podman (rootless) | Daemonless containers, enhanced security |
| **azure_devops_agents** | Azure DevOps agents | Azure Pipelines CI/CD |
| **github_actions_runners** | GitHub Actions runners | GitHub workflows CI/CD |
| **gitlab_ci_runners** | GitLab CI runners | GitLab pipelines CI/CD |
| **asdf** | Version manager | Manage Node.js, Python, Ruby versions |

---

## Docker Role

### Basic Installation

```yaml
---
- name: Install Docker
  hosts: docker_hosts
  become: true
  
  roles:
    - code3tech.devtools.docker
```

### With Custom Configuration

```yaml
---
- name: Install Docker with custom settings
  hosts: docker_hosts
  become: true
  
  vars:
    # Add users to docker group (password-less docker commands)
    docker_users:
      - deploy
      - jenkins
      - webapp
    
    # Configure Docker daemon
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "10m"
        max-file: "3"
      storage-driver: "overlay2"
      max-concurrent-downloads: 10
  
  roles:
    - code3tech.devtools.docker
```

### With Registry Authentication

```yaml
---
- name: Install Docker with private registry access
  hosts: docker_hosts
  become: true
  
  vars:
    docker_registries_auth:
      - registry: "ghcr.io"
        username: "myuser"
        password: "{{ vault_github_token }}"
      
      - registry: "registry.company.com"
        username: "ci-user"
        password: "{{ vault_registry_password }}"
  
  roles:
    - code3tech.devtools.docker
```

**💡 Tip**: Use Ansible Vault for secrets:
```bash
ansible-vault create secrets.yml
# Add: vault_github_token: "ghp_xxxxx"
```

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `docker_users` | `[]` | Users to add to docker group |
| `docker_daemon_config` | `{}` | Docker daemon configuration |
| `docker_registries_auth` | `[]` | Private registry credentials |
| `docker_version` | `""` | Specific version (empty = latest) |
| `docker_configure_repo` | `true` | Add official Docker repository |

**📖 Complete documentation**: [Docker Role README](../../roles/docker/README.md)

---

## Podman Role

### Basic Installation

```yaml
---
- name: Install Podman with rootless support
  hosts: podman_hosts
  become: true
  
  roles:
    - code3tech.devtools.podman
```

### With Rootless Configuration

```yaml
---
- name: Install Podman with multi-user rootless
  hosts: podman_hosts
  become: true
  
  vars:
    # Enable rootless for these users
    podman_users:
      - developer
      - webapp
      - jenkins
    
    # Configure rootless runtime
    podman_rootless_enable: true
    
    # Per-user registry authentication
    podman_registries_auth:
      - registry: "quay.io"
        username: "devuser"
        password: "{{ vault_quay_token }}"
  
  roles:
    - code3tech.devtools.podman
```

### Key Differences: Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| **Daemon** | Requires dockerd | Daemonless |
| **Root required** | Yes (or group) | No (true rootless) |
| **systemd integration** | Service-based | User services |
| **Security** | Group = root access | Per-user isolation |
| **OCI compliance** | Yes | Yes |
| **Docker compatible** | N/A | Yes (alias docker=podman) |

**When to use Podman:**
- Security-first environments
- Multi-tenant systems
- No daemon overhead needed
- Kubernetes-native workflows

**📖 Complete documentation**: [Podman Role README](../../roles/podman/README.md)

---

## Azure DevOps Agents

### Single Agent

```yaml
---
- name: Deploy Azure DevOps self-hosted agent
  hosts: ci_servers
  become: true
  
  vars:
    azure_devops_agents_org_url: "https://dev.azure.com/your-org"
    azure_devops_agents_pat: "{{ vault_azure_pat }}"
    
    azure_devops_agents_list:
      - name: "agent-01"
        pool: "Default"
  
  roles:
    - code3tech.devtools.azure_devops_agents
```

### Multi-Agent Setup

```yaml
---
- name: Deploy multiple Azure DevOps agents
  hosts: ci_servers
  become: true
  
  vars:
    azure_devops_agents_org_url: "https://dev.azure.com/your-org"
    azure_devops_agents_pat: "{{ vault_azure_pat }}"
    
    # Deploy 3 agents on same host
    azure_devops_agents_list:
      - name: "build-agent-01"
        pool: "Build-Pool"
        agent_type: "self_hosted"
      
      - name: "deploy-agent-01"
        deployment_group: "Production"
        agent_type: "deployment_group"
      
      - name: "env-agent-01"
        environment: "Production"
        agent_type: "environment"
  
  roles:
    - code3tech.devtools.azure_devops_agents
```

**💡 Agent Types:**
- **self_hosted**: Regular pipeline agent (pool-based)
- **deployment_group**: Deployment group agent
- **environment**: Environment resource agent

**📖 Complete documentation**: [Azure DevOps Agents README](../../roles/azure_devops_agents/README.md)

---

## GitHub Actions Runners

### Organization Runner

```yaml
---
- name: Deploy GitHub Actions runner for organization
  hosts: ci_servers
  become: true
  
  vars:
    github_actions_runners_org: "your-organization"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    
    github_actions_runners_list:
      - name: "runner-01"
        labels:
          - "linux"
          - "docker"
          - "self-hosted"
  
  roles:
    - code3tech.devtools.github_actions_runners
```

### Repository Runner

```yaml
---
- name: Deploy GitHub Actions runner for specific repository
  hosts: ci_servers
  become: true
  
  vars:
    github_actions_runners_scope: "repository"
    github_actions_runners_owner: "your-organization"
    github_actions_runners_repo: "your-repository"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    
    github_actions_runners_list:
      - name: "repo-runner-01"
        labels:
          - "linux"
          - "nodejs"
  
  roles:
    - code3tech.devtools.github_actions_runners
```

### Ephemeral Runner

```yaml
---
- name: Deploy ephemeral (single-use) runner
  hosts: ci_servers
  become: true
  
  vars:
    github_actions_runners_org: "your-organization"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    
    github_actions_runners_list:
      - name: "ephemeral-runner-01"
        ephemeral: true                    # Single-use runner
        labels:
          - "ephemeral"
          - "docker"
  
  roles:
    - code3tech.devtools.github_actions_runners
```

**💡 Scopes:**
- **organization**: Runner available to all repos in org
- **repository**: Runner for specific repo only
- **enterprise**: Runner for GitHub Enterprise (requires enterprise license)

**📖 Complete documentation**: [GitHub Actions Runners README](../../roles/github_actions_runners/README.md)

---

## GitLab CI Runners

### Group Runner (Recommended)

```yaml
---
- name: Deploy GitLab CI runner for group
  hosts: ci_servers
  become: true
  
  vars:
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "your-group"
    
    gitlab_ci_runners_runners_list:
      - name: "runner-01"
        executor: "shell"
        tags:
          - "linux"
          - "shell"
          - "docker"
  
  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Multi-Runner with Access Control

```yaml
---
- name: Deploy GitLab CI runners with different access levels
  hosts: ci_servers
  become: true
  
  vars:
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "devops-team"
    
    gitlab_ci_runners_runners_list:
      # Development runner (any branch)
      - name: "dev-runner-01"
        tags: ["development", "test"]
        run_untagged: true
        access_level: "not_protected"
      
      # Production runner (protected branches only)
      - name: "prod-runner-01"
        tags: ["production", "deploy"]
        run_untagged: false
        access_level: "ref_protected"
        locked: false
  
  roles:
    - code3tech.devtools.gitlab_ci_runners
```

**💡 Access Levels:**
- **not_protected**: Any branch can use
- **ref_protected**: Only protected branches (main, release/*)

**📖 Complete documentation**: [GitLab CI Runners README](../../roles/gitlab_ci_runners/README.md)

---

## asdf Version Manager

### Basic Installation

```yaml
---
- name: Install asdf version manager
  hosts: dev_servers
  become: true
  
  vars:
    asdf_users:
      - developer
      - webapp
  
  roles:
    - code3tech.devtools.asdf
```

### With Plugins and Versions

```yaml
---
- name: Install asdf with Node.js and Python
  hosts: dev_servers
  become: true
  
  vars:
    asdf_users:
      - developer
    
    # Install plugins
    asdf_plugins:
      - name: nodejs
        versions:
          - "20.10.0"
          - "18.19.0"
        global: "20.10.0"
      
      - name: python
        versions:
          - "3.11.7"
          - "3.12.1"
        global: "3.12.1"
      
      - name: terraform
        versions:
          - "1.6.6"
        global: "1.6.6"
  
  roles:
    - code3tech.devtools.asdf
```

### Centralized Architecture

**Benefits:**
- ✅ Plugins installed once, shared by all users
- ✅ Group-based permissions (`asdf` group)
- ✅ Consistent versions across teams
- ✅ Easy version management

**Users can:**
```bash
# List available versions
asdf list nodejs

# Switch version (user-level)
asdf local nodejs 18.19.0

# Install new version (group permission required)
asdf install nodejs 21.0.0
```

**📖 Complete documentation**: [asdf Role README](../../roles/asdf/README.md)

---

## Combining Multiple Roles

### CI/CD Server Setup

```yaml
---
- name: Complete CI/CD server setup
  hosts: ci_servers
  become: true
  
  vars:
    # Docker configuration
    docker_users:
      - runner
      - jenkins
    
    # GitHub Actions runner
    github_actions_runners_org: "your-org"
    github_actions_runners_pat: "{{ vault_github_pat }}"
    github_actions_runners_list:
      - name: "runner-01"
        labels: ["linux", "docker"]
  
  roles:
    # Install Docker first (dependency)
    - code3tech.devtools.docker
    
    # Install asdf for version management
    - code3tech.devtools.asdf
    
    # Install GitHub Actions runner
    - code3tech.devtools.github_actions_runners
```

**Execution order matters!** Dependencies first, then dependent roles.

### Multi-Cloud CI/CD Infrastructure

```yaml
---
- name: Deploy runners for all platforms
  hosts: ci_servers
  become: true
  
  vars_files:
    - secrets.yml  # Contains all PATs/tokens
  
  roles:
    # Docker for container builds
    - code3tech.devtools.docker
    
    # Azure DevOps agent
    - role: code3tech.devtools.azure_devops_agents
      vars:
        azure_devops_agents_org_url: "{{ vault_azure_org_url }}"
        azure_devops_agents_pat: "{{ vault_azure_pat }}"
    
    # GitHub Actions runner
    - role: code3tech.devtools.github_actions_runners
      vars:
        github_actions_runners_org: "{{ vault_github_org }}"
        github_actions_runners_pat: "{{ vault_github_pat }}"
    
    # GitLab CI runner
    - role: code3tech.devtools.gitlab_ci_runners
      vars:
        gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
```

---

## Role Comparison Table

### Container Runtimes

| Feature | Docker | Podman |
|---------|--------|--------|
| **Best for** | Standard deployments | Security-first, rootless |
| **Daemon** | Required | No |
| **User privileges** | Group membership | True rootless |
| **Performance** | Standard | Slightly better (no daemon) |
| **Compatibility** | Docker only | Docker + Kubernetes native |

### CI/CD Runners

| Feature | Azure DevOps | GitHub Actions | GitLab CI |
|---------|--------------|----------------|-----------|
| **Agent types** | 3 types | 3 scopes | 3 runner types |
| **API-based** | Partial | Full (labels) | Full (create/update/delete) |
| **Multi-runner** | ✅ | ✅ | ✅ |
| **Auto-create resources** | ✅ | ✅ | ✅ |
| **Tag management** | Static | Dynamic (API) | Dynamic (API) |

---

## Quick Reference

### Installation Commands

```bash
# View available roles
ansible-galaxy collection list code3tech.devtools

# View role variables
ansible-doc -t role code3tech.devtools.docker

# Test role syntax
ansible-playbook playbook.yml --syntax-check

# Dry run (check mode)
ansible-playbook playbook.yml --check

# Run with verbose output
ansible-playbook playbook.yml -vv
```

### Common Variables Pattern

All roles follow consistent naming:
```yaml
{role}_users: []                    # Users to configure
{role}_version: ""                  # Specific version
{role}_configure_repo: true         # Add package repository
{role}_service_enabled: true        # Enable service
{role}_service_state: started       # Service state
```

---

## Next Steps

✅ **Explored all roles!** Continue with:

1. **[Common Patterns](05-common-patterns.md)** - Multi-environment, vault, tags, templates
2. **[Troubleshooting](06-troubleshooting.md)** - Fix common execution issues
3. **[User Guides](../user-guides/)** - Deep dive into specific roles

---

[← Back: Inventory Basics](03-inventory-basics.md) | [Next: Common Patterns →](05-common-patterns.md)
