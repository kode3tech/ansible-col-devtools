# Ansible Role: GitLab CI Runners

**Enterprise-grade** Ansible role for deploying and managing GitLab CI self-hosted runners on Linux servers.

## ✨ Key Features

- 🎯 **Multi-Runner Support**: Deploy N runners per host with isolated directories
- 🏢 **Three Runner Types**: Instance, Group, and Project runners  
- 🤖 **API-Based Management**: Create, update, and delete runners via GitLab API
- 🏷️ **Tag Management**: Dynamic tag updates without re-registration
- 🔄 **Lifecycle Management**: Install, configure, update, and remove runners
- 🔐 **Advanced Features**: run_untagged, locked, access_level configuration
- ✅ **Service Verification**: Comprehensive service status checks
- 🏗️ **Multi-Platform**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+

## 📋 Table of Contents

- [Requirements](#requirements)
- [Architecture](#architecture)
- [Role Variables](#role-variables)
- [Runner List Configuration](#runner-list-configuration)
- [Example Playbooks](#example-playbooks)
- [API-Based Management](#api-based-management)
- [Service Management](#service-management)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Security Considerations](#security-considerations)

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- GitLab API Personal Access Token (PAT) with `create_runner` scope
- Internet connectivity to GitLab API and package repositories

### Supported Distributions

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/CentOS/Rocky/AlmaLinux** | 9, 10 |

### GitLab Token Requirements

The role requires a Personal Access Token (PAT) with the following scope:

| Scope | Purpose |
|-------|---------|
| `create_runner` | Create and manage runners via API |

**⚠️ Security**: Always use Ansible Vault to store tokens:
```bash
ansible-vault create vars/secrets.yml
# Add: gitlab_ci_runners_api_token: "glpat-YOUR_TOKEN"
```

## Architecture

### Directory Structure

The role creates an isolated directory structure for each runner:

```
/opt/gitlab-ci-runners/               # Base path (configurable)
├── runner-01/                        # Runner 1 directory
│   ├── config.toml                   # Runner configuration
│   ├── builds/                       # Job build directories
│   └── cache/                        # Job cache
├── runner-02/                        # Runner 2 directory
│   ├── config.toml
│   ├── builds/
│   └── cache/
└── builds/                           # Shared builds (optional)
```

### Runner Types

| Type | Scope | Use Case |
|------|-------|----------|
| **instance_type** | Entire GitLab instance | Self-managed GitLab only |
| **group_type** | Specific group + all projects | Team runners (recommended) |
| **project_type** | Single project only | Project-specific workloads |

### Systemd Services

Each runner gets its own systemd service:

```
gitlab-runner@runner-01.service
gitlab-runner@runner-02.service
gitlab-runner@runner-03.service
```

## Role Variables

### Required Variables

```yaml
# GitLab URL
gitlab_ci_runners_gitlab_url: "https://gitlab.com"

# API Token (use Vault!)
gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"

# Runner type
gitlab_ci_runners_api_runner_type: "group_type"  # or instance_type, project_type

# For group_type runners
gitlab_ci_runners_api_group_full_path: "your-group-name"

# For project_type runners
# gitlab_ci_runners_api_project_path: "group/project"

# Runners to deploy
gitlab_ci_runners_runners_list:
  - name: "runner-01"
    executor: "shell"
    tags: ["linux", "shell"]
```

### Optional Variables

```yaml
# Auto-create resources
gitlab_ci_runners_auto_create_group: true
gitlab_ci_runners_group_visibility: "private"

# Tag management
gitlab_ci_runners_update_tags_via_api: true

# Performance
gitlab_ci_runners_concurrent: 4
gitlab_ci_runners_request_concurrency: 2

# Installation
gitlab_ci_runners_configure_repo: true
gitlab_ci_runners_version: ""  # empty = latest

# Service user
gitlab_ci_runners_user: "gitlab-runner"
gitlab_ci_runners_create_user: true
```

## Runner List Configuration

### Runner Attributes Reference

Each runner in `gitlab_ci_runners_runners_list` is a dictionary with the following attributes:

#### Required Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | **Yes** | Unique runner name (used for directory, service name, and cache key) |

#### Core Configuration

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `state` | string | `present` | Runner lifecycle state: `present` (install/register) or `absent` (unregister/remove) |
| `executor` | string | `shell` | Executor type: `shell`, `docker`, `docker+machine`, `kubernetes`, etc. |
| `description` | string | `{{ name }}` | Human-readable description shown in GitLab UI |
| `tags` | list | `[]` | List of tags for job matching (e.g., `["linux", "docker", "production"]`) |

#### API-Based Runner Creation

These attributes control API-based runner creation (when `token_mode=api`):

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_runner_type` | string | Global default | Runner scope: `instance_type`, `group_type`, or `project_type` |
| `api_group_id` | int | Global default | GitLab numeric group ID (required for `group_type`) |
| `api_group_full_path` | string | Global default | Alternative to `api_group_id`: group path (e.g., `"platform/ci"`) |
| `api_project_id` | int | Global default | GitLab numeric project ID (required for `project_type`) |
| `api_project_path` | string | Global default | Alternative to `api_project_id`: project path (e.g., `"mygroup/myproject"`) |
| `api_description` | string | `{{ description }}` | API-specific description (defaults to `description` attribute) |

#### Access Control

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `locked` | bool | `false` | `true`: Runner locked to current project only<br>`false`: Runner can be used by multiple projects in group |
| `access_level` | string | `""` | Access restriction: `not_protected` (any branch) or `ref_protected` (protected branches only) |
| `run_untagged` | bool | `false` | Allow runner to pick up jobs without tags |
| `paused` | bool | `false` | Create runner in paused state (won't pick up jobs until unpaused) |

#### Performance & Limits

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `maximum_timeout` | int | `0` | Maximum job timeout in seconds (0 = use GitLab default, typically 3600) |

#### Directories

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `builds_dir` | string | `{{ base_path }}/{{ name }}/builds` | Directory for job build files |
| `cache_dir` | string | `{{ base_path }}/{{ name }}/cache` | Directory for job cache files |

#### Advanced

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `maintenance_note` | string | `""` | Admin note shown in GitLab UI (e.g., "Prod runner - contact DevOps team") |

### Complete Runner Example

```yaml
gitlab_ci_runners_runners_list:
  - name: "prod-runner-01"                    # Required: unique identifier
    state: present                            # Optional: present or absent
    
    # Core configuration
    executor: "shell"                         # Optional: shell, docker, etc.
    description: "Production Deployment Runner"  # Optional: human-readable name
    tags:                                     # Optional: job matching tags
      - production
      - deploy
      - linux
    
    # API-based creation (overrides global defaults)
    api_runner_type: "group_type"            # Optional: instance_type, group_type, project_type
    api_group_full_path: "devops/production" # Optional: alternative to api_group_id
    api_description: "Prod runner managed by Ansible"  # Optional: API-specific description
    
    # Access control
    locked: false                            # Optional: false = multiple projects, true = locked
    access_level: "ref_protected"            # Optional: ref_protected or not_protected
    run_untagged: false                      # Optional: true = pick untagged jobs
    paused: false                            # Optional: true = start in paused state
    
    # Performance
    maximum_timeout: 10800                   # Optional: 3 hours (0 = GitLab default)
    
    # Directories (optional overrides)
    builds_dir: "/custom/builds/path"       # Optional: override default builds directory
    cache_dir: "/custom/cache/path"         # Optional: override default cache directory
    
    # Advanced
    maintenance_note: "Contact DevOps team before modifying"  # Optional: admin note
```

### Basic Runner

```yaml
gitlab_ci_runners_runners_list:
  - name: "dev-runner-01"
    description: "Development Runner"
    executor: "shell"
    tags:
      - development
      - linux
    run_untagged: true
    maximum_timeout: 3600
```

### Runner with Access Control

```yaml
gitlab_ci_runners_runners_list:
  - name: "prod-runner-01"
    description: "Production Runner"
    executor: "shell"
    locked: false              # Group runner (multiple projects)
    access_level: "ref_protected"  # Only protected branches
    tags:
      - production
      - deploy
    run_untagged: false
    maximum_timeout: 10800
```

### Runner Removal

```yaml
gitlab_ci_runners_runners_list:
  - name: "old-runner-01"
    state: absent  # Will unregister and remove
```

### Per-Runner API Scope Override

```yaml
gitlab_ci_runners_runners_list:
  # Runner for specific group (overrides global group)
  - name: "platform-runner-01"
    api_runner_type: "group_type"
    api_group_full_path: "platform"
    tags: ["platform", "backend"]
  
  # Runner for specific project (overrides global settings)
  - name: "webapp-runner-01"
    api_runner_type: "project_type"
    api_project_path: "platform/webapp"
    tags: ["webapp", "frontend"]
```

## Example Playbooks

### Basic Installation

```yaml
---
- name: Install GitLab CI Runners
  hosts: gitlab_runners
  become: true
  
  vars:
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "devops-team"
    
    gitlab_ci_runners_runners_list:
      - name: "runner-01"
        executor: "shell"
        tags: ["linux", "shell"]
        
  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Multi-Runner Deployment

```yaml
---
- name: Deploy Multiple GitLab Runners
  hosts: gitlab_runners
  become: true
  
  vars:
    gitlab_ci_runners_gitlab_url: "https://gitlab.com"
    gitlab_ci_runners_api_token: "{{ vault_gitlab_api_token }}"
    gitlab_ci_runners_api_runner_type: "group_type"
    gitlab_ci_runners_api_group_full_path: "devops-team"
    
    # Deploy 3 runners with different purposes
    gitlab_ci_runners_runners_list:
      # Development runner
      - name: "dev-runner-01"
        executor: "shell"
        access_level: "not_protected"
        tags: ["development", "ci", "test"]
        run_untagged: true
        
      # Staging runner
      - name: "staging-runner-01"
        executor: "shell"
        access_level: "ref_protected"
        tags: ["staging", "deploy"]
        run_untagged: false
        
      # Production runner
      - name: "prod-runner-01"
        executor: "shell"
        access_level: "ref_protected"
        locked: false
        tags: ["production", "deploy"]
        run_untagged: false
        
  roles:
    - code3tech.devtools.gitlab_ci_runners
```

## API-Based Management

### Auto-Create Group

```yaml
gitlab_ci_runners_auto_create_group: true
gitlab_ci_runners_group_visibility: "private"  # private, internal, public
```

### Dynamic Tag Updates

Update runner tags without re-registration:

```yaml
gitlab_ci_runners_update_tags_via_api: true

# Simply change tags in runners_list and re-run playbook
gitlab_ci_runners_runners_list:
  - name: "runner-01"
    tags: ["new-tag-1", "new-tag-2"]  # Tags updated via API
```

### Runner Access Levels

| access_level | Description |
|--------------|-------------|
| `""` (empty) | Default - no restrictions |
| `not_protected` | Any branch can use |
| `ref_protected` | Only protected branches (main, release/*) |

## Service Management

### Check Service Status

```bash
# List all runner services
systemctl list-units 'gitlab-runner@*'

# Check specific runner
systemctl status gitlab-runner@runner-01

# View logs
journalctl -u gitlab-runner@runner-01 -f
```

### Manage Services

```bash
# Restart runner
systemctl restart gitlab-runner@runner-01

# Stop runner
systemctl stop gitlab-runner@runner-01

# Enable on boot
systemctl enable gitlab-runner@runner-01
```

## Troubleshooting

### Common Issues

**Issue**: Runner not appearing in GitLab UI
```bash
# Verify runner is registered
gitlab-runner list --config /opt/gitlab-ci-runners/runner-01/config.toml

# Check authentication
gitlab-runner verify --config /opt/gitlab-ci-runners/runner-01/config.toml
```

**Issue**: Service won't start
```bash
# Check service status
systemctl status gitlab-runner@runner-01

# View logs
journalctl -u gitlab-runner@runner-01 -n 50

# Check config file
cat /opt/gitlab-ci-runners/runner-01/config.toml
```

**Issue**: Jobs not picked up
- Verify tags match your `.gitlab-ci.yml`
- Check `run_untagged` setting
- Ensure runner is not paused in GitLab UI
- Check `access_level` for protected branches

### Debug Mode

Enable detailed logging:

```yaml
gitlab_ci_runners_no_log: false  # Show sensitive output
```

## Testing

This role includes Molecule tests for all supported distributions:

```bash
# Test all scenarios
cd roles/gitlab_ci_runners
molecule test

# Test specific distro
molecule test --scenario-name default -- --limit ubuntu2204
```

## Security Considerations

### Token Security

✅ **DO**:
- Use Ansible Vault for tokens
- Use dedicated service account tokens
- Rotate tokens regularly
- Limit token scopes to minimum required

❌ **DON'T**:
- Commit tokens to git
- Use personal tokens in production
- Share tokens between environments

### Runner Security

- Runners execute code from GitLab jobs - ensure trust
- Use `access_level: "ref_protected"` for production
- Consider separate runners for sensitive workloads
- Review `locked` setting based on security requirements

### User Permissions

The `gitlab_ci_runners_user` runs all jobs:
- Grant minimum required permissions
- Use dedicated user account
- Don't run as root (default: gitlab-runner)

## License

MIT

## Author Information

This role was created by the **Code3Tech DevOps Team**.

- GitHub: [@kode3tech](https://github.com/kode3tech)
- Repository: [ansible-col-devtools](https://github.com/kode3tech/ansible-col-devtools)

[← Back to Roles](../README.md)
