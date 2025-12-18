# Installation Guide

Get the **code3tech.devtools** collection installed and ready to use.

## 📋 Table of Contents

- [Installation Methods](#installation-methods)
- [System Requirements](#system-requirements)
- [Installing Dependencies](#installing-dependencies)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Installation Methods

### 🌟 Method 1: From Ansible Galaxy (Recommended)

Install the latest stable version directly from Ansible Galaxy:

```bash
ansible-galaxy collection install code3tech.devtools
```

**Install specific version:**

```bash
ansible-galaxy collection install code3tech.devtools:1.4.0
```

**Install with requirements file:**

Create `requirements.yml`:

```yaml
---
collections:
  - name: code3tech.devtools
    version: ">=1.4.0"
```

Install:

```bash
ansible-galaxy collection install -r requirements.yml
```

---

### 🔧 Method 2: From Source (Development)

For the latest features or contributing:

```bash
# Clone repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate development environment (creates venv if needed)
source activate.sh

# Install collection locally
make install-collection
```

---

## System Requirements

### Control Node (Where Ansible Runs)

| Requirement | Minimum Version |
|-------------|----------------|
| **Ansible** | >= 2.15 |
| **Python** | >= 3.9 |
| **Operating System** | Linux, macOS, WSL2 |

### Target Nodes (Managed Hosts)

| Distribution | Supported Versions |
|--------------|-------------------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/Rocky/Alma** | 9, 10 |

**Required on target hosts:**
- Python >= 3.9
- SSH access
- sudo/root privileges (for most roles)

---

## Installing Dependencies

The collection requires additional Ansible collections for full functionality:

### Required Collections

```bash
# Install all required dependencies
ansible-galaxy collection install -r requirements.yml
```

**Or install individually:**

```bash
# For Docker role (registry authentication)
ansible-galaxy collection install community.docker

# For Podman role (registry authentication)
ansible-galaxy collection install containers.podman
```

### Verify Dependencies

```bash
ansible-galaxy collection list
```

Expected output:
```
code3tech.devtools     1.4.0
community.docker       5.0.2+
containers.podman      1.18.0+
```

---

## Verification

### Check Collection Installation

```bash
# List installed collections
ansible-galaxy collection list | grep code3tech

# Should output:
# code3tech.devtools     1.4.0
```

### Verify Ansible Version

```bash
ansible --version
```

Expected output:
```
ansible [core 2.15.0+]
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/home/user/.ansible/plugins/modules']
  ansible python module location = /usr/lib/python3.9/site-packages/ansible
  ansible collection location = /home/user/.ansible/collections
  python version = 3.9.0+
```

### Test Collection Access

```bash
# List roles in collection
ansible-galaxy collection list code3tech.devtools -vvv
```

---

## Troubleshooting

### Issue: "Collection not found"

**Symptom:**
```
ERROR! couldn't resolve module/action 'code3tech.devtools.docker'
```

**Solutions:**

1. **Verify installation path:**
   ```bash
   ansible-galaxy collection list
   ```

2. **Check ansible.cfg configuration:**
   ```ini
   [defaults]
   collections_path = ~/.ansible/collections:/usr/share/ansible/collections
   ```

3. **Reinstall collection:**
   ```bash
   ansible-galaxy collection install code3tech.devtools --force
   ```

---

### Issue: "Ansible version too old"

**Symptom:**
```
ERROR! Ansible requires a minimum version of 2.15
```

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible
```

**RHEL/Rocky/Alma:**
```bash
sudo dnf install ansible-core
```

**Using pip (all platforms):**
```bash
pip install --upgrade ansible
```

---

### Issue: "Dependencies missing"

**Symptom:**
```
ERROR! The collection community.docker is required but not installed
```

**Solution:**
```bash
# Install from requirements file
ansible-galaxy collection install -r requirements.yml

# Or install missing collection directly
ansible-galaxy collection install community.docker
```

---

### Issue: "Permission denied when installing"

**Symptom:**
```
ERROR! Cannot write to /usr/share/ansible/collections
```

**Solutions:**

**Option 1: Install to user directory (recommended)**
```bash
ansible-galaxy collection install code3tech.devtools --collections-path ~/.ansible/collections
```

**Option 2: Use sudo (not recommended)**
```bash
sudo ansible-galaxy collection install code3tech.devtools
```

---

## Installation Verification Checklist

Before proceeding, ensure all checks pass:

- [ ] Ansible version >= 2.15
- [ ] Python version >= 3.9
- [ ] Collection `code3tech.devtools` installed
- [ ] Collection `community.docker` installed
- [ ] Collection `containers.podman` installed
- [ ] Can list collection: `ansible-galaxy collection list code3tech.devtools`

---

## Next Steps

✅ **Collection installed!** Now you're ready to:

1. **[Create your first playbook](02-first-playbook.md)** - Deploy Docker in 5 minutes
2. **[Learn inventory basics](03-inventory-basics.md)** - Define your target hosts
3. **[Explore available roles](04-using-roles.md)** - See what the collection offers

---

## Additional Resources

- **Official Ansible Galaxy**: https://galaxy.ansible.com/ui/repo/published/code3tech/devtools/
- **GitHub Repository**: https://github.com/kode3tech/ansible-col-devtools
- **Changelog**: [CHANGELOG.md](../../CHANGELOG.md)
- **Requirements file**: [requirements.yml](../../requirements.yml)

---

[← Back to Getting Started](README.md) | [Next: Your First Playbook →](02-first-playbook.md)
