# Ansible Role: GitHub Actions Runners

**Enterprise-grade** Ansible role for deploying and managing GitHub Actions self-hosted runners on Linux servers.

## ✨ Key Features

- 🎯 **Multi-Runner Support**: Deploy N runners per host with isolated directories
- 🏢 **Three Scopes**: Organization, Repository, and Enterprise runners
- 🏷️ **Label Management**: Automatic label assignment and updates via REST API
- 👥 **Runner Groups**: Create and assign runners to groups (Organization/Enterprise)
- 🔄 **Lifecycle Management**: Install, configure, update, and remove runners
- 🔐 **Secure Authentication**: Registration tokens with automatic refresh
- ✅ **Service Verification**: Comprehensive service status checks
- 🏗️ **Multi-Platform**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+

## 📋 Table of Contents

- [Ansible Role: GitHub Actions Runners](#ansible-role-github-actions-runners)
  - [✨ Key Features](#-key-features)
  - [📋 Table of Contents](#-table-of-contents)
  - [Requirements](#requirements)
    - [Supported Distributions](#supported-distributions)
    - [GitHub Token Requirements](#github-token-requirements)
  - [Architecture](#architecture)
    - [Directory Structure](#directory-structure)
    - [Runner Scopes](#runner-scopes)
  - [Role Variables](#role-variables)
    - [Required Variables](#required-variables)
    - [Runner Configuration](#runner-configuration)
    - [Optional Variables](#optional-variables)
  - [Runner List Configuration](#runner-list-configuration)
    - [Basic Runner](#basic-runner)
    - [Runner with Custom Labels](#runner-with-custom-labels)
    - [Runner in a Group](#runner-in-a-group)
    - [Runner Removal](#runner-removal)
  - [Dependencies](#dependencies)
  - [Example Playbooks](#example-playbooks)
    - [Basic Installation](#basic-installation)
    - [Organization Runners](#organization-runners)
    - [Repository Runners](#repository-runners)
    - [Enterprise Runners](#enterprise-runners)
    - [Multi-Runner Deployment](#multi-runner-deployment)
    - [Runner Removal](#runner-removal-1)
  - [Labels and Groups](#labels-and-groups)
    - [Label Management](#label-management)
    - [Runner Groups](#runner-groups)
  - [Service Management](#service-management)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Validation Errors](#validation-errors)
  - [Testing](#testing)
  - [Security Considerations](#security-considerations)
  - [Comparison: GitHub Actions vs Azure DevOps](#comparison-github-actions-vs-azure-devops)
  - [License](#license)
  - [Author Information](#author-information)

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- GitHub Personal Access Token (PAT) with appropriate scopes
- Internet connectivity to GitHub API and releases

### Supported Distributions

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/CentOS/Rocky/AlmaLinux** | 9, 10 |

### GitHub Token Requirements

The role requires a Personal Access Token (PAT) with different scopes depending on the runner scope:

| Runner Scope | Required PAT Scopes |
|--------------|---------------------|
| **Repository** | `repo` (full repository access) |
| **Organization** | `admin:org` |
| **Enterprise** | `admin:enterprise` |

**Note**: For runner groups, additional `manage_runners:org` or `manage_runners:enterprise` scope may be required.

## Architecture

### Directory Structure

The role creates an isolated directory structure for each runner:

```
/opt/github-actions-runners/          # Base path (configurable)
├── .downloads/                       # Cached runner packages
│   └── actions-runner-linux-x64-2.x.x.tar.gz
├── runner-01/                        # Runner 1 directory
│   ├── config.sh                     # Configuration script
│   ├── run.sh                        # Manual run script
│   ├── svc.sh                        # Service management script
│   ├── .runner                       # Runner configuration
│   ├── .credentials                  # Encrypted credentials
│   ├── _work/                        # Workflow execution directory
│   └── ...                           # Runner binaries
├── runner-02/                        # Runner 2 directory
│   └── ...
└── runner-N/                         # Runner N directory
    └── ...
```

### Runner Scopes

| Scope | Description | API Endpoint |
|-------|-------------|--------------|
| **repository** | Runs jobs for a single repository | `/repos/{owner}/{repo}/actions/runners` |
| **organization** | Runs jobs for any repository in the organization | `/orgs/{org}/actions/runners` |
| **enterprise** | Runs jobs across the entire enterprise | `/enterprises/{enterprise}/actions/runners` |

## Role Variables

### Required Variables

```yaml
# GitHub Personal Access Token with appropriate scopes
github_actions_runners_token: ""

# Scope of the runners: organization, repository, or enterprise
github_actions_runners_scope: "organization"

# Organization name (required for scope: organization)
github_actions_runners_organization: ""

# Repository in format "owner/repo" (required for scope: repository)
github_actions_runners_repository: ""

# Enterprise slug (required for scope: enterprise)
github_actions_runners_enterprise: ""

# List of runners to deploy
github_actions_runners_list: []
```

### Runner Configuration

```yaml
# Runner version (leave empty for latest)
github_actions_runners_version: ""

# Base installation path
github_actions_runners_base_path: "/opt/github-actions-runners"

# Runner user and group
github_actions_runners_user: "ghrunner"
github_actions_runners_group: "ghrunner"

# Default labels applied to all runners
github_actions_runners_default_labels:
  - "self-hosted"
  - "Linux"
  - "{{ ansible_architecture }}"

# Enable ephemeral runners (removed after each job)
github_actions_runners_ephemeral: false

# Replace existing runner with same name
github_actions_runners_replace_existing: false
```

### Optional Variables

```yaml
# Runner group for organization/enterprise runners
github_actions_runners_group_name: "Default"

# Create runner group if it doesn't exist
github_actions_runners_create_group: false

# Service configuration
github_actions_runners_service_enabled: true
github_actions_runners_service_state: "started"

# Force runner reinstallation
github_actions_runners_force_reinstall: false

# Skip service verification
github_actions_runners_skip_verification: false

# Work folder cleanup (days to keep, 0 = disabled)
github_actions_runners_work_folder_cleanup_days: 0

# Also cleanup toolcache (Node.js, Python, etc.)
github_actions_runners_cleanup_toolcache: false

# Days to keep toolcache entries
github_actions_runners_toolcache_cleanup_days: 30
```

For complete variable reference, see [Variables Reference](../../docs/reference/VARIABLES.md).

## Work Folder Cleanup

The role includes automatic cleanup of old work directories to prevent disk space issues.

### How It Works

The `_work` directory stores:
- **Repository clones** - Source code from workflow jobs
- **Temporary files** - Build artifacts, logs
- **Toolcache** - Installed tools (Node.js, Python, etc.)

Over time, this can grow to **50-100GB+** on busy runners.

### Enabling Cleanup

```yaml
# Remove work directories older than 7 days
github_actions_runners_work_folder_cleanup_days: 7

# Also clean old toolcache entries (optional)
github_actions_runners_cleanup_toolcache: true
github_actions_runners_toolcache_cleanup_days: 30
```

### What Gets Cleaned

| Directory | Condition | Impact |
|-----------|-----------|--------|
| `_work/*` | Older than X days | Repos will be re-cloned |
| `_work/_temp/*` | Older than 1 day | None (temp files) |
| `_work/_tool/*` | Older than X days (if enabled) | Tools will be re-downloaded |

### Running Cleanup Only

You can run cleanup independently using tags:

```bash
ansible-playbook playbook.yml --tags cleanup
```

## Runner List Configuration

The `github_actions_runners_list` variable accepts a list of runner configurations.

### Runner Attributes Reference

Each runner in `github_actions_runners_list` is a dictionary with the following attributes:

#### Required Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | **Yes** | Unique runner name (used for directory and service identification) |

#### Core Configuration

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `state` | string | `present` | Runner lifecycle state: `present` (install/register) or `absent` (unregister/remove) |
| `labels` | list | `[]` | Custom labels for job routing (added to default labels: self-hosted, Linux, X64) |
| `runner_group` | string | `"Default"` | Runner group name (organization/enterprise only, ignored for repository scope) |
| `work_dir` | string | `"_work"` | Work directory name relative to runner path |

#### Advanced Configuration

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `ephemeral` | bool | `false` | Ephemeral runner: automatically removed after running one job |
| `replace` | bool | `false` | Replace existing runner with same name during registration |

### Complete Runner Example

```yaml
github_actions_runners_list:
  - name: "prod-runner-01"                    # Required: unique identifier
    state: present                            # Optional: present or absent
    
    # Labels for job routing
    labels:                                   # Optional: custom labels
      - production
      - deploy
      - kubernetes
    
    # Organization/Enterprise features
    runner_group: "production"                # Optional: group name (org/enterprise only)
    
    # Advanced features
    work_dir: "_work"                         # Optional: work directory name
    ephemeral: false                          # Optional: one-time runner
    replace: false                            # Optional: replace existing runner
```

### Basic Runner

```yaml
github_actions_runners_list:
  - name: "runner-01"
```

### Runner with Custom Labels

```yaml
github_actions_runners_list:
  - name: "docker-runner"
    labels:
      - "docker"
      - "nodejs"
      - "python"
```

### Runner in a Group

```yaml
github_actions_runners_list:
  - name: "production-runner"
    runner_group: "production"
    labels:
      - "production"
      - "secure"
```

### Runner Removal

```yaml
github_actions_runners_list:
  - name: "old-runner"
    state: absent
```

### Complete Runner Configuration

```yaml
github_actions_runners_list:
  - name: "complete-runner"
    state: present              # present (default) or absent
    labels:                     # Runner labels
      - "docker"
      - "nodejs"
    runner_group: "production"  # Runner group (org/enterprise only)
    work_folder: "_work"        # Work folder name (default: _work)
    ephemeral: false            # Ephemeral runner (one job only)
    replace: false              # Replace existing runner with same name
```

## Dependencies

None.

## Example Playbooks

### Basic Installation

```yaml
---
- name: Install GitHub Actions Runner
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "myorg"
    github_actions_runners_list:
      - name: "runner-{{ inventory_hostname }}"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Organization Runners

```yaml
---
- name: Deploy Organization Runners
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "mycompany"
    
    github_actions_runners_list:
      - name: "build-runner-01"
        labels:
          - "build"
          - "docker"
      
      - name: "build-runner-02"
        labels:
          - "build"
          - "nodejs"
      
      - name: "deploy-runner"
        labels:
          - "deploy"
          - "kubernetes"
        runner_group: "production"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Repository Runners

```yaml
---
- name: Deploy Repository Runners
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "repository"
    github_actions_runners_repository: "myorg/myrepo"
    
    github_actions_runners_list:
      - name: "repo-runner-01"
        labels:
          - "self-hosted"
          - "linux"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Enterprise Runners

```yaml
---
- name: Deploy Enterprise Runners
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "enterprise"
    github_actions_runners_enterprise: "my-enterprise"
    
    github_actions_runners_list:
      - name: "enterprise-runner-01"
        runner_group: "all-repos"
      
      - name: "enterprise-runner-02"
        runner_group: "internal-repos"

  roles:
    - code3tech.devtools.github_actions_runners
```

### Multi-Runner Deployment

```yaml
---
- name: Deploy Multiple Runners per Host
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "mycompany"
    
    # Deploy 3 runners per host
    github_actions_runners_list:
      - name: "{{ inventory_hostname }}-runner-01"
        labels: ["docker", "general"]
      
      - name: "{{ inventory_hostname }}-runner-02"
        labels: ["docker", "nodejs"]
      
      - name: "{{ inventory_hostname }}-runner-03"
        labels: ["docker", "python"]

  roles:
    - code3tech.devtools.github_actions_runners
```

### Runner Removal

```yaml
---
- name: Remove GitHub Actions Runners
  hosts: runners
  become: true

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "mycompany"
    
    github_actions_runners_list:
      - name: "old-runner-01"
        state: absent
      
      - name: "old-runner-02"
        state: absent
      
      # Keep this one running
      - name: "active-runner"
        state: present

  roles:
    - code3tech.devtools.github_actions_runners
```

## Labels and Groups

### Label Management

Labels help you route jobs to specific runners. The role supports:

1. **Default Labels**: Applied to all runners automatically
2. **Per-Runner Labels**: Specified in the runner configuration
3. **Label Updates**: Modify labels via the GitHub API

```yaml
# Default labels for all runners
github_actions_runners_default_labels:
  - "self-hosted"
  - "Linux"
  - "{{ ansible_architecture }}"

# Per-runner labels
github_actions_runners_list:
  - name: "specialized-runner"
    labels:
      - "docker"
      - "gpu"
      - "high-memory"
```

**Using Labels in Workflows:**

```yaml
# .github/workflows/build.yml
jobs:
  build:
    runs-on: [self-hosted, docker, Linux]
    steps:
      - uses: actions/checkout@v4
      # ...
```

### Runner Groups

Runner groups provide **access control** for organization and enterprise runners, similar to Azure DevOps `open_access` feature.

#### Quick Start - Open Access (All Repos)

```yaml
# Visibility: all = All repos can use (like open_access: true)
github_actions_runners_default_group_visibility: "all"

github_actions_runners_list:
  - name: "prod-runner-01"
    runner_group: "production"  # Group created automatically with visibility: all
```

#### Advanced - Restricted Access (Selected Repos)

```yaml
# Define groups with specific access control
github_actions_runners_groups:
  # Open access - all repos can use
  - name: "shared"
    visibility: "all"                # Like Azure DevOps open_access: true
    allows_public_repos: false

  # Restricted access - only specified repos
  - name: "production"
    visibility: "selected"           # Like Azure DevOps open_access: false
    allows_public_repos: false
    selected_repositories:           # Only these repos can use
      - "frontend-app"
      - "backend-api"
      - "infrastructure"

  # Open source projects
  - name: "open-source"
    visibility: "all"
    allows_public_repos: true        # Allow public repos

# Assign runners to groups
github_actions_runners_list:
  - name: "prod-runner-01"
    runner_group: "production"
  
  - name: "shared-runner-01"
    runner_group: "shared"
```

#### Visibility Options

| Visibility | Description | Azure DevOps Equivalent |
|------------|-------------|------------------------|
| `all` | All repositories can use runners | `open_access: true` |
| `selected` | Only specified repositories | `open_access: false` |

#### Group Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `github_actions_runners_auto_create_groups` | bool | `true` | Auto-create groups if missing |
| `github_actions_runners_default_group_visibility` | string | `"all"` | Default visibility for new groups |
| `github_actions_runners_default_group_allows_public_repos` | bool | `false` | Allow public repos by default |
| `github_actions_runners_groups` | list | `[]` | Explicit group configurations |

**Note**: Runner groups are only available for organization and enterprise scopes.

## Service Management

The role configures systemd services for each runner:

```yaml
# Service configuration
github_actions_runners_service_enabled: true   # Start on boot
github_actions_runners_service_state: "started"  # Current state
```

**Service Names:**
- Format: `actions.runner.{scope}.{runner-name}.service`
- Example: `actions.runner.myorg.runner-01.service`

**Manual Service Management:**

```bash
# Check status
sudo systemctl status actions.runner.myorg.runner-01

# Stop runner
sudo systemctl stop actions.runner.myorg.runner-01

# Start runner
sudo systemctl start actions.runner.myorg.runner-01

# View logs
sudo journalctl -u actions.runner.myorg.runner-01 -f
```

## Troubleshooting

### Common Issues

#### 1. Registration Token Expired

```
Error: The runner registration token has expired
```

**Solution**: Registration tokens are valid for 1 hour. Re-run the playbook to get a new token.

#### 2. Runner Already Exists

```
Error: A runner with the name 'runner-01' already exists
```

**Solutions**:
- Set `github_actions_runners_replace_existing: true`
- Or remove the runner from GitHub UI first
- Or use a different runner name

#### 3. Permission Denied

```
Error: Resource not accessible by integration
```

**Solution**: Verify your PAT has the correct scopes:
- Repository: `repo`
- Organization: `admin:org`
- Enterprise: `admin:enterprise`

#### 4. Service Failed to Start

```bash
# Check service status
sudo systemctl status actions.runner.myorg.runner-01

# Check logs
sudo journalctl -u actions.runner.myorg.runner-01 -n 50
```

**Common causes**:
- Missing dependencies (run `./bin/installdependencies.sh`)
- Wrong file permissions
- Port conflicts

### Validation Errors

The role provides detailed validation errors with ASCII-box formatting:

```
╔══════════════════════════════════════════════════════════════════════╗
║                 VALIDATION ERROR: MISSING ORGANIZATION               ║
╠══════════════════════════════════════════════════════════════════════╣
║ github_actions_runners_scope is 'organization' but                   ║
║ github_actions_runners_organization is not defined.                  ║
║                                                                      ║
║ Example:                                                             ║
║   github_actions_runners_organization: "my-organization"             ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Testing

This role includes Molecule tests for validation:

```bash
cd roles/github_actions_runners

# Run full test suite
molecule test

# Run converge only (faster iteration)
molecule converge

# Run verification
molecule verify

# Destroy test containers
molecule destroy
```

**Note**: Full runner registration requires real GitHub credentials. CI tests validate structure and prerequisites only.

## Security Considerations

### Token Security

- **Always** use Ansible Vault for `github_actions_runners_token`
- Tokens should have minimum required scopes
- Consider using GitHub App instead of PAT for better security
- Rotate tokens regularly

```yaml
# Encrypt token with Ansible Vault
ansible-vault encrypt_string 'ghp_your_token' --name 'vault_github_token'

# Reference in playbook
github_actions_runners_token: "{{ vault_github_token }}"
```

### Runner Security

- Runners execute untrusted code from workflows
- Use ephemeral runners for public repositories
- Implement network isolation for sensitive environments
- Consider runner groups to limit repository access

```yaml
# Enable ephemeral runners (destroyed after each job)
github_actions_runners_ephemeral: true
```

### File Permissions

The role creates all files with restricted permissions:
- Runner directories: `0755`
- Configuration files: `0600`
- Service user: dedicated `ghrunner` user

## Comparison: GitHub Actions vs Azure DevOps

| Feature | GitHub Actions | Azure DevOps |
|---------|---------------|--------------|
| **Token Type** | Registration Token (1h expiry) | PAT (persistent) |
| **Scopes** | Organization, Repository, Enterprise | Pool, Deployment Group, Environment |
| **Groups** | Runner Groups | Agent Pools |
| **Tags/Labels** | Labels | Capabilities + Tags |
| **Service Name** | `actions.runner.*` | `vstsagent.*` |
| **API** | GitHub REST API | Azure DevOps REST API |
| **Ephemeral** | Native support | Limited support |

## License

MIT

## Author Information

This role was created by the **Code3Tech DevOps Team**.

- GitHub: [code3tech](https://github.com/code3tech)
- Repository: [ansible-col-devtools](https://github.com/kode3tech/ansible-col-devtools)

---

📖 **Additional Resources:**
- [GitHub Actions Self-Hosted Runners Documentation](https://docs.github.com/en/actions/hosting-your-own-runners)
- [GitHub REST API - Runners](https://docs.github.com/en/rest/actions/self-hosted-runners)
- [Example Playbooks](../../playbooks/github_actions_runners/)

[← Back to Collection](../../README.md)
