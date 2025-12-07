# Part 6: Advanced Features

> 🎬 **Video Tutorial Section**: Master advanced features like ephemeral runners, work folder cleanup, multi-runner deployments, and runner removal. These features are essential for production environments.

## 📋 Table of Contents

- [Ephemeral Runners](#ephemeral-runners)
- [Work Folder Cleanup](#work-folder-cleanup)
- [Multi-Runner Deployment](#multi-runner-deployment)
- [Runner Removal](#runner-removal)
- [Replacing Existing Runners](#replacing-existing-runners)
- [Custom Runner Paths](#custom-runner-paths)
- [Proxy Configuration](#proxy-configuration)
- [GitHub Enterprise Server](#github-enterprise-server)
- [Production Playbook Example](#production-playbook-example)

---

## Ephemeral Runners

### What Are Ephemeral Runners?

Ephemeral runners run **ONE job** and then automatically **remove themselves**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Ephemeral vs Persistent Runners                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PERSISTENT RUNNER (Default)                                            │
│   ────────────────────────────                                           │
│                                                                          │
│   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐                            │
│   │ Job 1│   │ Job 2│   │ Job 3│   │ Job 4│   ... (runs forever)       │
│   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘                            │
│      │          │          │          │                                  │
│      ▼          ▼          ▼          ▼                                  │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Runner stays alive, processing job after job                    │   │
│   │ ⚠️ State persists between jobs (cache, files, etc.)            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   EPHEMERAL RUNNER                                                       │
│   ────────────────                                                       │
│                                                                          │
│   ┌──────┐                                                              │
│   │ Job 1│                                                              │
│   └──┬───┘                                                              │
│      │                                                                   │
│      ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Runner processes job, then DELETES ITSELF                       │   │
│   │ ✅ Clean environment every time                                 │   │
│   │ ✅ No state persists                                            │   │
│   │ ⚠️ Must be recreated for next job                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### When to Use Ephemeral Runners

| Use Case | Ephemeral? | Reason |
|----------|------------|--------|
| Public repositories | ✅ Yes | Security - untrusted code |
| Open source projects | ✅ Yes | External contributors |
| Sensitive environments | ✅ Yes | No data leakage between jobs |
| Auto-scaling | ✅ Yes | Spin up, run job, spin down |
| High-volume CI | ❌ No | Overhead of recreation |
| Caching needed | ❌ No | Cache lost each time |
| Internal repos only | ❌ No | Persistent is more efficient |

### Configuring Ephemeral Runners

```yaml
# Global setting - all runners ephemeral
github_actions_runners_ephemeral: true

github_actions_runners_list:
  - name: "ephemeral-runner-01"
```

Or per-runner:

```yaml
github_actions_runners_list:
  # Ephemeral for open source
  - name: "oss-runner"
    ephemeral: true              # This runner is ephemeral
    labels:
      - "opensource"
      - "ephemeral"

  # Persistent for internal use
  - name: "internal-runner"
    ephemeral: false             # This runner is persistent (default)
    labels:
      - "internal"
      - "persistent"
```

### Complete Ephemeral Playbook

```yaml
---
# ephemeral-runners.yml
# Deploy ephemeral runners for open source or untrusted workloads

- name: Deploy Ephemeral GitHub Actions Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "myorg"

    # Runner groups for ephemeral runners
    github_actions_runners_groups:
      - name: "ephemeral-runners"
        visibility: "all"
        allows_public_repos: true     # Safe because ephemeral!

    github_actions_runners_list:
      - name: "ephemeral-01-{{ inventory_hostname }}"
        ephemeral: true
        runner_group: "ephemeral-runners"
        labels:
          - "ephemeral"
          - "disposable"
          - "docker"

  roles:
    - code3tech.devtools.github_actions_runners
```

---

## Work Folder Cleanup

### The Problem: Disk Space

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Work Folder Growth Problem                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   OVER TIME, THE _work FOLDER GROWS:                                    │
│                                                                          │
│   Day 1:    /opt/github-actions-runners/runner-01/_work/                │
│             └── repo-a/  (500 MB)                                       │
│             Total: 500 MB                                                │
│                                                                          │
│   Day 7:    /opt/github-actions-runners/runner-01/_work/                │
│             ├── repo-a/  (500 MB)                                       │
│             ├── repo-b/  (1.2 GB)                                       │
│             ├── repo-c/  (800 MB)                                       │
│             └── _temp/   (200 MB)                                       │
│             Total: 2.7 GB                                                │
│                                                                          │
│   Day 30:   /opt/github-actions-runners/runner-01/_work/                │
│             ├── 20+ repository clones                                   │
│             ├── Build artifacts                                         │
│             ├── Node modules                                            │
│             ├── Docker layers                                           │
│             └── Toolcache (Python, Node.js installations)              │
│             Total: 50+ GB ⚠️ DISK FULL!                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Solution: Automatic Cleanup

The role includes automatic cleanup of old work directories:

```yaml
# Enable cleanup - remove directories older than 7 days
github_actions_runners_work_folder_cleanup_days: 7

# Also clean toolcache (Node.js, Python installations)
github_actions_runners_cleanup_toolcache: true
github_actions_runners_toolcache_cleanup_days: 30
```

### What Gets Cleaned

| Directory | Cleaned When | Impact |
|-----------|--------------|--------|
| `_work/*` | Older than X days | Repos re-cloned on next job |
| `_work/_temp/*` | Older than 1 day | None (temporary files) |
| `_work/_tool/*` | Older than X days (if enabled) | Tools re-downloaded |

### Cleanup Configuration Options

```yaml
# Cleanup every 7 days (recommended for busy runners)
github_actions_runners_work_folder_cleanup_days: 7

# OR disable cleanup entirely (not recommended for production)
github_actions_runners_work_folder_cleanup_days: 0

# Also clean toolcache (optional - may slow down first job)
github_actions_runners_cleanup_toolcache: true
github_actions_runners_toolcache_cleanup_days: 30
```

### Running Cleanup Manually

You can run cleanup independently using tags:

```bash
# Run only cleanup tasks
ansible-playbook playbook.yml -i inventory.ini --tags cleanup
```

### Complete Cleanup Playbook

```yaml
---
# runners-with-cleanup.yml
# Deploy runners with automatic disk cleanup

- name: Deploy Runners with Disk Cleanup
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "myorg"

    # =========================================================================
    # CLEANUP CONFIGURATION
    # =========================================================================
    # Remove work directories older than 7 days
    github_actions_runners_work_folder_cleanup_days: 7

    # Also clean toolcache (Python, Node.js installations)
    github_actions_runners_cleanup_toolcache: true
    github_actions_runners_toolcache_cleanup_days: 30

    github_actions_runners_list:
      - name: "runner-{{ inventory_hostname }}"
        labels:
          - "docker"
          - "auto-cleanup"

  roles:
    - code3tech.devtools.github_actions_runners
```

---

## Multi-Runner Deployment

### Why Multiple Runners?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Single vs Multiple Runners                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   SINGLE RUNNER:                                                        │
│   ──────────────                                                         │
│   ┌─────────────────────────────────────────┐                           │
│   │                Server                    │                           │
│   │                                         │                           │
│   │   ┌─────────────────────────────────┐   │                           │
│   │   │ Runner 1                        │   │                           │
│   │   │                                 │   │                           │
│   │   │ Job A → Job B → Job C → ...    │   │                           │
│   │   │ (sequential, one at a time)    │   │                           │
│   │   └─────────────────────────────────┘   │                           │
│   │                                         │                           │
│   └─────────────────────────────────────────┘                           │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   MULTIPLE RUNNERS:                                                      │
│   ─────────────────                                                      │
│   ┌─────────────────────────────────────────┐                           │
│   │                Server                    │                           │
│   │                                         │                           │
│   │   ┌───────────┐ ┌───────────┐ ┌───────────┐                        │
│   │   │ Runner 1  │ │ Runner 2  │ │ Runner 3  │                        │
│   │   │           │ │           │ │           │                        │
│   │   │ Job A     │ │ Job B     │ │ Job C     │                        │
│   │   │ (parallel)│ │ (parallel)│ │ (parallel)│                        │
│   │   └───────────┘ └───────────┘ └───────────┘                        │
│   │                                         │                           │
│   └─────────────────────────────────────────┘                           │
│                                                                          │
│   ✅ 3x faster throughput!                                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Deploying Multiple Runners

```yaml
github_actions_runners_list:
  # Deploy 4 runners on each server
  - name: "{{ inventory_hostname }}-runner-01"
    labels: ["docker", "general"]

  - name: "{{ inventory_hostname }}-runner-02"
    labels: ["docker", "general"]

  - name: "{{ inventory_hostname }}-runner-03"
    labels: ["docker", "nodejs"]

  - name: "{{ inventory_hostname }}-runner-04"
    labels: ["docker", "python"]
```

### Dynamic Runner Count with Loop

```yaml
---
# Deploy N runners per server using a loop

- name: Deploy Multiple Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "myorg"

    # Number of runners to deploy per server
    runner_count: 4

    # Dynamically generate runner list
    github_actions_runners_list: >-
      {{
        range(1, runner_count + 1) | list | map('regex_replace', '^(.*)$',
        '{"name": "' ~ inventory_hostname ~ '-runner-0\\1", "labels": ["docker", "general"]}')
        | map('from_json') | list
      }}

  roles:
    - code3tech.devtools.github_actions_runners
```

### Different Runners for Different Purposes

```yaml
github_actions_runners_list:
  # 2 general purpose runners
  - name: "general-runner-01"
    labels: ["general", "docker"]
  - name: "general-runner-02"
    labels: ["general", "docker"]

  # 1 heavy build runner
  - name: "heavy-runner-01"
    labels: ["heavy", "docker", "high-memory"]

  # 1 deployment runner
  - name: "deploy-runner-01"
    runner_group: "production"
    labels: ["deploy", "production", "kubernetes"]
```

---

## Runner Removal

### Removing Specific Runners

```yaml
github_actions_runners_list:
  # This runner will be REMOVED
  - name: "old-runner-01"
    state: absent               # ← Magic word!

  # This runner stays (default)
  - name: "active-runner"
    state: present             # or just omit this line
```

### Removing All Runners from Host

```yaml
# Remove ALL runners from this host
github_actions_runners_state: "absent"

github_actions_runners_list:
  - name: "runner-01"
  - name: "runner-02"
  - name: "runner-03"
# All three will be removed!
```

### Complete Removal Playbook

```yaml
---
# remove-runners.yml
# Remove runners from servers

- name: Remove GitHub Actions Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  vars:
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "myorg"

    # Removal settings
    github_actions_runners_remove_on_uninstall: true    # Unregister from GitHub
    github_actions_runners_delete_on_remove: true       # Delete local files

    github_actions_runners_list:
      - name: "runner-to-remove-01"
        state: absent

      - name: "runner-to-remove-02"
        state: absent

  roles:
    - code3tech.devtools.github_actions_runners
```

### Removal Options

| Variable | Default | Description |
|----------|---------|-------------|
| `github_actions_runners_remove_on_uninstall` | `true` | Unregister from GitHub API |
| `github_actions_runners_delete_on_remove` | `true` | Delete local runner directory |
| `github_actions_runners_force_remove` | `false` | Force remove even if running jobs |

---

## Replacing Existing Runners

### When to Use Replace

```yaml
# Replace runner if it already exists (same name)
github_actions_runners_replace_existing: true

github_actions_runners_list:
  - name: "runner-01"
    # If "runner-01" exists, it will be replaced
```

**Use when:**
- Recreating a runner with new configuration
- Fixing a broken runner
- Updating runner to new version

---

## Custom Runner Paths

### Default Paths

```
Default base path: /opt/github-actions-runners/
Default user: ghrunner
Default group: ghrunner
```

### Customizing Paths

```yaml
# Custom installation path
github_actions_runners_base_path: "/srv/github-runners"

# Custom user/group
github_actions_runners_user: "ci-runner"
github_actions_runners_group: "ci-runner"

# Don't create user (use existing)
github_actions_runners_create_user: false
```

---

## Proxy Configuration

### Behind Corporate Proxy

```yaml
# Proxy settings
github_actions_runners_proxy_url: "http://proxy.company.com:8080"
github_actions_runners_no_proxy: "localhost,127.0.0.1,internal.company.com"
```

---

## GitHub Enterprise Server

### Connecting to GHES

```yaml
# GitHub Enterprise Server configuration
github_actions_runners_api_url: "https://github.company.com/api/v3"
github_actions_runners_github_url: "https://github.company.com"

# Optional: Custom CA certificate
github_actions_runners_ssl_ca_cert: "/etc/ssl/certs/company-ca.crt"

# NOT recommended for production!
# github_actions_runners_ssl_skip_cert_validation: true
```

---

## Production Playbook Example

### Complete Production-Ready Playbook

```yaml
---
# =============================================================================
# production-runners.yml
# Production-ready GitHub Actions runner deployment
# =============================================================================
#
# FEATURES:
# - Multiple runners per server (3)
# - Automatic disk cleanup
# - Runner groups with access control
# - Time synchronization verification
# - Service health checks
#
# REQUIREMENTS:
# - Ansible 2.15+
# - code3tech.devtools collection
# - vars/github_secrets.yml with vault_github_token
#
# USAGE:
# ansible-playbook production-runners.yml -i inventory.ini --ask-vault-pass
# =============================================================================

- name: Deploy Production GitHub Actions Runners
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml

  # ===========================================================================
  # PRE-FLIGHT CHECKS
  # ===========================================================================
  pre_tasks:
    - name: Verify time synchronization
      ansible.builtin.command: timedatectl status
      changed_when: false
      register: time_status

    - name: Display time sync status
      ansible.builtin.debug:
        msg: "{{ time_status.stdout_lines }}"

    - name: Check available disk space
      ansible.builtin.shell: df -h / | tail -1 | awk '{print $4}'
      changed_when: false
      register: disk_space

    - name: Warn if disk space is low
      ansible.builtin.debug:
        msg: "⚠️ WARNING: Only {{ disk_space.stdout }} available on root partition"
      when: disk_space.stdout | regex_replace('[^0-9]', '') | int < 20

  vars:
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    github_actions_runners_token: "{{ vault_github_token }}"

    # =========================================================================
    # SCOPE CONFIGURATION
    # =========================================================================
    github_actions_runners_scope: "organization"
    github_actions_runners_organization: "{{ vault_github_org | default('myorg') }}"

    # =========================================================================
    # INSTALLATION SETTINGS
    # =========================================================================
    github_actions_runners_version: ""                    # Empty = latest
    github_actions_runners_base_path: "/opt/github-actions-runners"
    github_actions_runners_user: "ghrunner"
    github_actions_runners_group: "ghrunner"

    # =========================================================================
    # SERVICE CONFIGURATION
    # =========================================================================
    github_actions_runners_service_enabled: true
    github_actions_runners_service_state: "started"

    # =========================================================================
    # CLEANUP CONFIGURATION
    # =========================================================================
    github_actions_runners_work_folder_cleanup_days: 7    # Clean after 7 days
    github_actions_runners_cleanup_toolcache: true        # Also clean toolcache
    github_actions_runners_toolcache_cleanup_days: 30     # Keep for 30 days

    # =========================================================================
    # RUNNER GROUPS
    # =========================================================================
    github_actions_runners_groups:
      # Development: All repos can use
      - name: "development"
        visibility: "all"
        allows_public_repos: false

      # Production: Selected repos only
      - name: "production"
        visibility: "selected"
        selected_repositories:
          - "frontend-app"
          - "backend-api"
          - "infrastructure"
        allows_public_repos: false

    # =========================================================================
    # RUNNER LIST (3 runners per server)
    # =========================================================================
    github_actions_runners_list:
      # General purpose runner 1
      - name: "{{ inventory_hostname }}-runner-01"
        runner_group: "development"
        labels:
          - "docker"
          - "nodejs"
          - "general"

      # General purpose runner 2
      - name: "{{ inventory_hostname }}-runner-02"
        runner_group: "development"
        labels:
          - "docker"
          - "python"
          - "general"

      # Production deployment runner
      - name: "{{ inventory_hostname }}-prod-runner"
        runner_group: "production"
        labels:
          - "docker"
          - "kubernetes"
          - "production"
          - "deploy"

  roles:
    - code3tech.devtools.github_actions_runners

  # ===========================================================================
  # POST-DEPLOYMENT VERIFICATION
  # ===========================================================================
  post_tasks:
    - name: List all runner services
      ansible.builtin.shell: systemctl list-units 'actions.runner.*' --no-pager
      changed_when: false
      register: runner_services

    - name: Display runner services status
      ansible.builtin.debug:
        msg: "{{ runner_services.stdout_lines }}"

    - name: Verify all services are running
      ansible.builtin.shell: |
        systemctl is-active actions.runner.*.{{ item.name }} 2>/dev/null || echo "not-found"
      loop: "{{ github_actions_runners_list }}"
      loop_control:
        label: "{{ item.name }}"
      register: service_status
      changed_when: false
      failed_when: >
        'active' not in service_status.stdout and
        'not-found' not in service_status.stdout

    - name: Summary
      ansible.builtin.debug:
        msg: |
          ✅ Deployment Complete!
          
          Runners deployed: {{ github_actions_runners_list | length }}
          Cleanup enabled: {{ github_actions_runners_work_folder_cleanup_days }} days
          
          Check runners in GitHub:
          https://github.com/organizations/{{ github_actions_runners_organization }}/settings/actions/runners
```

---

## Summary

| Feature | Variable | Description |
|---------|----------|-------------|
| **Ephemeral** | `ephemeral: true` | Single-use runners |
| **Cleanup** | `work_folder_cleanup_days: 7` | Auto-clean old files |
| **Multi-runner** | Multiple items in list | Deploy N runners |
| **Removal** | `state: absent` | Remove runners |
| **Replace** | `replace_existing: true` | Replace if exists |
| **Custom path** | `base_path: "/custom"` | Custom install location |
| **Proxy** | `proxy_url: "http://..."` | Behind proxy |
| **GHES** | `api_url: "https://..."` | Enterprise Server |

---

**Next Section**: [Part 7: Security Best Practices](07-security.md) →

← **Previous Section**: [Part 5: Labels & Runner Groups](05-labels-and-groups.md)

---

[← Back to User Guides](../README.md)
