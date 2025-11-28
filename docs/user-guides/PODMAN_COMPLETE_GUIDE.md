# Podman Complete Guide - Root vs Rootless Mode

A comprehensive guide to understanding and configuring Podman with the `code3tech.devtools` Ansible collection. This guide covers everything from basic concepts to production deployment with performance optimization.

## 📋 Table of Contents

- [Overview](#overview)
  - [What is Podman?](#what-is-podman)
  - [Podman vs Docker](#podman-vs-docker)
  - [Root Mode vs Rootless Mode](#root-mode-vs-rootless-mode)
- [Quick Start](#quick-start)
- [Understanding the Modes](#understanding-the-modes)
  - [Root Mode (Traditional)](#root-mode-traditional)
  - [Rootless Mode (Recommended)](#rootless-mode-recommended)
  - [Mode Comparison Table](#mode-comparison-table)
  - [When to Use Each Mode](#when-to-use-each-mode)
- [Installation and Basic Configuration](#installation-and-basic-configuration)
  - [Minimal Installation](#minimal-installation)
  - [Installation with Rootless Users](#installation-with-rootless-users)
- [Complete Variable Reference](#complete-variable-reference)
  - [Package Configuration](#package-configuration)
  - [Rootless Configuration](#rootless-configuration)
  - [Storage Configuration](#storage-configuration)
  - [Registry Configuration](#registry-configuration)
  - [Authentication Configuration](#authentication-configuration)
- [Production Playbook Explained](#production-playbook-explained)
  - [Pre-Tasks: Environment Preparation](#pre-tasks-environment-preparation)
  - [Role Configuration](#role-configuration)
  - [Post-Tasks: Validation](#post-tasks-validation)
- [Performance Optimization](#performance-optimization)
  - [crun vs runc Runtime](#crun-vs-runc-runtime)
  - [Storage Optimization](#storage-optimization)
  - [Parallel Downloads](#parallel-downloads)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Complete Examples](#complete-examples)

---

## Overview

### What is Podman?

Podman is a **daemonless container engine** developed by Red Hat as an alternative to Docker. Key characteristics:

- **No Daemon Required**: Unlike Docker, Podman doesn't require a background service running as root
- **OCI-Compliant**: Uses the same container images and registries as Docker
- **CLI Compatible**: Most Docker commands work with Podman (`alias docker=podman`)
- **Rootless by Design**: Built from the ground up to support rootless containers
- **Pod Support**: Native support for Kubernetes-style pods

### Podman vs Docker

| Feature | Docker | Podman |
|---------|--------|--------|
| **Architecture** | Client-Server (daemon) | Daemonless (fork-exec) |
| **Root Required** | Yes (daemon runs as root) | No (supports rootless) |
| **Security** | Daemon is attack surface | Smaller attack surface |
| **Systemd Integration** | Limited | Native |
| **Pod Support** | Through Compose | Native pods |
| **CLI Compatibility** | - | Compatible with Docker CLI |
| **Image Format** | OCI/Docker | OCI/Docker |

### Root Mode vs Rootless Mode

This is the **most important concept** to understand when working with Podman:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PODMAN EXECUTION MODES                        │
├─────────────────────────────────┬───────────────────────────────────┤
│         ROOT MODE               │         ROOTLESS MODE              │
├─────────────────────────────────┼───────────────────────────────────┤
│ • Runs as root user             │ • Runs as regular user             │
│ • Full system access            │ • Limited to user's permissions    │
│ • System-wide containers        │ • Per-user containers              │
│ • Can bind to ports < 1024      │ • Ports < 1024 need workaround     │
│ • Shared storage                │ • Isolated storage per user        │
│ • Higher performance            │ • Slightly lower performance       │
│ • Traditional Docker-like       │ • More secure                      │
├─────────────────────────────────┼───────────────────────────────────┤
│ USE WHEN:                       │ USE WHEN:                          │
│ • System services               │ • Developer workstations           │
│ • CI/CD pipelines (controlled)  │ • Multi-tenant environments        │
│ • Maximum performance needed    │ • Security is priority             │
│ • Legacy Docker workflows       │ • Kubernetes/OpenShift migration   │
└─────────────────────────────────┴───────────────────────────────────┘
```

---

## Quick Start

### Minimal Installation (5 minutes)

```yaml
---
- name: Install Podman - Quick Start
  hosts: all
  become: true
  roles:
    - code3tech.devtools.podman
```

That's it! This will:
- Install Podman, Buildah, and Skopeo
- Configure default registries (docker.io, quay.io)
- Enable rootless mode
- Apply sensible defaults

### With Rootless Users

```yaml
---
- name: Install Podman with Rootless Users
  hosts: all
  become: true
  vars:
    podman_rootless_users:
      - devuser
      - jenkins
  roles:
    - code3tech.devtools.podman
```

---

## Understanding the Modes

### Root Mode (Traditional)

When you run Podman as root (or with `sudo`):

```bash
sudo podman run alpine echo "Hello from root mode"
```

**Characteristics:**
- Containers run with root privileges inside the container
- Container processes can access host resources (with proper mapping)
- Storage location: `/var/lib/containers/storage`
- Authentication file: `/root/.config/containers/auth.json`
- Can bind to privileged ports (80, 443, etc.)

**Ansible Configuration for Root Mode:**
```yaml
# Root mode is implicit when NOT using rootless
podman_enable_rootless: false
podman_rootless_users: []  # Empty - no rootless users
```

### Rootless Mode (Recommended)

When you run Podman as a regular user:

```bash
# As regular user (no sudo)
podman run alpine echo "Hello from rootless mode"
```

**Characteristics:**
- Containers run without root privileges
- Uses user namespaces (`subuid`/`subgid`) for isolation
- Storage location: `~/.local/share/containers/storage`
- Authentication file: `~/.config/containers/auth.json` or `$XDG_RUNTIME_DIR/containers/auth.json`
- Cannot bind to ports < 1024 without additional configuration

**Ansible Configuration for Rootless Mode:**
```yaml
podman_enable_rootless: true
podman_rootless_users:
  - devuser
  - ciuser
  - appuser
```

### Mode Comparison Table

| Aspect | Root Mode | Rootless Mode |
|--------|-----------|---------------|
| **Security** | Lower (root access) | Higher (user namespace isolation) |
| **Storage Location** | `/var/lib/containers/storage` | `~/.local/share/containers/storage` |
| **Auth File** | `/root/.config/containers/auth.json` | `~/.config/containers/auth.json` |
| **Runtime Dir** | `/run/containers/storage` | `/run/user/<UID>/containers` |
| **XDG_RUNTIME_DIR** | `/run/user/0` | `/run/user/<UID>` |
| **Network** | Full access (iptables) | slirp4netns (user-space) |
| **Privileged Ports** | Yes (< 1024) | No (without workaround) |
| **Performance** | Higher | Slightly lower |
| **Shared Containers** | Yes | Per-user isolation |
| **Use Case** | System services, CI/CD | Developers, multi-tenant |

### When to Use Each Mode

#### ✅ Use Root Mode When:
- Running system-level container services
- You need maximum performance
- Binding to ports 80, 443, or other privileged ports
- Running in a controlled CI/CD environment
- Migrating from Docker (similar behavior)
- Need shared containers visible to all users

#### ✅ Use Rootless Mode When:
- Developer workstations (default recommendation)
- Multi-user systems where users shouldn't see each other's containers
- Security is a priority
- Migrating to Kubernetes/OpenShift (similar security model)
- Untrusted users need container access
- Compliance requirements demand non-root containers

#### 🔄 Hybrid Approach (Recommended for Production):
```yaml
# System services run as root
# Developer/test users run rootless
podman_enable_rootless: true
podman_rootless_users:
  - developer1
  - developer2
  - testuser
# Root mode remains available for system services
```

---

## Installation and Basic Configuration

### Minimal Installation

The simplest playbook to install Podman:

```yaml
---
- name: Podman Minimal Installation
  hosts: all
  become: true
  roles:
    - code3tech.devtools.podman
```

**What this does:**
1. Installs packages: `podman`, `buildah`, `skopeo`, `crun`
2. Configures registries: `docker.io`, `quay.io`
3. Enables rootless mode (no users configured)
4. Applies default storage configuration

### Installation with Rootless Users

```yaml
---
- name: Podman with Rootless Configuration
  hosts: all
  become: true
  vars:
    # Enable rootless mode
    podman_enable_rootless: true
    
    # Users to configure for rootless Podman
    podman_rootless_users:
      - developer
      - tester
      - ciuser
  roles:
    - code3tech.devtools.podman
```

**What this does:**
1. All steps from minimal installation
2. Configures `subuid`/`subgid` for each user
3. Creates XDG_RUNTIME_DIR for each user
4. Each user can now run `podman` without sudo

---

## Complete Variable Reference

### Package Configuration

#### `podman_packages`
**Type:** List  
**Default:**
```yaml
podman_packages:
  - podman
  - buildah
  - skopeo
  - crun  # High-performance OCI runtime
```

**Description:** Packages to install. By default includes:

| Package | Description |
|---------|-------------|
| `podman` | Main container engine |
| `buildah` | Build OCI container images |
| `skopeo` | Copy/inspect container images |
| `crun` | Fast OCI runtime (20-30% faster than runc) |

**Customization Example:**
```yaml
# Add additional tools
podman_packages:
  - podman
  - buildah
  - skopeo
  - crun
  - podman-compose  # Docker Compose compatibility
  - udica           # SELinux policy generator
```

---

### Rootless Configuration

#### `podman_enable_rootless`
**Type:** Boolean  
**Default:** `true`

**Description:** Enable rootless Podman support. When enabled, the role will:
- Configure user namespaces
- Set up subuid/subgid mappings
- Create necessary runtime directories

```yaml
# Enable rootless (recommended)
podman_enable_rootless: true

# Disable rootless (root-only mode)
podman_enable_rootless: false
```

---

#### `podman_rootless_users`
**Type:** List  
**Default:** `[]`

**Description:** Users to configure for rootless Podman. Each user will:
- Get subuid/subgid entries
- Have XDG_RUNTIME_DIR created
- Be able to run `podman` without sudo
- Have isolated container storage

```yaml
podman_rootless_users:
  - developer      # Regular developer
  - testuser       # QA/test user
  - jenkins        # CI/CD user
  - "{{ ansible_user }}"  # Current SSH user
```

**⚠️ Important:** Users MUST exist on the system before the role runs. Create users in `pre_tasks` if needed:

```yaml
pre_tasks:
  - name: Create Podman users
    ansible.builtin.user:
      name: "{{ item }}"
      shell: /bin/bash
      create_home: true
    loop:
      - developer
      - testuser
```

---

#### `podman_subuid_start` / `podman_subuid_count`
**Type:** Integer  
**Default:** `100000` / `65536`

**Description:** Defines the subuid range for rootless users.

```yaml
# Each user gets 65536 UIDs starting from 100000
podman_subuid_start: 100000
podman_subuid_count: 65536
```

**How it works:**
```
User 1: subuid 100000-165535 (65536 IDs)
User 2: subuid 165536-231071 (65536 IDs)
User 3: subuid 231072-296607 (65536 IDs)
```

**Result in `/etc/subuid`:**
```
developer:100000:65536
testuser:165536:65536
jenkins:231072:65536
```

---

#### `podman_subgid_start` / `podman_subgid_count`
**Type:** Integer  
**Default:** `100000` / `65536`

**Description:** Same as subuid but for group IDs (GIDs).

```yaml
podman_subgid_start: 100000
podman_subgid_count: 65536
```

---

### Storage Configuration

#### `podman_storage_conf`
**Type:** Dictionary  
**Default:** Performance-optimized configuration

**Description:** Complete Podman storage and engine configuration. This is where the magic happens!

```yaml
podman_storage_conf:
  # ============================================
  # STORAGE SECTION
  # ============================================
  storage:
    # Storage driver (overlay is fastest for most cases)
    driver: "overlay"
    
    # Runtime root (tmpfs for better performance)
    runroot: "/run/containers/storage"
    
    # Graph root (where images/containers are stored)
    graphroot: "/var/lib/containers/storage"
    
    options:
      overlay:
        # Mount options for overlay driver
        # metacopy=on: Reduces I/O by copying only metadata, not data
        #              Provides 30-50% I/O reduction
        mountopt: "nodev,metacopy=on"
  
  # ============================================
  # ENGINE SECTION
  # ============================================
  engine:
    # OCI Runtime: crun is 20-30% faster than runc
    runtime: "crun"
    
    # Events logger (file is more efficient than journald)
    events_logger: "file"
    
    # Cgroup manager (systemd for better integration)
    cgroup_manager: "systemd"
    
    # Number of locks for concurrent operations
    num_locks: 2048
    
    # Parallel image layer downloads
    # Higher = faster pulls on good networks
    image_parallel_copies: 10
```

**Explanation of Each Option:**

| Option | Value | Performance Impact |
|--------|-------|-------------------|
| `driver: overlay` | Best for most systems | Native, fast, copy-on-write |
| `mountopt: metacopy=on` | Copies metadata only | **+30-50% I/O reduction** |
| `runtime: crun` | C-based runtime | **+20-30% faster startup** |
| `events_logger: file` | File-based logging | Lower overhead than journald |
| `cgroup_manager: systemd` | Systemd integration | Better resource tracking |
| `num_locks: 2048` | Concurrent ops | Supports many containers |
| `image_parallel_copies: 10` | Parallel downloads | **+200-300% faster pulls** |

---

#### `podman_reset_storage_on_driver_change`
**Type:** Boolean  
**Default:** `false`

**Description:** When `true`, automatically resets storage if driver conflicts are detected.

```yaml
# Automatic reset on driver change
podman_reset_storage_on_driver_change: true
```

**⚠️ WARNING:** This will **DELETE ALL CONTAINERS AND IMAGES** on the system. Use only when:
- Migrating from another driver
- Troubleshooting storage issues
- Fresh installations

---

### Registry Configuration

#### `podman_registries_conf`
**Type:** Dictionary  
**Default:**
```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io
```

**Description:** Configures which registries to search when using unqualified image names.

```yaml
# When you run: podman pull alpine
# Podman searches in order: docker.io, quay.io, ghcr.io
podman_registries_conf:
  unqualified-search-registries:
    - docker.io      # Docker Hub
    - quay.io        # Red Hat Quay
    - ghcr.io        # GitHub Container Registry
    - gcr.io         # Google Container Registry
    - registry.company.com  # Private registry
```

**Behavior Example:**
```bash
# With the config above:
podman pull alpine
# Tries: docker.io/library/alpine
# Then: quay.io/alpine
# Then: ghcr.io/alpine
# Until found or all fail
```

---

#### `podman_insecure_registries`
**Type:** List  
**Default:** `[]`

**Description:** Registries that use HTTP or self-signed certificates.

```yaml
podman_insecure_registries:
  - "registry.internal.company.com:5000"  # HTTP registry
  - "192.168.1.100:5000"                  # IP-based registry
  - "localhost:5000"                       # Local development
```

**⚠️ Security Warning:** Only use for:
- Internal/trusted networks
- Development environments
- Air-gapped systems

**Result in `/etc/containers/registries.conf`:**
```toml
[[registry]]
location = "registry.internal.company.com:5000"
insecure = true

[[registry]]
location = "192.168.1.100:5000"
insecure = true
```

---

### Authentication Configuration

#### `podman_registries_auth`
**Type:** List  
**Default:** `[]`

**Description:** Credentials for private registry authentication. Works for both root and rootless modes.

```yaml
podman_registries_auth:
  # Docker Hub
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_dockerhub_token }}"
  
  # Quay.io
  - registry: "quay.io"
    username: "myorg+robot"
    password: "{{ vault_quay_token }}"
  
  # GitHub Container Registry
  - registry: "ghcr.io"
    username: "github-user"
    password: "{{ vault_github_token }}"
  
  # Private Enterprise Registry
  - registry: "registry.company.com"
    username: "ci-service"
    password: "{{ vault_company_registry_pass }}"
```

**Authentication Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry hostname (docker.io, quay.io, etc.) |
| `username` | string | Yes | Username or service account |
| `password` | string | Yes | Password or access token |

**⚠️ ALWAYS use Ansible Vault for passwords!**

```bash
# Create encrypted vars file
ansible-vault create vars/registry_secrets.yml

# Content:
vault_dockerhub_token: "dckr_pat_xxxxx"
vault_quay_token: "xxxxx"
vault_github_token: "ghp_xxxxx"
```

---

#### `podman_clean_credentials`
**Type:** Boolean  
**Default:** `false`

**Description:** Remove existing credentials before re-authentication. Useful when:
- Changing passwords
- Fixing "invalid credentials" errors
- Rotating service accounts

```yaml
# Enable credential cleanup
podman_clean_credentials: true
```

---

## Production Playbook Explained

This section dissects a complete production playbook line by line:

### Pre-Tasks: Environment Preparation

#### Time Synchronization

```yaml
pre_tasks:
  # ==========================================================================
  # TIME SYNCHRONIZATION - CRITICAL FOR GPG KEY VALIDATION
  # ==========================================================================
```

**Why it's needed:**
- GPG keys have validity dates
- If system clock is wrong, package installation fails
- RHEL 10+ is especially sensitive to clock skew

```yaml
  # --- RedHat-like (RHEL, CentOS, Rocky, AlmaLinux) ---
  - name: "[TimeSync] Ensure chrony is installed (RedHat)"
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
    tags: timesync
```

**Explanation:**
- `chrony` is the modern NTP client for RHEL
- More accurate than `ntpd` for containers
- Handles clock drift better in VMs

```yaml
  - name: "[TimeSync] Force time synchronization (RedHat)"
    ansible.builtin.command:
      cmd: chronyc makestep
    changed_when: false
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
```

**Explanation:**
- `chronyc makestep` forces immediate clock adjustment
- Normally chrony adjusts gradually (slew)
- `makestep` makes abrupt correction when needed

```yaml
  # --- Debian-like (Debian, Ubuntu) ---
  - name: "[TimeSync] Ensure systemd-timesyncd is installed (Debian)"
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
      cache_valid_time: 3600
    when: ansible_os_family == 'Debian'
```

**Explanation:**
- Ubuntu/Debian use `systemd-timesyncd` by default
- Lighter than chrony, sufficient for most cases
- `cache_valid_time: 3600` avoids unnecessary apt updates

---

#### Creating Test User for Rootless Validation

```yaml
  # ==========================================================================
  # CREATE UNPRIVILEGED TEST USER FOR ROOTLESS PODMAN
  # ==========================================================================
  - name: "[TestUser] Create unprivileged user for rootless Podman testing"
    ansible.builtin.user:
      name: "{{ podman_test_user }}"
      comment: "Podman Rootless Test User (no admin privileges)"
      shell: /bin/bash
      create_home: true
      state: present
    tags: testuser
```

**Why this is important:**
- Tests rootless mode with a truly unprivileged user
- Validates that no sudo/root access is needed
- Proves the security model works

```yaml
  - name: "[TestUser] Ensure test user is NOT in sudo/wheel group"
    ansible.builtin.user:
      name: "{{ podman_test_user }}"
      groups: []
      append: false
    tags: testuser
```

**Explanation:**
- Removes user from ALL groups
- Ensures no accidental privilege escalation
- `append: false` replaces groups (not adds)

```yaml
  - name: "[TestUser] Get test user UID"
    ansible.builtin.command: id -u {{ podman_test_user }}
    register: test_user_uid
    changed_when: false
```

**Why we need the UID:**
- XDG_RUNTIME_DIR is `/run/user/<UID>`
- Podman needs this for authentication files
- Must match actual user UID

---

#### Custom Storage Directory

```yaml
  - name: Create custom Podman data directory
    ansible.builtin.file:
      path: /opt/podman-data
      state: directory
      mode: '0711'
      owner: root
      group: root
```

**Why custom directory:**
- Separate from OS partition
- Can be on SSD for performance
- Easier backup/management
- `mode: '0711'` allows user traverse but not listing

---

### Role Configuration

The role is invoked with comprehensive variables:

```yaml
  vars:
    # ==========================================================================
    # ROOTLESS CONFIGURATION
    # ==========================================================================
    podman_enable_rootless: true
    
    podman_rootless_users:
      - "{{ ansible_user }}"      # SSH user (typically admin)
      - "{{ podman_test_user }}"  # Unprivileged test user
```

**Design Decision:**
- `ansible_user` = the user running Ansible (has sudo)
- `podman_test_user` = no privileges (pure rootless test)
- Both should be able to run containers

```yaml
    # ==========================================================================
    # STORAGE CONFIGURATION - PERFORMANCE FOCUSED
    # ==========================================================================
    podman_storage_conf:
      storage:
        driver: "overlay"
        # Custom directory (recommended: SSD)
        graphroot: "/opt/podman-data/storage"
        runroot: "/run/containers/storage"
        options:
          overlay:
            # metacopy=on: +30-50% I/O performance
            mountopt: "nodev,metacopy=on"
```

**Performance Impact:**
- `graphroot` on SSD = faster image operations
- `runroot` on tmpfs = faster container runtime
- `metacopy=on` = major I/O reduction

```yaml
      engine:
        # crun: 20-30% faster than runc
        runtime: "crun"
        # systemd integration for proper cleanup
        cgroup_manager: "systemd"
        # Parallel downloads (network permitting)
        image_parallel_copies: 10
```

---

### Post-Tasks: Validation

#### Basic Verification

```yaml
  post_tasks:
    - name: Verify Podman is installed
      ansible.builtin.command: podman --version
      register: podman_version_result
      changed_when: false
```

**Purpose:** Confirm installation succeeded before proceeding.

#### System Information

```yaml
    - name: Get Podman system info
      ansible.builtin.command: podman info --format json
      register: podman_info_result
      changed_when: false

    - name: Parse Podman info
      ansible.builtin.set_fact:
        podman_info: "{{ podman_info_result.stdout | from_json }}"
```

**What we extract:**
- Runtime type (crun/runc)
- Storage driver
- Graph/run root locations
- Rootless status
- Kernel version

#### Container Pull/Run Tests

```yaml
    # --- Get ansible_user UID ---
    - name: Get ansible_user UID
      ansible.builtin.command: id -u {{ ansible_user }}
      register: ansible_user_uid_result
```

**Why not use `ansible_user_uid`:**
- When using `become: true`, `ansible_user_uid` returns 0 (root)
- We need the REAL user UID for XDG_RUNTIME_DIR
- Explicit `id -u` always returns correct UID

```yaml
    - name: Ensure XDG_RUNTIME_DIR exists for ansible_user
      ansible.builtin.file:
        path: "/run/user/{{ ansible_user_uid_real }}"
        state: directory
        owner: "{{ ansible_user }}"
        group: "{{ ansible_user }}"
        mode: '0700'
```

**Critical for rootless:**
- Podman stores auth tokens here
- Must be owned by the user
- Mode 0700 for security

```yaml
    - name: Pull Alpine image (rootless)
      ansible.builtin.command: podman pull docker.io/library/alpine:latest
      become: true
      become_user: "{{ ansible_user }}"
      environment:
        XDG_RUNTIME_DIR: "/run/user/{{ ansible_user_uid_real }}"
```

**Key Points:**
- `become_user`: Switch to regular user (rootless mode)
- `XDG_RUNTIME_DIR`: Required for authentication
- Tests that pull works without sudo

```yaml
    - name: Run Alpine container test (rootless)
      ansible.builtin.command: >
        podman run --rm docker.io/library/alpine:latest 
        echo "Alpine container test - SUCCESS"
      become: true
      become_user: "{{ ansible_user }}"
      environment:
        XDG_RUNTIME_DIR: "/run/user/{{ ansible_user_uid_real }}"
```

**Validation:**
- `--rm`: Auto-remove container after exit
- Simple echo test proves containers work
- Full rootless validation

---

## Performance Optimization

### crun vs runc Runtime

| Aspect | runc | crun |
|--------|------|------|
| **Language** | Go | C |
| **Startup Time** | Baseline | 20-30% faster |
| **Memory Usage** | Higher | 30-50% lower |
| **Compatibility** | Maximum | Very high |
| **Maintenance** | Docker/Kubernetes | Red Hat |

**When to use crun:**
- High-density workloads (many containers)
- Serverless/FaaS (fast startup matters)
- Memory-constrained environments
- LXC containers (better compatibility)

**Configuration:**
```yaml
podman_storage_conf:
  engine:
    runtime: "crun"
```

---

### Storage Optimization

#### metacopy=on

```yaml
options:
  overlay:
    mountopt: "nodev,metacopy=on"
```

**What it does:**
- Only copies file metadata, not actual data
- Actual data is referenced from lower layer
- Reduces I/O by 30-50%

**Requirements:**
- Kernel 4.19+ (Ubuntu 20.04+, RHEL 8+)
- ext4 or xfs filesystem
- `overlay` driver

#### Custom Graph Root on SSD

```yaml
storage:
  graphroot: "/opt/podman-data/storage"
```

**Recommendations:**
- Use SSD for graphroot
- Keep on separate partition from OS
- Consider LVM for easier management
- Monitor space usage

---

### Parallel Downloads

```yaml
engine:
  image_parallel_copies: 10
```

**Effect:**
- Downloads 10 layers simultaneously
- Reduces pull time by 200-300%
- Depends on network bandwidth

**Tuning:**
```yaml
# Fast network (1Gbps+)
image_parallel_copies: 20

# Slow network (100Mbps)
image_parallel_copies: 5

# Very slow network
image_parallel_copies: 3
```

---

## Security Best Practices

### 1. Always Use Ansible Vault for Credentials

```bash
# Create vault
ansible-vault create vars/secrets.yml

# Run with vault
ansible-playbook playbook.yml --ask-vault-pass
```

### 2. Prefer Rootless Mode

```yaml
podman_enable_rootless: true
podman_rootless_users:
  - developer1
  - developer2
```

### 3. Limit Insecure Registries

```yaml
# Only for internal/trusted networks
podman_insecure_registries:
  - "internal-registry.company.local:5000"
```

### 4. Use Access Tokens, Not Passwords

- Docker Hub: Use Access Tokens
- GitHub: Use PATs with minimal scope
- Quay: Use Robot Accounts

### 5. Regular Credential Rotation

```yaml
# When rotating credentials
podman_clean_credentials: true
```

---

## Troubleshooting

### Common Error: XDG_RUNTIME_DIR Not Owned

```
Error: XDG_RUNTIME_DIR directory "/run/user/0" is not owned by the current user
```

**Cause:** Running as user but XDG_RUNTIME_DIR points to root's directory.

**Solution:**
```yaml
- name: Get real user UID
  ansible.builtin.command: id -u {{ ansible_user }}
  register: real_uid

- name: Set environment
  environment:
    XDG_RUNTIME_DIR: "/run/user/{{ real_uid.stdout }}"
```

### Common Error: Storage Driver Mismatch

```
Error: database configuration mismatch
```

**Cause:** Changing storage drivers without reset.

**Solution:**
```yaml
podman_reset_storage_on_driver_change: true
```

Or manually:
```bash
podman system reset --force
```

### Common Error: Permission Denied on Auth File

```
Error: permission denied reading auth.json
```

**Cause:** Auth file created as root, user can't read.

**Solution:** The role handles this automatically, but manual fix:
```bash
sudo chown $USER:$USER ~/.config/containers/auth.json
```

### Common Error: subuid/subgid Not Configured

```
Error: cannot find UID/GID for user
```

**Cause:** User not in `/etc/subuid` or `/etc/subgid`.

**Solution:** Ensure user is in `podman_rootless_users`:
```yaml
podman_rootless_users:
  - myuser
```

---

## Complete Examples

### Example 1: Development Workstation

```yaml
---
- name: Podman for Developers
  hosts: workstations
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
    
    podman_registries_auth:
      - registry: "ghcr.io"
        username: "{{ github_user }}"
        password: "{{ vault_github_token }}"
  
  roles:
    - code3tech.devtools.podman
```

### Example 2: CI/CD Pipeline Server

```yaml
---
- name: Podman for CI/CD
  hosts: ci_servers
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - jenkins
      - gitlab-runner
    
    podman_storage_conf:
      storage:
        graphroot: "/data/podman/storage"
      engine:
        runtime: "crun"
        image_parallel_copies: 20
    
    podman_registries_auth:
      - registry: "docker.io"
        username: "{{ dockerhub_user }}"
        password: "{{ vault_dockerhub_token }}"
      - registry: "registry.company.com"
        username: "ci-service"
        password: "{{ vault_company_token }}"
  
  roles:
    - code3tech.devtools.podman
```

### Example 3: Production with Full Optimization

See the complete production playbook at:
[playbooks/podman/install-podman.yml](../../playbooks/podman/install-podman.yml)

---

## See Also

- [Registry Authentication Guide](REGISTRY_AUTHENTICATION.md) - Complete registry auth documentation
- [Podman Role README](../../roles/podman/README.md) - Role reference
- [Variables Reference](../reference/VARIABLES.md) - Complete variables list
- [FAQ](../FAQ.md) - Frequently asked questions

---

## External References

- [Podman Official Documentation](https://docs.podman.io/)
- [Podman Rootless Mode](https://github.com/containers/podman/blob/main/rootless.md)
- [crun vs runc Comparison](https://developers.redhat.com/blog/2019/01/29/podman-runtime-crun)
- [Red Hat Container Tools](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/building_running_and_managing_containers/)

---

[← Back to User Guides](README.md)
