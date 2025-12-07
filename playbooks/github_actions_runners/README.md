# GitHub Actions Runners - Example Playbooks

This directory contains example playbooks for deploying and managing GitHub Actions self-hosted runners using the `github_actions_runners` role.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Available Playbooks](#available-playbooks)
- [Quick Start](#quick-start)
- [Variables Configuration](#variables-configuration)
- [Runner Groups](#runner-groups)
- [Work Folder Cleanup](#work-folder-cleanup)
- [Usage Examples](#usage-examples)

## Overview

These playbooks demonstrate common deployment scenarios for GitHub Actions self-hosted runners:

| Playbook | Description | Complexity |
|----------|-------------|------------|
| [install-single-runner.yml](install-single-runner.yml) | Basic single runner installation | Basic |
| [install-multi-runner.yml](install-multi-runner.yml) | Multiple runners per host | Intermediate |
| [install-production.yml](install-production.yml) | ⭐ Production deployment with validation | Advanced |

## Key Features

- ✅ **Multi-runner support**: Deploy N runners per host with isolated directories
- ✅ **Three scopes**: Organization, Repository, and Enterprise runners
- ✅ **Runner groups with visibility control**: Like Azure DevOps `open_access`
- ✅ **Custom labels per runner**: Route jobs to specific runners
- ✅ **Automatic work folder cleanup**: Prevent disk space issues
- ✅ **Service verification**: Ensure all services are running
- ✅ **Time synchronization**: Important for token validation

## Prerequisites

1. **Ansible Collection**: Install the collection

   ```bash
   ansible-galaxy collection install code3tech.devtools
   ```

2. **GitHub Personal Access Token**: Create a PAT with appropriate scopes
   - **Repository scope**: `repo` (for repository runners)
   - **Organization scope**: `admin:org` (for organization runners)
   - **Enterprise scope**: `admin:enterprise` (for enterprise runners)

3. **Inventory**: Prepare your target hosts

   ```ini
   # inventory.ini
   [runners]
   runner-host-01 ansible_host=192.168.1.10
   runner-host-02 ansible_host=192.168.1.11
   ```

## Available Playbooks

### 1. install-single-runner.yml

**Purpose**: Quick installation of a single runner per host

**Best for**:
- Development environments
- Small teams
- Testing the role

**Key features**:
- One runner per host
- Default labels
- Organization scope

### 2. install-multi-runner.yml

**Purpose**: Deploy multiple runners on each host

**Best for**:
- CI/CD farms
- Maximizing host utilization
- Parallel job execution

**Key features**:
- N runners per host
- Custom labels per runner
- Runner groups support

### 3. install-production.yml ⭐

**Purpose**: Production-ready deployment with comprehensive validation

**Best for**:
- Production environments
- Enterprise deployments
- Teams requiring high reliability

**Key features**:
- Pre-flight validation with time synchronization
- Runner groups with visibility control (like Azure DevOps `open_access`)
- Automatic work folder cleanup to prevent disk space issues
- Service verification and comprehensive logging
- Error handling with detailed diagnostics

## Quick Start

1. **Create variables file**:

   ```bash
   # Create vars directory
   mkdir -p vars
   
   # Create and encrypt secrets
   ansible-vault create vars/github_secrets.yml
   ```

   Add to the vault file:
   ```yaml
   vault_github_token: "ghp_your_github_token_here"
   ```

2. **Run the playbook**:

   ```bash
   # Single runner (development)
   ansible-playbook install-single-runner.yml \
     -i inventory.ini \
     --ask-vault-pass \
     -e github_actions_runners_organization="your-org"

   # Production deployment
   ansible-playbook install-production.yml \
     -i inventory.ini \
     --ask-vault-pass
   ```

## Variables Configuration

### Required Variables

```yaml
# GitHub PAT with appropriate scopes
github_actions_runners_token: "{{ vault_github_token }}"

# Runner scope: organization, repository, or enterprise
github_actions_runners_scope: "organization"

# Organization name (for scope: organization)
github_actions_runners_organization: "your-organization"

# Repository (for scope: repository)
github_actions_runners_repository: "owner/repo"

# Enterprise slug (for scope: enterprise)
github_actions_runners_enterprise: "your-enterprise"

# List of runners to deploy
github_actions_runners_list:
  - name: "runner-01"
```

### Optional Variables

```yaml
# Custom labels for all runners
github_actions_runners_default_labels:
  - "self-hosted"
  - "Linux"
  - "x64"

# Runner user/group
github_actions_runners_user: "ghrunner"
github_actions_runners_group: "ghrunner"

# Base installation path
github_actions_runners_base_path: "/opt/github-actions-runners"

# Ephemeral runners (removed after each job)
github_actions_runners_ephemeral: false

# Work folder cleanup (days, 0 = disabled)
github_actions_runners_work_folder_cleanup_days: 7
```

## Runner Groups

Runner groups control which repositories can use specific runners, similar to Azure DevOps `open_access`.

### Visibility Options

| Visibility | Description | Use Case |
|------------|-------------|----------|
| `all` | All repos can use runners | Development, testing |
| `selected` | Only specific repos can use | Production workloads |
| `private` | Only private repos can use | Security compliance |

### Configuration Example

```yaml
# Define groups with access control
github_actions_runners_groups:
  # Production: Only specific repos can use (restricted)
  - name: "production"
    visibility: "selected"
    allows_public_repos: false
    selected_repositories:
      - "frontend-app"
      - "backend-api"

  # Development: All repos can use (open access)
  - name: "development"
    visibility: "all"
    allows_public_repos: false

# Assign runners to groups
github_actions_runners_list:
  - name: "prod-runner-01"
    labels: ["production", "docker"]
    runner_group: "production"  # ← Restricted access

  - name: "dev-runner-01"
    labels: ["development", "nodejs"]
    runner_group: "development"  # ← Open access
```

## Work Folder Cleanup

GitHub Actions runners store temporary files in `_work` directories which can grow significantly over time.

### Features

- ✅ **Automatic cleanup**: Removes work directories older than X days
- ✅ **Temp file cleanup**: Always removes `_temp` directories older than 1 day
- ✅ **Optional toolcache cleanup**: Clear Node.js, Python, etc. installations
- ✅ **Disk usage reporting**: Shows usage before and after cleanup

### Configuration

```yaml
# Enable cleanup (7 days retention)
github_actions_runners_work_folder_cleanup_days: 7

# Optional: Also cleanup toolcache
github_actions_runners_cleanup_toolcache: true
github_actions_runners_toolcache_cleanup_days: 30
```

### Running Cleanup Only

```bash
# Run only cleanup tasks (using tags)
ansible-playbook install-production.yml \
  -i inventory.ini \
  --tags cleanup
```

## Usage Examples

### Deploy Organization Runners

```bash
ansible-playbook install-production.yml \
  -i inventory.ini \
  --ask-vault-pass \
  -e github_actions_runners_scope=organization \
  -e github_actions_runners_organization=mycompany
```

### Deploy Repository Runners

```bash
ansible-playbook install-single-runner.yml \
  -i inventory.ini \
  --ask-vault-pass \
  -e github_actions_runners_scope=repository \
  -e github_actions_runners_repository=myorg/myrepo
```

### Deploy Multiple Runners per Host

```bash
ansible-playbook install-multi-runner.yml \
  -i inventory.ini \
  --ask-vault-pass \
  -e github_actions_runners_organization=mycompany \
  -e runners_per_host=3
```

### Remove Runners

```bash
# Set state: absent in the runner list
ansible-playbook install-production.yml \
  -i inventory.ini \
  --ask-vault-pass \
  -e "{'github_actions_runners_list': [{'name': 'old-runner', 'state': 'absent'}]}"
```

---

📖 **For complete documentation**, see the [role README](../../roles/github_actions_runners/README.md).

[← Back to Playbooks](../README.md)
