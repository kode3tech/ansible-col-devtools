# Multi-User Configuration

Guide to configuring asdf for multiple users with the centralized group-based architecture.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [User Configuration](#user-configuration)
- [Shell Profile Configuration](#shell-profile-configuration)
- [Group Permissions](#group-permissions)
- [Per-User Customization](#per-user-customization)
- [Mixed Shell Environments](#mixed-shell-environments)

---

## Architecture Overview

The asdf role uses a **centralized group-based architecture**:

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

### Benefits of Centralized Architecture

| Benefit | Description |
|---------|-------------|
| **No duplication** | Plugins installed once, used by all |
| **Disk efficient** | Single installation, multiple users |
| **Simplified management** | Central configuration |
| **No conflicts** | Group permissions prevent access issues |
| **Consistent versions** | All users get same default versions |

### Comparison: Centralized vs Per-User

| Aspect | Centralized (This Role) | Per-User |
|--------|------------------------|----------|
| Installation location | `/opt/asdf` | `~/.asdf` per user |
| Disk usage | Low (single copy) | High (copies per user) |
| Plugin management | Single configuration | Per-user configuration |
| Version consistency | Guaranteed | User-dependent |
| Administration | Easy | Complex |
| User isolation | Shared plugins | Isolated plugins |

---

## User Configuration

### Basic User Setup

Configure users to have asdf access:

```yaml
---
- name: Multi-User asdf Setup
  hosts: all
  become: true
  
  vars:
    asdf_users:
      - developer       # Development user
      - devops          # DevOps engineer
      - jenkins         # CI/CD service account
      - deploy          # Deployment user
    
    asdf_plugins:
      - name: "nodejs"
        versions: ["22.11.0"]
        global: "22.11.0"
  
  roles:
    - code3tech.devtools.asdf
```

### Dynamic User Configuration

Use Ansible facts for dynamic configuration:

```yaml
vars:
  asdf_users:
    - "{{ ansible_user }}"              # Current SSH user
    - "{{ lookup('env', 'DEPLOY_USER') | default('deploy', true) }}"
```

### User Prerequisites

**Important:** Users must exist before running the role.

```yaml
pre_tasks:
  - name: Ensure users exist
    ansible.builtin.user:
      name: "{{ item }}"
      state: present
      shell: /bin/bash
    loop: "{{ asdf_users }}"
```

### What Happens for Each User

When you add a user to `asdf_users`, the role:

1. **Adds user to `asdf` group** - Enables access to `/opt/asdf`
2. **Configures shell profile** - Adds asdf to PATH
3. **Verifies access** - Tests user can run asdf commands

---

## Shell Profile Configuration

### Supported Shells

The role supports three shell profiles:

| Shell | Profile Variable | File Path |
|-------|-----------------|-----------|
| **Bash** | `bashrc` | `~/.bashrc` |
| **Zsh** | `zshrc` | `~/.zshrc` |
| **Fish** | `config/fish/config.fish` | `~/.config/fish/config.fish` |

### Setting Shell Profile

```yaml
vars:
  asdf_shell_profile: "bashrc"   # For bash users (default)
  # asdf_shell_profile: "zshrc"  # For zsh users
  # asdf_shell_profile: "config/fish/config.fish"  # For fish users
```

### Shell Configuration Content

**Bash/Zsh (~/.bashrc or ~/.zshrc):**

```bash
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

**Fish (~/.config/fish/config.fish):**

```fish
# BEGIN ANSIBLE MANAGED BLOCK - asdf configuration
set -gx ASDF_DIR "/opt/asdf"
set -gx ASDF_DATA_DIR "/opt/asdf"
set -gx PATH "$ASDF_DIR/bin" "$ASDF_DIR/shims" $PATH
# END ANSIBLE MANAGED BLOCK - asdf configuration
```

### System-Wide Configuration

Additionally, a system-wide script is created in `/etc/profile.d/asdf.sh`:

```bash
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
```

This ensures asdf is available even if user profile configuration fails.

### Disabling Shell Configuration

To skip shell configuration (handle manually):

```yaml
vars:
  asdf_configure_shell: false
```

---

## Group Permissions

### The asdf Group

The role creates an `asdf` group with special permissions:

```bash
# Check group
getent group asdf
# Output: asdf:x:1001:developer,devops,jenkins

# Verify permissions
ls -la /opt/asdf
# drwxrwxr-x root asdf /opt/asdf
```

### Permission Structure

```
/opt/asdf/
├── Mode: 0775 (rwxrwxr-x)
│   ├── Owner (root): read, write, execute
│   ├── Group (asdf): read, write, execute
│   └── Others: read, execute
│
├── plugins/    # 0775 - Group can add plugins
├── installs/   # 0775 - Group can install versions
└── shims/      # 0775 - Group can update shims
```

### Verifying User Access

```bash
# Check user's groups
groups developer
# developer : developer asdf

# Test asdf access
sudo -u developer asdf --version
sudo -u developer asdf plugin list
sudo -u developer node --version
```

---

## Per-User Customization

### Local Version Overrides

While plugins are shared, users can set local versions:

```bash
# As developer user
cd ~/my-project
asdf local nodejs 20.18.0

# Creates .tool-versions in current directory
cat .tool-versions
# nodejs 20.18.0
```

### User-Specific .tool-versions

Each user can have their own default versions:

```bash
# In user's home directory
cat ~/.tool-versions
nodejs 20.18.0
python 3.12.7
```

### Project-Level Configuration

Projects can specify exact versions:

```bash
# In project root
cat /path/to/project/.tool-versions
nodejs 20.18.0
python 3.12.7
terraform 1.8.0
```

### Version Resolution Priority

asdf resolves versions in this order:

```
1. ASDF_*_VERSION env variable (highest priority)
2. .tool-versions in current directory
3. .tool-versions in parent directories (recursive)
4. .tool-versions in home directory
5. Global version (asdf global)
6. System version (lowest priority)
```

---

## Mixed Shell Environments

### Handling Multiple Shells

When users have different shells, configure per-host or per-user:

#### Option 1: Host-Based Configuration

```yaml
---
- name: Configure developers (bash users)
  hosts: dev_servers
  become: true
  vars:
    asdf_shell_profile: "bashrc"
    asdf_users:
      - developer
  roles:
    - code3tech.devtools.asdf

- name: Configure admins (zsh users)
  hosts: admin_servers
  become: true
  vars:
    asdf_shell_profile: "zshrc"
    asdf_users:
      - admin
  roles:
    - code3tech.devtools.asdf
```

#### Option 2: Multiple Play Configuration

```yaml
---
- name: Configure all users with primary shell
  hosts: all
  become: true
  vars:
    asdf_shell_profile: "bashrc"  # Primary shell
    asdf_users:
      - developer
      - devops
  roles:
    - code3tech.devtools.asdf

# Manually configure alternative shells
- name: Configure zsh for specific users
  hosts: all
  become: true
  tasks:
    - name: Configure asdf for zsh users
      ansible.builtin.blockinfile:
        path: "/home/{{ item }}/.zshrc"
        block: |
          export ASDF_DIR="/opt/asdf"
          export ASDF_DATA_DIR="/opt/asdf"
          export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
        marker: "# {mark} ANSIBLE MANAGED BLOCK - asdf configuration"
      loop:
        - admin
        - sre
```

#### Option 3: Configure All Shells

Create a comprehensive configuration for all shells:

```yaml
---
- name: Configure asdf for all shells
  hosts: all
  become: true
  
  vars:
    asdf_users:
      - developer
      - admin
  
  tasks:
    - name: Configure bashrc
      ansible.builtin.blockinfile:
        path: "/home/{{ item }}/.bashrc"
        create: true
        block: |
          export ASDF_DIR="/opt/asdf"
          export ASDF_DATA_DIR="/opt/asdf"
          export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
        marker: "# {mark} ANSIBLE MANAGED BLOCK - asdf configuration"
      loop: "{{ asdf_users }}"
    
    - name: Configure zshrc
      ansible.builtin.blockinfile:
        path: "/home/{{ item }}/.zshrc"
        create: true
        block: |
          export ASDF_DIR="/opt/asdf"
          export ASDF_DATA_DIR="/opt/asdf"
          export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
        marker: "# {mark} ANSIBLE MANAGED BLOCK - asdf configuration"
      loop: "{{ asdf_users }}"
```

---

## Service Account Configuration

### CI/CD Users (Jenkins, GitHub Actions)

Configure service accounts for CI/CD:

```yaml
vars:
  asdf_users:
    - jenkins        # Jenkins service account
    - runner         # GitHub Actions runner
    - gitlab-runner  # GitLab runner
  
  asdf_shell_profile: "bashrc"  # Service accounts typically use bash
```

### Non-Interactive Shell Configuration

For service accounts that don't use interactive shells, ensure profile is sourced:

```yaml
post_tasks:
  - name: Ensure asdf is in non-interactive path for service accounts
    ansible.builtin.lineinfile:
      path: "/home/{{ item }}/.bash_profile"
      line: "source ~/.bashrc"
      create: true
    loop:
      - jenkins
      - runner
```

### Verification for Service Accounts

```bash
# Test as jenkins user
sudo -u jenkins bash -c 'source ~/.bashrc && node --version'
sudo -u jenkins bash -c 'source ~/.bashrc && asdf current'
```

---

## Troubleshooting Multi-User Issues

### User Not in asdf Group

```bash
# Check user groups
groups username
# If asdf not listed, add manually:
sudo usermod -aG asdf username

# User must log out/in for group changes
```

### Permission Denied Errors

```bash
# Check /opt/asdf permissions
ls -la /opt/asdf
# Should be: drwxrwxr-x root asdf

# Fix if needed
sudo chgrp -R asdf /opt/asdf
sudo chmod -R g+rwX /opt/asdf
```

### Shell Not Configured

```bash
# Verify shell configuration
grep -r "ASDF_DIR" ~/.bashrc ~/.zshrc 2>/dev/null

# If missing, add manually or re-run playbook
```

### New User After Role Execution

When adding new users after initial role execution:

```yaml
- name: Add new user to asdf
  hosts: target
  become: true
  tasks:
    - name: Add user to asdf group
      ansible.builtin.user:
        name: newuser
        groups: asdf
        append: true
    
    - name: Configure shell
      ansible.builtin.blockinfile:
        path: "/home/newuser/.bashrc"
        block: |
          export ASDF_DIR="/opt/asdf"
          export ASDF_DATA_DIR="/opt/asdf"
          export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
        marker: "# {mark} ANSIBLE MANAGED BLOCK - asdf configuration"
```

---

## Next Steps

- **[Production Deployment](06-production-deployment.md)** - Complete production playbooks
- **[Performance & Security](07-performance-security.md)** - Optimization and best practices
- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions

---

[← Back to asdf Documentation](README.md) | [Previous: Plugin Management](04-plugin-management.md) | [Next: Production Deployment →](06-production-deployment.md)
