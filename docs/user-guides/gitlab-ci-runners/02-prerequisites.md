# Part 2: Prerequisites & Setup

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [GitLab Account Requirements](#gitlab-account-requirements)
- [Creating a Personal Access Token (PAT)](#creating-a-personal-access-token-pat)
- [Ansible Environment Setup](#ansible-environment-setup)
- [Installing the Collection](#installing-the-collection)
- [Creating Your Inventory](#creating-your-inventory)
- [Setting Up Ansible Vault](#setting-up-ansible-vault)
- [Verification Checklist](#verification-checklist)

---

## System Requirements

### Target Server Requirements

These are the servers where runners will be installed:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Minimum Server Requirements                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   HARDWARE                                                               │
│   ────────                                                               │
│   • CPU: 2 cores minimum (4+ recommended for parallel jobs)             │
│   • RAM: 2GB minimum (4GB+ recommended)                                 │
│   • Disk: 20GB minimum (more for Docker builds/caching)                 │
│   • Network: Outbound internet access to gitlab.com or your GitLab      │
│                                                                          │
│   OPERATING SYSTEM                                                       │
│   ────────────────                                                       │
│   ┌────────────────────┬──────────────────────────────────────┐        │
│   │ Distribution       │ Supported Versions                    │        │
│   ├────────────────────┼──────────────────────────────────────┤        │
│   │ Ubuntu             │ 22.04, 24.04, 25.04                   │        │
│   │ Debian             │ 11 (Bullseye), 12 (Bookworm), 13      │        │
│   │ RHEL/Rocky/Alma    │ 9, 10                                 │        │
│   └────────────────────┴──────────────────────────────────────┘        │
│                                                                          │
│   CONNECTIVITY                                                           │
│   ────────────                                                           │
│   • SSH access from Ansible controller                                  │
│   • Outbound HTTPS (443) to:                                            │
│     - gitlab.com (or your self-hosted GitLab URL)                       │
│     - gitlab.com/api/v4 (API endpoint)                                  │
│     - Executor dependencies (docker.io for Docker executor)             │
│                                                                          │
│   DOCKER EXECUTOR (Optional but Recommended)                             │
│   ────────────────────────────────────────                               │
│   • Docker Engine installed (use code3tech.devtools.docker role)        │
│   • Runner user added to docker group                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Ansible Controller Requirements

This is the machine where you run Ansible:

| Requirement | Minimum Version |
|-------------|-----------------|
| **Python** | 3.9+ |
| **Ansible** | 2.15+ |
| **ansible-galaxy** | Included with Ansible |

---

## GitLab Account Requirements

### Understanding What You Need

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GitLab Requirements by Scope                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PROJECT RUNNER                                                         │
│   ──────────────                                                         │
│   ✅ Any GitLab account (gitlab.com or self-hosted)                      │
│   ✅ Maintainer role in the project                                      │
│   ✅ GitLab Free, Premium, or Ultimate                                   │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   GROUP RUNNER                                                           │
│   ────────────                                                           │
│   ✅ GitLab group (not personal namespace)                               │
│   ✅ Owner or Maintainer role in the group                               │
│   ✅ GitLab Free, Premium, or Ultimate                                   │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   INSTANCE RUNNER                                                        │
│   ───────────────                                                        │
│   ✅ Self-hosted GitLab instance (NOT gitlab.com)                        │
│   ✅ Administrator access to GitLab                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Creating a Personal Access Token (PAT)

### Step-by-Step Guide

A Personal Access Token (PAT) is like a password that Ansible uses to communicate with GitLab's API.

#### For Project or Group Runners

##### Step 1: Navigate to Access Tokens

1. Log into GitLab (gitlab.com or your self-hosted instance)
2. For **Project runner**: Go to your project → Settings → Access Tokens
3. For **Group runner**: Go to your group → Settings → Access Tokens

```
┌───────────────────────────────────────────────────────────┐
│  GitLab UI Navigation                                     │
│  ─────────────────────                                    │
│                                                           │
│  Project/Group → Settings → Access Tokens                 │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

##### Step 2: Create Token

Fill in the form:

| Field | Value | Notes |
|-------|-------|-------|
| **Token name** | `ansible-runner-automation` | Descriptive name |
| **Expiration date** | 90 days (or never) | Balance security vs convenience |
| **Scopes** | `api`, `read_api`, `create_runner` | **CRITICAL**: Must include these |

**Required scopes explained:**
- `api` - Full API access (needed for runner creation/deletion)
- `read_api` - Read-only API access (for querying runner info)
- `create_runner` - Specific permission to create runners

##### Step 3: Copy Token

```
┌───────────────────────────────────────────────────────────┐
│  ⚠️  IMPORTANT: Copy token NOW!                           │
│  ────────────────────────────                             │
│                                                           │
│  Token: glpat-xxxxxxxxxxxxxxxxxxxx                        │
│         └─ Copy this!                                     │
│                                                           │
│  ⚠️  You won't be able to see it again!                   │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Token format:**
- `glpat-` prefix = Personal Access Token
- Example: `glpat-xxxxxxxxxxxxxxxxxxxx` (20 characters after prefix)

#### For Instance Runners (Admin Only)

##### Step 1: Navigate to Admin Area

1. Log into GitLab as administrator
2. Click Admin Area (wrench icon)
3. Go to Settings → CI/CD → Runners

##### Step 2: Use Admin Token

1. Click your profile picture → Settings → Access Tokens
2. Create token with **admin** scope
3. Token format: `glpat-xxxxxxxxxxxxxxxxxxxx`

**Required scope:**
- `api` - Full API access (includes admin operations)

---

### Token Security Best Practices

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Token Security Checklist                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ✅ DO:                                                                 │
│   ────                                                                   │
│   • Store tokens in Ansible Vault (encrypted)                           │
│   • Use descriptive token names                                         │
│   • Set expiration dates (90 days recommended)                          │
│   • Use minimum required scopes                                         │
│   • Rotate tokens regularly                                             │
│   • Delete unused tokens                                                │
│                                                                          │
│   ❌ DON'T:                                                              │
│   ───────                                                                │
│   • Never commit tokens to git                                          │
│   • Never share tokens in chat/email                                    │
│   • Don't use overly broad scopes                                       │
│   • Don't reuse tokens across environments                              │
│   • Never log tokens in plaintext                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Ansible Environment Setup

### Option 1: Using Project Virtual Environment (Recommended)

This collection includes a convenient activation script:

```bash
# Clone the collection repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment (creates if needed)
source activate.sh

# Verify versions
ansible --version
python --version
```

**What `activate.sh` does:**
- Creates Python virtual environment if needed
- Installs Ansible and dependencies
- Activates the environment
- Sets up collection path

### Option 2: System-Wide Installation

```bash
# Install Ansible
pip3 install ansible>=2.15

# Or using your package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install ansible

# RHEL/Rocky:
sudo dnf install ansible
```

---

## Installing the Collection

### From Ansible Galaxy

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Verify installation
ansible-galaxy collection list | grep code3tech
```

Expected output:
```
code3tech.devtools    1.4.0
```

### From Source (Development)

```bash
# Clone repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment
source activate.sh

# Install in development mode
make install-collection

# Verify
ansible-galaxy collection list | grep code3tech
```

---

## Creating Your Inventory

### Basic Inventory Structure

Create `inventory/hosts.ini`:

```ini
# inventory/hosts.ini
[gitlab_runners]
runner01.example.com ansible_host=192.168.1.100
runner02.example.com ansible_host=192.168.1.101

[gitlab_runners:vars]
ansible_user=ubuntu
ansible_become=true
ansible_python_interpreter=/usr/bin/python3
```

### YAML Inventory (Alternative)

Create `inventory/hosts.yml`:

```yaml
# inventory/hosts.yml
all:
  children:
    gitlab_runners:
      hosts:
        runner01.example.com:
          ansible_host: 192.168.1.100
        runner02.example.com:
          ansible_host: 192.168.1.101
      vars:
        ansible_user: ubuntu
        ansible_become: true
        ansible_python_interpreter: /usr/bin/python3
```

### Test Connectivity

```bash
# Test ping
ansible gitlab_runners -i inventory/hosts.ini -m ping

# Expected output:
# runner01.example.com | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

---

## Setting Up Ansible Vault

### Why Use Ansible Vault?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Why Ansible Vault?                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   WITHOUT VAULT (❌ Insecure)                                            │
│   ──────────────────────────                                             │
│   vars/gitlab.yml:                                                       │
│     gitlab_api_token: glpat-xxxxxxxxxxxxxxxxxxxx  # ❌ VISIBLE!         │
│                                                                          │
│   Problems:                                                              │
│   • Token visible in git history                                        │
│   • Anyone with repo access sees token                                  │
│   • Risk of accidental token exposure                                   │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   WITH VAULT (✅ Secure)                                                 │
│   ──────────────────                                                     │
│   vars/vault.yml (encrypted):                                           │
│     $ANSIBLE_VAULT;1.1;AES256                                           │
│     66633...encrypted...data...here...                                  │
│                                                                          │
│   vars/gitlab.yml:                                                       │
│     gitlab_api_token: "{{ vault_gitlab_api_token }}"  # ✅ Safe!        │
│                                                                          │
│   Benefits:                                                              │
│   • Token encrypted in git                                              │
│   • Requires vault password to decrypt                                  │
│   • Safe to commit to repository                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Creating a Vault File

#### Step 1: Create Vault Password File

```bash
# Create a secure password file (DO NOT commit this!)
echo "MySecureVaultPassword123!" > ~/.ansible_vault_pass

# Secure the file
chmod 600 ~/.ansible_vault_pass
```

#### Step 2: Create Encrypted Vault

```bash
# Create encrypted variables file
ansible-vault create vars/vault.yml \
  --vault-password-file ~/.ansible_vault_pass
```

This opens an editor. Add your tokens:

```yaml
# vars/vault.yml (encrypted)
---
# GitLab API Token (from previous step)
vault_gitlab_api_token: "glpat-xxxxxxxxxxxxxxxxxxxx"

# Docker Hub credentials (if using private images)
vault_dockerhub_username: "myuser"
vault_dockerhub_password: "mypassword"
```

Save and close. The file is now encrypted.

#### Step 3: Create Unencrypted Variables File

```bash
# Create vars/gitlab.yml (safe to commit)
cat > vars/gitlab.yml <<'EOF'
---
# Reference vault variables (this is safe!)
gitlab_api_token: "{{ vault_gitlab_api_token }}"
gitlab_url: "https://gitlab.com"

# Runner configuration
runners_executor: "docker"
# Note: Docker image must be configured manually in config.toml after registration
EOF
```

### Using Vault in Playbooks

```yaml
# playbook.yml
---
- name: Deploy GitLab Runners
  hosts: gitlab_runners
  become: true

  vars_files:
    - vars/vault.yml      # Encrypted file (requires password)
    - vars/gitlab.yml     # Public file (references vault vars)

  roles:
    - code3tech.devtools.gitlab_ci_runners
```

### Running Playbook with Vault

```bash
# Option 1: Prompt for password
ansible-playbook playbook.yml --ask-vault-pass

# Option 2: Use password file (recommended for automation)
ansible-playbook playbook.yml \
  --vault-password-file ~/.ansible_vault_pass
```

### Vault Cheat Sheet

```bash
# Create encrypted file
ansible-vault create vars/vault.yml

# Edit encrypted file
ansible-vault edit vars/vault.yml

# View encrypted file
ansible-vault view vars/vault.yml

# Encrypt existing file
ansible-vault encrypt vars/existing.yml

# Decrypt file (permanently)
ansible-vault decrypt vars/vault.yml

# Change vault password
ansible-vault rekey vars/vault.yml
```

---

## Verification Checklist

Before proceeding to installation, verify you have:

### ✅ GitLab Setup
- [ ] GitLab account (gitlab.com or self-hosted)
- [ ] Personal Access Token (PAT) created
- [ ] Token has correct scopes (`api`, `read_api`, `create_runner`)
- [ ] Token copied and saved securely
- [ ] Know your runner type (project/group/instance)
- [ ] Have project ID, group ID, or admin access

### ✅ Ansible Environment
- [ ] Ansible >= 2.15 installed (`ansible --version`)
- [ ] Python >= 3.9 installed (`python --version`)
- [ ] Collection installed (`ansible-galaxy collection list | grep devtools`)
- [ ] Inventory file created (`inventory/hosts.ini`)
- [ ] Can ping target hosts (`ansible all -m ping`)

### ✅ Target Servers
- [ ] SSH access working
- [ ] sudo/root privileges available
- [ ] Supported OS version (Ubuntu 22+, Debian 11+, RHEL 9+)
- [ ] Outbound HTTPS access to GitLab
- [ ] Docker installed (if using Docker executor)

### ✅ Security
- [ ] Ansible Vault file created (`vars/vault.yml`)
- [ ] Vault password file secured (`chmod 600 ~/.ansible_vault_pass`)
- [ ] Token stored in vault (NOT in plaintext files)
- [ ] Vault password file NOT committed to git

### ✅ Documentation
- [ ] Read [Part 1 - Introduction](01-introduction.md)
- [ ] Understand runner types (project/group/instance)
- [ ] Know which executor to use (Docker recommended)

---

## Quick Test

Run this command to verify everything is ready:

```bash
# Test full playbook syntax
ansible-playbook playbook.yml \
  --vault-password-file ~/.ansible_vault_pass \
  --syntax-check

# Test variable interpolation
ansible-playbook playbook.yml \
  --vault-password-file ~/.ansible_vault_pass \
  --check \
  --diff
```

---

## Next Steps

Everything configured? Great!

**Continue to [Part 3: Basic Installation](03-basic-installation.md)** to deploy your first runner.

Or jump to:
- **[Part 4: Runner Types](04-runner-types.md)** - Learn about project/group/instance runners
- **[Part 6: Production Deployment](06-production-deployment.md)** - Production patterns

---

## Troubleshooting

### "Collection not found"

```bash
# Verify collection installed
ansible-galaxy collection list | grep devtools

# If not found, install it
ansible-galaxy collection install code3tech.devtools
```

### "Cannot connect to hosts"

```bash
# Test SSH connection
ssh -i ~/.ssh/your_key ubuntu@runner01.example.com

# Test Ansible ping
ansible gitlab_runners -i inventory/hosts.ini -m ping
```

### "Vault password incorrect"

```bash
# Verify password file exists
cat ~/.ansible_vault_pass

# Try editing vault file (will prompt for password)
ansible-vault edit vars/vault.yml
```

---

[← Back to Guide Index](README.md)
