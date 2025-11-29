# asdf Complete Guide - Multi-Version Runtime Management

A comprehensive guide to installing and configuring asdf version manager with the `code3tech.devtools` Ansible collection. This guide covers everything from basic concepts to production deployment with multi-user support.

## 📋 Table of Contents

- [Overview](#overview)
  - [What is asdf?](#what-is-asdf)
  - [asdf Architecture](#asdf-architecture)
  - [asdf vs Other Version Managers](#asdf-vs-other-version-managers)
- [Quick Start](#quick-start)
- [Installation and Basic Configuration](#installation-and-basic-configuration)
  - [Minimal Installation](#minimal-installation)
  - [Installation with Plugins](#installation-with-plugins)
- [Complete Variable Reference](#complete-variable-reference)
  - [Basic Configuration](#basic-configuration)
  - [User Configuration](#user-configuration)
  - [Plugin Configuration](#plugin-configuration)
  - [Shell Configuration](#shell-configuration)
- [Production Playbook Explained](#production-playbook-explained)
  - [Pre-Tasks: Environment Preparation](#pre-tasks-environment-preparation)
  - [Role Configuration](#role-configuration)
  - [Post-Tasks: Validation](#post-tasks-validation)
- [Plugin Management](#plugin-management)
  - [Lightweight Plugins](#lightweight-plugins)
  - [Heavy Plugins](#heavy-plugins)
  - [Plugin Installation Times](#plugin-installation-times)
- [Multi-User Configuration](#multi-user-configuration)
  - [Group-Based Architecture](#group-based-architecture)
  - [User Shell Configuration](#user-shell-configuration)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Complete Examples](#complete-examples)

---

## Overview

### What is asdf?

asdf is an **extendable version manager** that allows you to manage multiple runtime versions for different programming languages and tools with a single CLI. Key characteristics:

- **Single CLI**: One tool to manage Node.js, Python, Ruby, Go, Rust, and 300+ more
- **Plugin-Based**: Each language/tool is a plugin
- **Per-Project Versions**: Use `.tool-versions` file to pin versions per project
- **Shell Integration**: Works with bash, zsh, and fish
- **No Root Required**: Versions installed in user space

### asdf Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ASDF ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────────────────────────────────────────────────────────┐ │
│    │                    /opt/asdf (System-Wide)                    │ │
│    │  ┌────────────────────────────────────────────────────────┐  │ │
│    │  │  bin/asdf              # Main binary                    │  │ │
│    │  │  plugins/              # Installed plugins              │  │ │
│    │  │  installs/             # Installed versions             │  │ │
│    │  │  shims/                # Shim executables               │  │ │
│    │  └────────────────────────────────────────────────────────┘  │ │
│    └──────────────────────────────────────────────────────────────┘ │
│                                  │                                   │
│                                  │ Group: asdf                       │
│                                  │ Permissions: 0775                 │
│                                  ▼                                   │
│    ┌──────────────────────────────────────────────────────────────┐ │
│    │                       User Access                             │ │
│    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │ │
│    │  │   User A     │  │   User B     │  │   User C     │       │ │
│    │  │ (asdf group) │  │ (asdf group) │  │ (asdf group) │       │ │
│    │  │   ~/.bashrc  │  │   ~/.zshrc   │  │   ~/.bashrc  │       │ │
│    │  └──────────────┘  └──────────────┘  └──────────────┘       │ │
│    └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│    ┌──────────────────────────────────────────────────────────────┐ │
│    │                   System-Wide PATH                            │ │
│    │  /etc/profile.d/asdf.sh                                       │ │
│    │  - Sets ASDF_DIR and ASDF_DATA_DIR                           │ │
│    │  - Adds shims to PATH                                         │ │
│    └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### asdf vs Other Version Managers

| Feature | asdf | nvm | pyenv | rbenv |
|---------|------|-----|-------|-------|
| **Languages** | 300+ plugins | Node.js only | Python only | Ruby only |
| **Single CLI** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Per-Project Versions** | ✅ `.tool-versions` | ✅ `.nvmrc` | ✅ `.python-version` | ✅ `.ruby-version` |
| **Shell Support** | bash, zsh, fish | bash, zsh | bash, zsh | bash, zsh |
| **Plugin Ecosystem** | ✅ Extensive | ❌ N/A | ❌ N/A | ❌ N/A |
| **Learning Curve** | Low | Low | Low | Low |

**Why asdf?**
- **One tool to rule them all**: No need to learn multiple version managers
- **Consistent interface**: Same commands for all languages
- **Team standardization**: Share `.tool-versions` in repositories
- **CI/CD friendly**: Reproducible builds with exact versions

---

## Quick Start

### Minimal Installation (2 minutes)

```yaml
---
- name: Install asdf - Quick Start
  hosts: all
  become: true
  roles:
    - code3tech.devtools.asdf
```

That's it! This will:
- Install asdf binary in `/opt/asdf`
- Create `asdf` group for shared access
- Configure system-wide PATH
- Ready for plugin installation

### With Plugins (5-15 minutes)

```yaml
---
- name: Install asdf with Plugins
  hosts: all
  become: true
  vars:
    asdf_users:
      - developer
    asdf_plugins:
      - name: "nodejs"
        versions: ["22.11.0"]
        global: "22.11.0"
      - name: "python"
        versions: ["3.13.0"]
        global: "3.13.0"
  roles:
    - code3tech.devtools.asdf
```

---

## Installation and Basic Configuration

### Minimal Installation

The simplest playbook to install asdf:

```yaml
---
- name: asdf Minimal Installation
  hosts: all
  become: true
  roles:
    - code3tech.devtools.asdf
```

**What this does:**
1. Downloads asdf binary from GitHub releases
2. Installs to `/opt/asdf`
3. Creates `asdf` group for multi-user access
4. Configures `/etc/profile.d/asdf.sh` for system-wide PATH
5. Installs system dependencies (git, curl, etc.)

### Installation with Plugins

```yaml
---
- name: asdf with Development Tools
  hosts: all
  become: true
  vars:
    asdf_users:
      - developer
      - devops
    asdf_plugins:
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
      - name: "nodejs"
        versions: ["22.11.0", "20.18.0"]
        global: "22.11.0"
  roles:
    - code3tech.devtools.asdf
```

**What this does:**
1. All steps from minimal installation
2. Adds specified users to `asdf` group
3. Installs plugins centrally (shared by all users)
4. Installs specified versions
5. Sets global versions for each plugin
6. Configures user shell profiles

---

## Complete Variable Reference

### Basic Configuration

#### `asdf_version`
**Type:** String  
**Default:** `"latest"`

**Description:** asdf version to install.

| Value | Description |
|-------|-------------|
| `latest` | Downloads latest release from GitHub |
| `v0.18.0` | Specific version tag |

```yaml
asdf_version: "latest"      # Always get latest
asdf_version: "v0.18.0"     # Pin to specific version
```

---

#### `asdf_install_dir`
**Type:** String  
**Default:** `"/opt/asdf"`

**Description:** System-wide installation directory.

```yaml
asdf_install_dir: "/opt/asdf"          # Default
asdf_install_dir: "/usr/local/asdf"    # Alternative location
```

**Directory Structure:**
```
/opt/asdf/
├── bin/
│   └── asdf              # Main binary
├── plugins/              # Installed plugins
│   ├── nodejs/
│   ├── python/
│   └── ...
├── installs/             # Installed versions
│   ├── nodejs/
│   │   ├── 22.11.0/
│   │   └── 20.18.0/
│   └── python/
│       └── 3.13.0/
└── shims/                # Shim executables
    ├── node
    ├── npm
    ├── python
    └── pip
```

---

#### `asdf_data_dir`
**Type:** String  
**Default:** `""` (uses `asdf_install_dir`)

**Description:** Custom data directory for plugins and installs.

```yaml
# Use default (same as install dir)
asdf_data_dir: ""

# Custom data directory (e.g., on faster storage)
asdf_data_dir: "/data/asdf"
```

**When to use custom data directory:**
- Separate SSD for faster builds
- Shared storage in NFS environments
- Separate backup requirements

---

#### `asdf_install_dependencies`
**Type:** Boolean  
**Default:** `true`

**Description:** Install system dependencies required by asdf and plugins.

```yaml
asdf_install_dependencies: true   # Install git, curl, build tools, etc.
asdf_install_dependencies: false  # Skip if already installed
```

**Installed Dependencies:**
- **All systems:** git, curl, unzip
- **Debian/Ubuntu:** build-essential, libssl-dev, libffi-dev
- **RHEL/Rocky:** gcc, make, openssl-devel

---

### User Configuration

#### `asdf_users`
**Type:** List  
**Default:** `[]`

**Description:** Users to add to the `asdf` group for shared access.

```yaml
asdf_users:
  - developer           # Development user
  - jenkins             # CI/CD user
  - deploy              # Deployment user
  - "{{ ansible_user }}" # Current SSH user
```

**What happens for each user:**
1. Added to `asdf` group
2. Shell profile configured (based on `asdf_shell_profile`)
3. Access to all installed plugins and versions

**Note:** Users must exist on the system before running the role.

---

### Plugin Configuration

#### `asdf_plugins`
**Type:** List  
**Default:** `[]`

**Description:** Centralized plugin configuration for all users.

```yaml
asdf_plugins:
  # Lightweight plugin (fast installation ~5-10 seconds)
  - name: "direnv"
    versions:
      - "2.35.0"
    global: "2.35.0"
  
  # Heavy plugin (compilation required ~3-8 minutes)
  - name: "nodejs"
    versions:
      - "22.11.0"      # Latest LTS
      - "20.18.0"      # Previous LTS
    global: "22.11.0"  # Default version
  
  # Multiple versions for testing
  - name: "python"
    versions:
      - "3.13.0"       # Latest
      - "3.12.7"       # Stable
      - "3.11.10"      # LTS
    global: "3.13.0"
```

**Plugin Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Plugin name (as in `asdf plugin add <name>`) |
| `versions` | List | Yes | Versions to install |
| `global` | String | No | Global version (default for all users) |

**Finding Plugin Names:**
```bash
# List all available plugins
asdf plugin list all

# Search for a plugin
asdf plugin list all | grep python
```

---

### Shell Configuration

#### `asdf_shell_profile`
**Type:** String  
**Default:** `"bashrc"`

**Description:** Shell profile file to configure.

| Value | File | Shell |
|-------|------|-------|
| `bashrc` | `~/.bashrc` | Bash |
| `zshrc` | `~/.zshrc` | Zsh |
| `config/fish/config.fish` | `~/.config/fish/config.fish` | Fish |

```yaml
asdf_shell_profile: "bashrc"                    # For bash users
asdf_shell_profile: "zshrc"                     # For zsh users
asdf_shell_profile: "config/fish/config.fish"  # For fish users
```

**What gets configured:**
```bash
# Added to ~/.bashrc (example)
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

#### `asdf_configure_shell`
**Type:** Boolean  
**Default:** `true`

**Description:** Whether to configure shell profiles automatically.

```yaml
asdf_configure_shell: true   # Configure user shells
asdf_configure_shell: false  # Skip shell configuration
```

---

## Production Playbook Explained

This section dissects a complete production playbook line by line.

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
- RHEL 9+ is especially sensitive to clock skew

```yaml
  - name: "[TimeSync] Ensure chrony is installed (RedHat)"
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']

  - name: "[TimeSync] Force time synchronization (RedHat)"
    ansible.builtin.command:
      cmd: chronyc makestep
    changed_when: false
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
```

```yaml
  - name: "[TimeSync] Ensure systemd-timesyncd is installed (Debian)"
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
    when: ansible_os_family == 'Debian'
```

---

#### System Requirements Check

```yaml
  - name: "[PreCheck] Verify internet connectivity"
    ansible.builtin.uri:
      url: "https://github.com"
      method: GET
      timeout: 10
    register: internet_check
    failed_when: false
```

**Purpose:** asdf downloads plugins from GitHub, so connectivity is essential.

```yaml
  - name: "[PreCheck] Check available disk space"
    ansible.builtin.command: df -h /opt
    register: disk_space
```

**Purpose:** Heavy plugins (nodejs, python) require significant disk space.

---

#### User Validation

```yaml
  - name: "[UserCheck] Verify configured users exist"
    ansible.builtin.getent:
      database: passwd
      key: "{{ item }}"
    loop: "{{ asdf_users }}"
    register: user_check
    failed_when: false
```

**Purpose:** Role requires users to exist before adding to asdf group.

---

### Role Configuration

The role is invoked with comprehensive variables:

```yaml
  vars:
    # ==========================================================================
    # BASIC CONFIGURATION
    # ==========================================================================
    asdf_version: "latest"
    asdf_install_dir: "/opt/asdf"
    asdf_install_dependencies: true
    asdf_configure_shell: true
    asdf_shell_profile: "bashrc"
```

**Key Settings:**
- `asdf_version: "latest"` - Always get newest asdf
- `asdf_install_dir: "/opt/asdf"` - System-wide installation
- `asdf_install_dependencies: true` - Install build tools for compilation

```yaml
    # ==========================================================================
    # USER CONFIGURATION (CENTRALIZED APPROACH)
    # ==========================================================================
    asdf_users:
      - "{{ ansible_user }}"
      # - "deploy"
      # - "jenkins"
```

**Centralized Approach:**
- All users get same plugins
- No per-user plugin configuration needed
- Group-based permissions (asdf group)

```yaml
    # ==========================================================================
    # PLUGIN CONFIGURATION (CENTRALIZED)
    # ==========================================================================
    asdf_plugins:
      # Lightweight plugins (fast)
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
      
      # Heavy plugins (require compilation)
      - name: "nodejs"
        versions: ["22.11.0", "20.18.0"]
        global: "22.11.0"
      
      - name: "python"
        versions: ["3.13.0", "3.12.7"]
        global: "3.13.0"
```

**Plugin Categories:**
- **Lightweight** (5-15 seconds): direnv, jq, yq, kubectl, helm
- **Heavy** (2-30 minutes): nodejs, python, ruby, golang, rust

---

### Post-Tasks: Validation

#### Basic Verification

```yaml
  post_tasks:
    - name: "[Verify] Check asdf installation"
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
      register: asdf_version_result
```

**Purpose:** Confirm asdf binary is installed and functional.

#### Plugin Validation

```yaml
    - name: "[Verify] List installed plugins"
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf plugin list"
      register: installed_plugins
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
```

**Purpose:** Verify all requested plugins were installed.

#### Functionality Tests

```yaml
    - name: "[FuncTest] Test nodejs functionality"
      ansible.builtin.command: "{{ asdf_install_dir }}/shims/node --version"
      register: nodejs_test
      environment:
        ASDF_DIR: "{{ asdf_install_dir }}"
        ASDF_DATA_DIR: "{{ asdf_install_dir }}"
      when: "'nodejs' in (asdf_plugins | map(attribute='name') | list)"
```

**Purpose:** Verify shims work and correct versions are active.

#### User Access Validation

```yaml
    - name: "[UserTest] Test user access to asdf"
      ansible.builtin.command: "{{ asdf_install_dir }}/bin/asdf --version"
      become: true
      become_user: "{{ item }}"
      loop: "{{ asdf_users }}"
      register: user_asdf_test
```

**Purpose:** Ensure all configured users can access asdf.

---

## Plugin Management

### Lightweight Plugins

**Installation Time:** ~5-15 seconds each

These plugins download pre-compiled binaries:

| Plugin | Description | Use Case |
|--------|-------------|----------|
| **direnv** | Environment variable manager | Per-directory env vars |
| **jq** | JSON processor | JSON manipulation in scripts |
| **yq** | YAML processor | YAML manipulation in scripts |
| **kubectl** | Kubernetes CLI | K8s cluster management |
| **helm** | K8s package manager | K8s deployments |
| **terraform** | Infrastructure as Code | Cloud provisioning |
| **awscli** | AWS CLI | AWS management |
| **gcloud** | Google Cloud CLI | GCP management |

**Example Configuration:**
```yaml
asdf_plugins:
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
  - name: "jq"
    versions: ["1.7.1"]
    global: "1.7.1"
  - name: "kubectl"
    versions: ["1.31.0"]
    global: "1.31.0"
```

### Heavy Plugins

**Installation Time:** ~2-30 minutes each

These plugins compile from source:

| Plugin | Time | Description | Requirements |
|--------|------|-------------|--------------|
| **nodejs** | 3-8 min | JavaScript runtime | gcc, make |
| **python** | 2-7 min | Python interpreter | gcc, libssl-dev, libffi-dev |
| **ruby** | 5-15 min | Ruby interpreter | gcc, make, libssl-dev |
| **golang** | 2-5 min | Go compiler | gcc (minimal) |
| **rust** | 10-30 min | Rust toolchain | gcc, make, curl |

**Example Configuration:**
```yaml
asdf_plugins:
  - name: "nodejs"
    versions:
      - "22.11.0"    # Latest LTS
      - "20.18.0"    # Previous LTS
    global: "22.11.0"
  
  - name: "python"
    versions:
      - "3.13.0"     # Latest
      - "3.12.7"     # Stable
    global: "3.13.0"
```

### Plugin Installation Times

| Scenario | Time | Plugins |
|----------|------|---------|
| **Minimal (binary only)** | ~10-20s | None |
| **Lightweight tools** | ~15-30s | direnv, jq, yq |
| **DevOps tools** | ~30-60s | kubectl, helm, terraform |
| **Node.js (1 version)** | ~3-8 min | nodejs |
| **Python (1 version)** | ~2-7 min | python |
| **Full development stack** | ~10-20 min | nodejs, python, ruby |

---

## Multi-User Configuration

### Group-Based Architecture

The role uses a **centralized group-based approach**:

```
┌────────────────────────────────────────────────────────────────────┐
│                    CENTRALIZED APPROACH                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   /opt/asdf/                                                        │
│   ├── Owner: root                                                   │
│   ├── Group: asdf                                                   │
│   ├── Mode: 0775                                                    │
│   │                                                                 │
│   ├── plugins/       ←── All plugins shared                        │
│   ├── installs/      ←── All versions shared                       │
│   └── shims/         ←── All shims shared                          │
│                                                                     │
│   Users:                                                            │
│   ├── developer  (asdf group) ──────────────────────────────────┐  │
│   ├── devops     (asdf group) ──── All users access same ───────┤  │
│   └── jenkins    (asdf group) ──── plugins and versions ────────┘  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **No duplication**: Plugins installed once, used by all
- **No conflicts**: Group permissions prevent access issues
- **Simplified management**: Central configuration
- **Disk efficient**: Single installation, multiple users

**Configuration:**
```yaml
asdf_users:
  - developer
  - devops
  - jenkins

asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
  # All users get nodejs 22.11.0
```

### User Shell Configuration

Each user gets shell configuration based on `asdf_shell_profile`:

**Bash (~/.bashrc):**
```bash
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

**Zsh (~/.zshrc):**
```zsh
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
fpath=($ASDF_DIR/completions $fpath)
autoload -Uz compinit && compinit
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

**Fish (~/.config/fish/config.fish):**
```fish
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
set -gx ASDF_DIR "/opt/asdf"
set -gx ASDF_DATA_DIR "/opt/asdf"
fish_add_path "$ASDF_DIR/bin" "$ASDF_DIR/shims"
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

---

## Performance Optimization

### 1. Use SSD for Installation Directory

```yaml
asdf_install_dir: "/opt/asdf"      # On SSD
asdf_data_dir: "/fast-ssd/asdf"    # Even faster storage
```

**Expected Improvement:** 30-50% faster plugin compilation

### 2. Choose Lightweight Plugins for Testing

```yaml
# ⚡ Fast (10-15 seconds)
asdf_plugins:
  - name: "direnv"
    versions: ["2.35.0"]
    global: "2.35.0"
  - name: "jq"
    versions: ["1.7.1"]
    global: "1.7.1"

# 🐢 Slow (5-15 minutes)
asdf_plugins:
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
```

### 3. Install Only Needed Versions

```yaml
# ❌ Too many versions (slow)
asdf_plugins:
  - name: "python"
    versions:
      - "3.13.0"
      - "3.12.7"
      - "3.11.10"
      - "3.10.15"
      - "3.9.20"
    global: "3.13.0"

# ✅ Only what you need (fast)
asdf_plugins:
  - name: "python"
    versions:
      - "3.13.0"      # Latest
      - "3.12.7"      # Fallback
    global: "3.13.0"
```

### 4. Use .tool-versions for Per-Project

Instead of installing many versions globally, use `.tool-versions`:

```bash
# In project directory
cat .tool-versions
nodejs 20.18.0
python 3.12.7

# Developers run:
asdf install
# Only installs versions they don't have
```

### 5. Prune Unused Versions

```bash
# List all installed versions
asdf list

# Uninstall unused version
asdf uninstall nodejs 18.0.0

# Check disk usage
du -sh /opt/asdf/installs/*
```

---

## Security Best Practices

### 1. Limit Group Membership

```yaml
# Only add TRUSTED users
asdf_users:
  - developer
  - jenkins
  # NOT: temp-contractor, guest, etc.
```

### 2. Use Specific Versions in Production

```yaml
# ❌ Don't use "latest" in production
asdf_version: "latest"

# ✅ Pin specific versions
asdf_version: "v0.18.0"
```

### 3. Verify Plugin Sources

```bash
# Check plugin source
asdf plugin list all | grep nodejs
# nodejs  https://github.com/asdf-vm/asdf-nodejs.git
```

Only use plugins from trusted sources (official asdf-vm repos or verified maintainers).

### 4. Use .tool-versions for Reproducibility

```bash
# In repository root
cat .tool-versions
nodejs 22.11.0
python 3.13.0

# CI/CD runs:
asdf install  # Gets exact versions
```

### 5. Regular Updates

```bash
# Update asdf
asdf update

# Update all plugins
asdf plugin update --all

# Update specific plugin
asdf plugin update nodejs
```

---

## Troubleshooting

### Common Error: Shim Not Found

```
command not found: node
```

**Cause:** Shell not configured or PATH not updated.

**Solution:**
```bash
# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Verify PATH
echo $PATH | grep asdf

# Manual fix
export PATH="/opt/asdf/shims:/opt/asdf/bin:$PATH"
```

---

### Common Error: Permission Denied

```
Permission denied: /opt/asdf/plugins/nodejs
```

**Cause:** User not in asdf group.

**Solution:**
```yaml
asdf_users:
  - myuser
```

Or manually:
```bash
sudo usermod -aG asdf myuser
newgrp asdf
```

---

### Common Error: Plugin Not Found

```
No such plugin: my-plugin
```

**Cause:** Plugin name incorrect or not in registry.

**Solution:**
```bash
# List available plugins
asdf plugin list all

# Search for plugin
asdf plugin list all | grep python
```

---

### Common Error: Version Not Found

```
version 99.99.99 not found
```

**Cause:** Requested version doesn't exist.

**Solution:**
```bash
# List available versions
asdf list all nodejs

# Install valid version
asdf install nodejs 22.11.0
```

---

### Common Error: Build Failed (Heavy Plugins)

```
BUILD FAILED: missing dependency
```

**Cause:** Missing system dependencies.

**Solution:**
```yaml
asdf_install_dependencies: true  # Enable in role
```

Or manually:
```bash
# Debian/Ubuntu
sudo apt install build-essential libssl-dev libffi-dev

# RHEL/Rocky
sudo dnf install gcc make openssl-devel
```

---

### Common Error: Old asdf Version

```
asdf: command 'set' is not known
```

**Cause:** Using old asdf command syntax.

**Solution:**
```bash
# Update asdf
asdf update

# Use new syntax (v0.16.0+)
asdf set nodejs 22.11.0  # Not 'asdf global'
```

---

### Common Error: Reshim Needed

```
node: command not found (but installed)
```

**Cause:** Shims not regenerated after package installation.

**Solution:**
```bash
# Reshim specific plugin
asdf reshim nodejs

# Reshim all plugins
asdf reshim
```

---

## Complete Examples

### Example 1: Development Workstation

```yaml
---
- name: asdf for Developers
  hosts: workstations
  become: true
  
  vars:
    asdf_users:
      - developer
    
    asdf_plugins:
      - name: "nodejs"
        versions: ["22.11.0", "20.18.0"]
        global: "22.11.0"
      - name: "python"
        versions: ["3.13.0", "3.12.7"]
        global: "3.13.0"
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
    
    asdf_shell_profile: "zshrc"  # Developers use zsh
  
  roles:
    - code3tech.devtools.asdf
```

### Example 2: CI/CD Pipeline Server

```yaml
---
- name: asdf for CI/CD
  hosts: ci_servers
  become: true
  
  vars:
    asdf_users:
      - jenkins
      - gitlab-runner
    
    asdf_plugins:
      - name: "nodejs"
        versions: ["22.11.0"]
        global: "22.11.0"
      - name: "python"
        versions: ["3.13.0"]
        global: "3.13.0"
      - name: "terraform"
        versions: ["1.9.0"]
        global: "1.9.0"
      - name: "kubectl"
        versions: ["1.31.0"]
        global: "1.31.0"
    
    asdf_shell_profile: "bashrc"
  
  roles:
    - code3tech.devtools.asdf
```

### Example 3: DevOps Tooling (Lightweight)

```yaml
---
- name: asdf DevOps Tools
  hosts: ops_servers
  become: true
  
  vars:
    asdf_users:
      - devops
    
    asdf_plugins:
      - name: "direnv"
        versions: ["2.35.0"]
        global: "2.35.0"
      - name: "jq"
        versions: ["1.7.1"]
        global: "1.7.1"
      - name: "yq"
        versions: ["4.44.3"]
        global: "4.44.3"
      - name: "kubectl"
        versions: ["1.31.0"]
        global: "1.31.0"
      - name: "helm"
        versions: ["3.16.0"]
        global: "3.16.0"
      - name: "terraform"
        versions: ["1.9.0"]
        global: "1.9.0"
  
  roles:
    - code3tech.devtools.asdf
```

### Example 4: Production with Full Optimization

For a complete production playbook with all features, see the example playbooks directory:
[playbooks/asdf/](../../playbooks/asdf/) - Contains production-ready examples

---

## See Also

- [asdf Role README](../../roles/asdf/README.md) - Role reference
- [Variables Reference](../reference/VARIABLES.md) - Complete variables list
- [FAQ](../FAQ.md) - Frequently asked questions
- [Example Playbooks](../../playbooks/asdf/) - Ready-to-use examples

---

## External References

- [asdf Official Documentation](https://asdf-vm.com/)
- [asdf GitHub Repository](https://github.com/asdf-vm/asdf)
- [asdf Plugins Directory](https://github.com/asdf-vm/asdf-plugins)
- [.tool-versions Format](https://asdf-vm.com/manage/configuration.html)

---

[← Back to User Guides](README.md)

**Performance Tip:** For testing, use lightweight plugins (direnv, jq). For production, install only the versions you need! ⚡
