# Basic Installation

Step-by-step guide to your first asdf deployment using the code3tech.devtools Ansible collection.

---

## 📋 Table of Contents

- [Minimal Installation](#minimal-installation)
- [Installation with Plugins](#installation-with-plugins)
- [Directory Structure](#directory-structure)
- [Verification Steps](#verification-steps)
- [What Gets Installed](#what-gets-installed)

---

## Minimal Installation

The simplest playbook to install asdf on your servers:

### Create the Playbook

Create `install-asdf-minimal.yml`:

```yaml
---
- name: asdf Minimal Installation
  hosts: all
  become: true
  
  roles:
    - code3tech.devtools.asdf
```

### Run the Playbook

```bash
# Run with inventory
ansible-playbook install-asdf-minimal.yml -i inventory.ini

# With verbose output
ansible-playbook install-asdf-minimal.yml -i inventory.ini -v
```

### What This Does

The minimal installation performs these steps:

1. **Downloads asdf binary** from GitHub releases (latest version)
2. **Installs to `/opt/asdf`** (centralized location)
3. **Creates `asdf` group** for multi-user access
4. **Configures `/etc/profile.d/asdf.sh`** for system-wide PATH
5. **Installs system dependencies** (git, curl, build tools)

### Expected Output

```
TASK [code3tech.devtools.asdf : Install asdf] *************************************
changed: [server1]

TASK [code3tech.devtools.asdf : Create asdf group] ********************************
changed: [server1]

TASK [code3tech.devtools.asdf : Configure system-wide PATH] ***********************
changed: [server1]

PLAY RECAP ************************************************************************
server1 : ok=8  changed=5  unreachable=0  failed=0  skipped=2  rescued=0  ignored=0
```

---

## Installation with Plugins

Add plugins and users to your installation:

### Playbook with Plugins

Create `install-asdf-with-plugins.yml`:

```yaml
---
- name: asdf with Development Tools
  hosts: all
  become: true
  
  vars:
    # Users to add to asdf group
    asdf_users:
      - developer
      - devops
    
    # Plugins to install centrally (shared by all users)
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

### What This Does

Beyond the minimal installation, this also:

1. **Adds specified users** to `asdf` group
2. **Installs plugins** centrally (shared by all users)
3. **Installs specified versions** of each plugin
4. **Sets global versions** for each plugin
5. **Configures user shell profiles** (adds asdf to PATH)

### Run and Verify

```bash
# Run the playbook
ansible-playbook install-asdf-with-plugins.yml -i inventory.ini

# SSH to server and verify
ssh server1

# Check asdf version
asdf --version

# List installed plugins
asdf plugin list

# Check nodejs version
node --version
```

---

## Directory Structure

After installation, asdf creates this directory structure:

```
/opt/asdf/                     # Main installation directory
├── bin/
│   └── asdf                   # Main binary
├── plugins/                   # Installed plugins
│   ├── nodejs/
│   │   └── bin/
│   │       └── install        # Plugin install script
│   ├── python/
│   └── direnv/
├── installs/                  # Installed versions
│   ├── nodejs/
│   │   ├── 22.11.0/           # Node.js v22.11.0
│   │   │   └── bin/
│   │   │       ├── node
│   │   │       └── npm
│   │   └── 20.18.0/           # Node.js v20.18.0
│   └── python/
│       └── 3.13.0/
│           └── bin/
│               ├── python
│               └── pip
└── shims/                     # Shim executables (version routing)
    ├── node                   # Routes to active nodejs version
    ├── npm
    ├── python
    ├── pip
    └── direnv
```

### Understanding Shims

Shims are lightweight scripts that route commands to the correct version:

```
$ which node
/opt/asdf/shims/node          # Points to shim, not actual binary

$ node --version              # Shim routes to global version
v22.11.0

$ cd project-with-tool-versions
$ node --version              # Shim routes to project version
v20.18.0
```

### Permissions Structure

```
/opt/asdf/
├── Owner: root
├── Group: asdf
└── Mode: 0775 (rwxrwxr-x)

Users in 'asdf' group:
├── developer  ─┐
├── devops     ─┼── Can use all plugins and versions
└── jenkins    ─┘
```

---

## Verification Steps

After installation, verify everything works:

### 1. Check asdf Installation

```bash
# Verify asdf binary
/opt/asdf/bin/asdf --version
# Expected: v0.18.0 (or latest version)

# Verify PATH configuration
which asdf
# Expected: /opt/asdf/bin/asdf
```

### 2. Verify Plugins

```bash
# List installed plugins
asdf plugin list
# Expected:
# direnv
# nodejs

# Check plugin versions
asdf list nodejs
# Expected:
#   22.11.0
#   20.18.0
```

### 3. Verify Global Versions

```bash
# Check global nodejs version
asdf current nodejs
# Expected: nodejs          22.11.0         /opt/asdf/.tool-versions

# Verify shim works
node --version
# Expected: v22.11.0
```

### 4. Verify User Access

```bash
# Test as different users
sudo -u developer asdf --version
sudo -u devops asdf plugin list
sudo -u jenkins node --version
```

### 5. Verify Group Membership

```bash
# Check asdf group members
getent group asdf
# Expected: asdf:x:1001:developer,devops,jenkins

# Verify user groups
groups developer
# Expected: developer asdf
```

---

## What Gets Installed

### System Dependencies

The role installs required system packages:

| Distribution | Packages Installed |
|--------------|-------------------|
| **Ubuntu/Debian** | git, curl, unzip, build-essential, libssl-dev, libffi-dev |
| **RHEL/Rocky** | git, curl, unzip, gcc, make, openssl-devel |

### Shell Profile Configuration

Each user in `asdf_users` gets shell configuration added:

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

Created in `/etc/profile.d/asdf.sh`:

```bash
export ASDF_DIR="/opt/asdf"
export ASDF_DATA_DIR="/opt/asdf"
export PATH="$ASDF_DIR/bin:$ASDF_DIR/shims:$PATH"
```

This ensures asdf is available for all login shells.

---

## Next Steps

Now that you have asdf installed, learn how to:

- **[Plugin Management](04-plugin-management.md)** - Install and manage plugins
- **[Multi-User Configuration](05-multi-user-config.md)** - Configure for multiple users
- **[Production Deployment](06-production-deployment.md)** - Deploy in production environments

---

[← Back to asdf Documentation](README.md) | [Next: Plugin Management →](04-plugin-management.md)
