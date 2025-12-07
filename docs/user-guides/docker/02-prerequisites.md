# Prerequisites

System requirements and setup needed before deploying Docker with the code3tech.devtools collection.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Supported Distributions](#supported-distributions)
- [Ansible Collection Installation](#ansible-collection-installation)
- [Ansible Vault Setup](#ansible-vault-setup)
- [Pre-Deployment Checklist](#pre-deployment-checklist)

---

## System Requirements

### Control Node (Ansible Host)

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Ansible** | 2.15+ | 2.17+ |
| **Python** | 3.9+ | 3.11+ |
| **Collections** | community.docker 3.4.0+ | Latest |

### Target Nodes (Docker Hosts)

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **RAM** | 2 GB | 4 GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Disk** | 20 GB | 50 GB+ (SSD recommended) |
| **Network** | Internet access | Fast connection for image pulls |

### Kernel Requirements

Docker requires specific kernel features:

| Feature | Requirement |
|---------|-------------|
| **Kernel Version** | 4.0+ (for overlay2) |
| **cgroups v2** | Supported (default on modern distros) |
| **User Namespaces** | Enabled (for rootless mode) |

Check kernel version:
```bash
uname -r
# Expected: 5.x or higher
```

---

## Supported Distributions

### Ubuntu

| Version | Codename | Status |
|---------|----------|--------|
| 22.04 LTS | Jammy | ✅ Fully Supported |
| 24.04 LTS | Noble | ✅ Fully Supported |
| 25.04 | Plucky | ✅ Fully Supported |

### Debian

| Version | Codename | Status |
|---------|----------|--------|
| 11 | Bullseye | ✅ Fully Supported |
| 12 | Bookworm | ✅ Fully Supported |
| 13 | Trixie | ✅ Fully Supported |

### RHEL-Based

| Distribution | Version | Status |
|--------------|---------|--------|
| RHEL | 9, 10 | ✅ Fully Supported |
| Rocky Linux | 9, 10 | ✅ Fully Supported |
| AlmaLinux | 9, 10 | ✅ Fully Supported |
| CentOS Stream | 9, 10 | ✅ Fully Supported |

### Not Supported

❌ Ubuntu 20.04 and older  
❌ Debian 10 and older  
❌ RHEL 8 and older  
❌ CentOS 7

---

## Ansible Collection Installation

### Install from Ansible Galaxy

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Install required dependencies
ansible-galaxy collection install community.docker
```

### Install from Requirements File

Create `requirements.yml`:

```yaml
---
collections:
  - name: code3tech.devtools
    version: ">=1.0.0"
  - name: community.docker
    version: ">=3.4.0"
```

Install:
```bash
ansible-galaxy collection install -r requirements.yml
```

### Verify Installation

```bash
# Check installed collections
ansible-galaxy collection list | grep -E "code3tech|community.docker"

# Expected output:
# code3tech.devtools    1.x.x
# community.docker      3.x.x
```

### Local Development Installation

For development or testing:

```bash
# Clone repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment
source activate.sh

# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Build and install locally
make install-collection
```

---

## Ansible Vault Setup

### Why Use Vault?

⚠️ **NEVER commit plain-text credentials to version control!**

Ansible Vault encrypts sensitive data:
- Registry passwords and tokens
- API keys
- Private configuration

### Create Encrypted Variables

```bash
# Create new vault file
ansible-vault create vars/docker_secrets.yml

# Add your secrets (in the editor):
vault_dockerhub_token: "dckr_pat_xxxxxxxxxxxxx"
vault_github_token: "ghp_xxxxxxxxxxxxxxxxxxxxx"
vault_registry_password: "your_secure_password"
```

### Encrypt Individual Strings

```bash
# Encrypt a single value
ansible-vault encrypt_string 'my_secret_password' --name 'vault_password'

# Output (add to your vars file):
vault_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          61626364656667686970...
```

### Using Vault Variables

Reference vault variables in your playbooks:

```yaml
vars_files:
  - vars/docker_secrets.yml

vars:
  docker_registries_auth:
    - registry: "ghcr.io"
      username: "myuser"
      password: "{{ vault_github_token }}"  # ✅ Encrypted!
```

### Running with Vault

```bash
# Interactive password prompt
ansible-playbook playbook.yml --ask-vault-pass

# Password file (automation)
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass

# Multiple vault IDs
ansible-playbook playbook.yml --vault-id prod@~/.vault_pass_prod
```

### Vault Best Practices

| Practice | Description |
|----------|-------------|
| **Separate files** | One vault file per environment |
| **Gitignore passwords** | Never commit `.vault_pass` files |
| **Rotate regularly** | Change vault passwords periodically |
| **Use vault IDs** | Separate vaults for dev/staging/prod |

---

## Pre-Deployment Checklist

### Before Running the Playbook

- [ ] **Ansible installed** (version 2.15+)
- [ ] **Collections installed** (code3tech.devtools, community.docker)
- [ ] **SSH access** to target hosts
- [ ] **Sudo privileges** on target hosts
- [ ] **Internet connectivity** on target hosts (for package installation)

### Target Host Requirements

- [ ] **Supported OS** (Ubuntu 22+, Debian 11+, RHEL 9+)
- [ ] **Kernel 4.0+** (for overlay2 storage driver)
- [ ] **Sufficient disk space** (20 GB minimum)
- [ ] **No conflicting Docker installations**

### If Using Private Registries

- [ ] **Vault configured** with encrypted credentials
- [ ] **Registry access tokens** generated
- [ ] **Network access** to private registries

### Verify Connectivity

```bash
# Test SSH connection
ansible all -i inventory.ini -m ping

# Check sudo access
ansible all -i inventory.ini -m command -a "whoami" --become

# Verify internet access
ansible all -i inventory.ini -m uri -a "url=https://download.docker.com"
```

---

## Next Steps

- **[Basic Installation](03-basic-installation.md)** - Your first Docker deployment
- **[Registry Authentication](04-registry-auth.md)** - Private registry setup

---

[← Back to Docker Documentation](README.md) | [Previous: Introduction](01-introduction.md) | [Next: Basic Installation →](03-basic-installation.md)
