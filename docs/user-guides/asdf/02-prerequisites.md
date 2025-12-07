# Part 2: Prerequisites & Setup

Before installing asdf, you need to prepare your environment. This guide walks you through all requirements.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installing the Ansible Collection](#installing-the-ansible-collection)
- [Preparing Target Hosts](#preparing-target-hosts)
- [User Preparation](#user-preparation)
- [Verification](#verification)
- [Next Steps](#next-steps)

## System Requirements

### Target Hosts (Where asdf Runs)

| Requirement | Specification |
|-------------|---------------|
| **OS** | Ubuntu 22.04+, Debian 11+, RHEL 9+ |
| **CPU** | 1+ core (2+ for compilation) |
| **RAM** | 512MB minimum, 2GB+ for heavy plugins |
| **Disk** | 500MB + space per installed version |
| **Network** | Internet access for downloads |

### Disk Space Estimates

| Installation | Disk Usage |
|--------------|------------|
| asdf binary only | ~50 MB |
| + lightweight plugins (direnv, jq) | ~100 MB |
| + nodejs (1 version) | ~200 MB |
| + python (1 version) | ~500 MB |
| + full stack (nodejs, python, ruby) | ~1.5 GB |

### Control Node (Where Ansible Runs)

| Requirement | Version |
|-------------|---------|
| **Ansible** | >= 2.15 |
| **Python** | >= 3.9 |

### Automatically Installed Dependencies

The role installs these packages automatically:

```
┌─────────────────────────────────────────────────────────────────┐
│                  Auto-Installed Dependencies                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  All Systems:                                                   │
│  ├── git              # For plugin management                  │
│  ├── curl             # For downloads                          │
│  └── unzip            # For extracting packages                │
│                                                                 │
│  Debian/Ubuntu (for compilation):                               │
│  ├── build-essential  # gcc, make, etc.                        │
│  ├── libssl-dev       # SSL libraries                          │
│  └── libffi-dev       # FFI libraries                          │
│                                                                 │
│  RHEL/Rocky/Alma (for compilation):                             │
│  ├── gcc              # C compiler                              │
│  ├── make             # Build tool                              │
│  └── openssl-devel    # SSL development files                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> 💡 **Tip**: Set `asdf_install_dependencies: false` if you manage dependencies separately.

## Installing the Ansible Collection

### Method 1: From Ansible Galaxy (Recommended)

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Verify installation
ansible-galaxy collection list | grep code3tech
```

### Method 2: From requirements.yml

Create `requirements.yml`:

```yaml
---
collections:
  - name: code3tech.devtools
    version: ">=1.1.0"
```

Install:

```bash
ansible-galaxy collection install -r requirements.yml
```

### Verify Installation

```bash
# List installed collections
ansible-galaxy collection list

# Expected output includes:
# Collection          Version
# ------------------- -------
# code3tech.devtools  1.2.0
```

## Preparing Target Hosts

### Step 1: Create Inventory File

Create `inventory.ini`:

```ini
# inventory.ini
[dev_servers]
dev01.example.com
dev02.example.com

[ci_servers]
jenkins01.example.com

[all:vars]
ansible_user=deploy
ansible_become=true
ansible_python_interpreter=/usr/bin/python3
```

### Step 2: Verify SSH Connectivity

```bash
# Test SSH connection
ansible all -i inventory.ini -m ping

# Expected output:
# dev01.example.com | SUCCESS => {"ping": "pong"}
# dev02.example.com | SUCCESS => {"ping": "pong"}
```

### Step 3: Verify Sudo Access

```bash
# Test sudo
ansible all -i inventory.ini -m command -a "whoami" --become

# Expected output:
# dev01.example.com | CHANGED | rc=0 >>
# root
```

### Step 4: Check Internet Connectivity

```bash
# Test GitHub access (where asdf downloads from)
ansible all -i inventory.ini -m uri -a "url=https://github.com return_content=no"

# Expected: SUCCESS
```

## User Preparation

### Understanding User Requirements

The asdf role adds specified users to the `asdf` group:

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Requirements                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Users MUST exist BEFORE running the role!                      │
│                                                                 │
│  asdf_users:                                                    │
│    - developer    ←── Must exist                               │
│    - jenkins      ←── Must exist                               │
│    - deploy       ←── Must exist                               │
│                                                                 │
│  The role will:                                                 │
│  ✅ Add users to 'asdf' group                                  │
│  ✅ Configure shell profiles (~/.bashrc, etc.)                 │
│  ❌ NOT create users (you must do this first)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Users (If Needed)

```yaml
# create-users.yml
---
- name: Create Users for asdf
  hosts: all
  become: true

  tasks:
    - name: Create developer user
      ansible.builtin.user:
        name: developer
        shell: /bin/bash
        create_home: true

    - name: Create CI user
      ansible.builtin.user:
        name: jenkins
        shell: /bin/bash
        create_home: true
```

Run:

```bash
ansible-playbook create-users.yml -i inventory.ini
```

### Step 2: Verify Users Exist

```bash
# Check users on target hosts
ansible all -i inventory.ini -m command -a "id developer"
ansible all -i inventory.ini -m command -a "id jenkins"

# Expected:
# uid=1001(developer) gid=1001(developer) groups=1001(developer)
```

### Step 3: Determine Shell Type

Check which shell your users use:

```bash
ansible all -i inventory.ini -m command -a "getent passwd developer | cut -d: -f7"

# /bin/bash → use asdf_shell_profile: "bashrc"
# /bin/zsh  → use asdf_shell_profile: "zshrc"
# /usr/bin/fish → use asdf_shell_profile: "config/fish/config.fish"
```

## Verification

### Checklist

Before proceeding, verify:

- [ ] Target hosts meet system requirements (OS, RAM, disk)
- [ ] Ansible collection installed (`ansible-galaxy collection list`)
- [ ] SSH connectivity working (`ansible all -m ping`)
- [ ] Sudo access confirmed (`ansible all -m command -a "whoami" --become`)
- [ ] Internet connectivity verified (GitHub accessible)
- [ ] Users exist on target hosts (or created)
- [ ] Shell type identified for users

### Quick Verification Script

Create `verify-prereqs.yml`:

```yaml
---
# verify-prereqs.yml
- name: Verify Prerequisites
  hosts: all
  become: true
  gather_facts: true

  tasks:
    - name: Check OS family
      ansible.builtin.debug:
        msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"

    - name: Check available disk space
      ansible.builtin.command: df -h /opt
      register: disk_space
      changed_when: false

    - name: Display disk space
      ansible.builtin.debug:
        var: disk_space.stdout_lines

    - name: Check internet connectivity
      ansible.builtin.uri:
        url: "https://github.com"
        method: HEAD
        timeout: 10
      register: github_check

    - name: Verify GitHub accessible
      ansible.builtin.debug:
        msg: "✅ GitHub accessible"
      when: github_check.status == 200

    - name: Check if users exist
      ansible.builtin.getent:
        database: passwd
        key: "{{ item }}"
      loop:
        - "{{ ansible_user }}"
      register: user_check
      ignore_errors: true

    - name: Display verification summary
      ansible.builtin.debug:
        msg: |
          ╔════════════════════════════════════════════╗
          ║         Prerequisites Verified             ║
          ╠════════════════════════════════════════════╣
          ║ OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          ║ Internet: ✅
          ║ Users: ✅
          ╚════════════════════════════════════════════╝
```

Run:

```bash
ansible-playbook verify-prereqs.yml -i inventory.ini
```

## Variable Reference (Quick Look)

You'll configure these in the next steps:

```yaml
# Basic configuration
asdf_version: "latest"              # asdf version
asdf_install_dir: "/opt/asdf"       # Installation directory
asdf_install_dependencies: true     # Install build tools

# User configuration  
asdf_users:                         # Users to configure
  - developer
asdf_shell_profile: "bashrc"        # Shell profile (bashrc, zshrc, fish)

# Plugin configuration
asdf_plugins:                       # Plugins to install
  - name: "nodejs"
    versions: ["22.11.0"]
    global: "22.11.0"
```

## Next Steps

Your environment is ready! Proceed to:

➡️ **[Part 3: Basic Installation](03-basic-installation.md)** - Install asdf step by step.

---

## Quick Reference

### Documentation Map

```
1. Introduction → [2. Prerequisites] → 3. Basic Install → ...
```

### Essential Commands

```bash
# Install collection
ansible-galaxy collection install code3tech.devtools

# Test connectivity
ansible all -i inventory.ini -m ping

# Verify users
ansible all -m command -a "id username"
```

---

[← Previous: Introduction](01-introduction.md) | [Back to Guide Index](README.md) | [Next: Basic Installation →](03-basic-installation.md)
