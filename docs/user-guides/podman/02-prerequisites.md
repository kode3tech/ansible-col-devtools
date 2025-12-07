# Prerequisites

System requirements and preparation for Podman installation.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Supported Distributions](#supported-distributions)
- [Collection Installation](#collection-installation)
- [Ansible Vault Setup](#ansible-vault-setup)
- [User Requirements](#user-requirements)
- [Pre-Deployment Checklist](#pre-deployment-checklist)

---

## System Requirements

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 1 core | 2+ cores |
| **RAM** | 1 GB | 4+ GB |
| **Disk** | 10 GB | 50+ GB (SSD preferred) |
| **Kernel** | 4.18+ | 5.4+ |
| **Ansible** | 2.15+ | Latest |
| **Python** | 3.9+ | 3.11+ |

### Kernel Requirements

Podman requires modern kernel features:

```bash
# Check kernel version
uname -r

# Minimum: 4.18+ (for user namespaces)
# Recommended: 5.4+ (for overlay fs improvements)
```

### Kernel Modules

Required modules (loaded automatically):

| Module | Purpose |
|--------|---------|
| `overlay` | Storage driver |
| `br_netfilter` | Bridge networking |
| `ip_tables` | Network filtering |

---

## Supported Distributions

### Ubuntu

| Version | Codename | Support |
|---------|----------|---------|
| 22.04 | Jammy | ✅ Full |
| 24.04 | Noble | ✅ Full |
| 25.04 | Plucky | ✅ Full |

### Debian

| Version | Codename | Support |
|---------|----------|---------|
| 11 | Bullseye | ✅ Full |
| 12 | Bookworm | ✅ Full |
| 13 | Trixie | ✅ Full |

### RHEL/Rocky/AlmaLinux

| Version | Support |
|---------|---------|
| 9.x | ✅ Full |
| 10.x | ✅ Full |

---

## Collection Installation

### Install from Ansible Galaxy

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Install required dependencies
ansible-galaxy collection install containers.podman
```

### Install from Source

```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment
source activate.sh

# Build and install
make install-collection
```

### Requirements File

Create `requirements.yml`:

```yaml
---
collections:
  - name: code3tech.devtools
    version: ">=1.0.0"
  - name: containers.podman
    version: ">=1.10.0"
  - name: ansible.posix
    version: ">=1.5.0"
  - name: community.general
    version: ">=6.0.0"
```

Install:

```bash
ansible-galaxy collection install -r requirements.yml
```

### Verify Installation

```bash
# Check collection is installed
ansible-galaxy collection list | grep devtools

# Check Podman module is available
ansible-doc containers.podman.podman_login
```

---

## Ansible Vault Setup

### Why Vault?

⚠️ **Never commit plain-text passwords!**

Registry credentials must be encrypted with Ansible Vault.

### Create Vault File

```bash
# Create encrypted secrets file
ansible-vault create vars/secrets.yml
```

### Example Vault Content

```yaml
# Registry credentials
vault_dockerhub_token: "dckr_pat_xxxxxxxxxxxxxxxxx"
vault_github_token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
vault_quay_token: "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
vault_private_registry_password: "your_secure_password"
```

### Encrypt Existing File

```bash
ansible-vault encrypt vars/secrets.yml
```

### Encrypt Single String

```bash
ansible-vault encrypt_string 'my_secret_password' --name 'vault_password'
```

Output (add to vars):
```yaml
vault_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted data...
```

### Running with Vault

```bash
# Interactive password prompt
ansible-playbook playbook.yml --ask-vault-pass

# Password file
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass

# Multiple vault IDs
ansible-playbook playbook.yml --vault-id prod@~/.vault_pass_prod
```

---

## User Requirements

### Rootless Users Must Exist

Users configured for rootless Podman **must exist** before the role runs.

#### Create in Pre-Tasks

```yaml
pre_tasks:
  - name: Create Podman users
    ansible.builtin.user:
      name: "{{ item }}"
      shell: /bin/bash
      create_home: true
    loop:
      - developer
      - jenkins
      - deployer
```

#### Or Use Existing Users

```yaml
vars:
  podman_rootless_users:
    - "{{ ansible_user }}"  # Current SSH user
```

### User Namespace Requirements

For rootless mode, users need subuid/subgid entries. The role handles this automatically, but manual verification:

```bash
# Check subuid
cat /etc/subuid

# Expected output:
# developer:100000:65536
# jenkins:165536:65536
```

---

## Pre-Deployment Checklist

### System Checks

- [ ] **Kernel version**: 4.18+ (check: `uname -r`)
- [ ] **Disk space**: 10+ GB free on `/var` or custom path
- [ ] **Memory**: 1+ GB available
- [ ] **Network**: Access to package repositories
- [ ] **Time sync**: System clock accurate (for GPG validation)

### Ansible Environment

- [ ] **Ansible version**: 2.15+ (check: `ansible --version`)
- [ ] **Python version**: 3.9+ (check: `python3 --version`)
- [ ] **Collection installed**: `code3tech.devtools`
- [ ] **Dependencies**: `containers.podman`, `ansible.posix`

### Security Preparation

- [ ] **Vault created**: Secrets encrypted
- [ ] **Registry tokens**: Generated for all registries
- [ ] **Users exist**: All rootless users created

### Inventory

```ini
# inventory.ini
[podman_hosts]
server1.example.com
server2.example.com

[podman_hosts:vars]
ansible_user=admin
ansible_become=true
```

---

## Network Requirements

### Package Repositories

Ensure access to:

| Distribution | Repository |
|--------------|------------|
| Ubuntu/Debian | `archive.ubuntu.com`, `deb.debian.org` |
| RHEL/Rocky | `cdn.redhat.com`, `mirrors.rockylinux.org` |

### Container Registries

Default registries:

| Registry | URL | Purpose |
|----------|-----|---------|
| Docker Hub | `docker.io` | Default images |
| Quay.io | `quay.io` | Red Hat images |

### Firewall Ports

For container networking (if applicable):

| Port | Protocol | Purpose |
|------|----------|---------|
| 80 | TCP | HTTP (root mode only) |
| 443 | TCP | HTTPS (root mode only) |
| 1024+ | TCP/UDP | User ports (rootless) |

---

## Time Synchronization

### Why It Matters

GPG keys have validity dates. If system clock is wrong:
- Package signature validation fails
- TLS certificates appear invalid
- Scheduled tasks run at wrong times

### Ubuntu/Debian

```yaml
pre_tasks:
  - name: Ensure systemd-timesyncd is installed
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
    when: ansible_os_family == 'Debian'
  
  - name: Enable time synchronization
    ansible.builtin.service:
      name: systemd-timesyncd
      state: started
      enabled: true
    when: ansible_os_family == 'Debian'
```

### RHEL/Rocky/Alma

```yaml
pre_tasks:
  - name: Ensure chrony is installed
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family == 'RedHat'
  
  - name: Enable chrony
    ansible.builtin.service:
      name: chronyd
      state: started
      enabled: true
    when: ansible_os_family == 'RedHat'
  
  - name: Force time sync
    ansible.builtin.command: chronyc makestep
    changed_when: false
    when: ansible_os_family == 'RedHat'
```

---

## Verification Script

Run before deployment:

```bash
#!/bin/bash
echo "=== Podman Pre-Deployment Check ==="

echo -e "\n1. Kernel Version:"
uname -r

echo -e "\n2. Disk Space:"
df -h / | tail -1

echo -e "\n3. Memory:"
free -h | grep Mem

echo -e "\n4. Ansible Version:"
ansible --version | head -1

echo -e "\n5. Python Version:"
python3 --version

echo -e "\n6. Collection Check:"
ansible-galaxy collection list 2>/dev/null | grep -E "devtools|podman" || echo "Collections not found"

echo -e "\n7. Time Sync:"
timedatectl status | grep -E "synchronized|System clock"

echo -e "\n=== Check Complete ==="
```

---

## Next Steps

- **[Basic Installation](03-basic-installation.md)** - Install Podman
- **[Rootless Configuration](05-rootless-config.md)** - Configure rootless users

---

[← Back to Podman Documentation](README.md) | [Previous: Introduction](01-introduction.md) | [Next: Basic Installation →](03-basic-installation.md)
