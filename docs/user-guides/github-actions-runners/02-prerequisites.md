# Part 2: Prerequisites & Setup

> 🎬 **Video Tutorial Section**: This section covers everything you need to prepare before deploying runners. Follow each step carefully - proper preparation prevents problems later!

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [GitHub Account Requirements](#github-account-requirements)
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
│   • Disk: 20GB minimum (more for Docker builds)                         │
│   • Network: Outbound internet access to github.com                     │
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
│     - github.com                                                        │
│     - api.github.com                                                    │
│     - *.actions.githubusercontent.com                                   │
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

## GitHub Account Requirements

### Understanding What You Need

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GitHub Requirements by Scope                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   REPOSITORY SCOPE                                                       │
│   ────────────────                                                       │
│   ✅ Any GitHub account                                                  │
│   ✅ Admin access to the repository                                      │
│   ✅ GitHub Free, Pro, Team, or Enterprise                               │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ORGANIZATION SCOPE                                                     │
│   ──────────────────                                                     │
│   ✅ GitHub Organization (not personal account)                          │
│   ✅ Owner or Admin role in the organization                             │
│   ✅ GitHub Team or Enterprise plan (for runner groups)                  │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ENTERPRISE SCOPE                                                       │
│   ─────────────────                                                      │
│   ✅ GitHub Enterprise Cloud or Server                                   │
│   ✅ Enterprise owner role                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Creating a Personal Access Token (PAT)

### Step-by-Step Guide with Screenshots

A Personal Access Token (PAT) is like a password that Ansible uses to communicate with GitHub.

#### Step 1: Navigate to Settings

1. Log into GitHub
2. Click your profile picture (top right)
3. Click **Settings**

```
┌───────────────────────────────┐
│  🔽 Your Profile Picture      │
│  ────────────────────────     │
│  Your profile                 │
│  Your repositories            │
│  Your projects                │
│  Your stars                   │
│  Your gists                   │
│  ────────────────────────     │
│  ⚙️ Settings  ← CLICK HERE    │
│  ────────────────────────     │
│  Sign out                     │
└───────────────────────────────┘
```

#### Step 2: Navigate to Developer Settings

1. Scroll down to the bottom of the left sidebar
2. Click **Developer settings**

```
┌───────────────────────────────┐
│  Settings                     │
│  ────────────────────────     │
│  Public profile               │
│  Account                      │
│  Appearance                   │
│  ...                          │
│  ────────────────────────     │
│  🔧 Developer settings ← HERE │
└───────────────────────────────┘
```

#### Step 3: Create Personal Access Token

1. Click **Personal access tokens**
2. Click **Tokens (classic)** - NOT "Fine-grained tokens"
3. Click **Generate new token**
4. Click **Generate new token (classic)**

```
┌───────────────────────────────────────────────────────────────────┐
│  Developer settings                                                │
│  ──────────────────                                                │
│                                                                    │
│  📱 GitHub Apps                                                    │
│  📱 OAuth Apps                                                     │
│  🔑 Personal access tokens                                         │
│     └── 🎫 Tokens (classic) ← USE THIS                            │
│     └── ⚡ Fine-grained tokens                                     │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  [Generate new token ▼]                                    │   │
│  │                                                            │   │
│  │   Generate new token (classic) ← CLICK THIS               │   │
│  │   Generate new token (Beta)                                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

#### Step 4: Configure Token Settings

Fill in the form:

```
┌───────────────────────────────────────────────────────────────────┐
│  New personal access token (classic)                               │
│  ──────────────────────────────────                                │
│                                                                    │
│  Note: ┌──────────────────────────────────────────┐               │
│        │ ansible-github-runners                   │               │
│        └──────────────────────────────────────────┘               │
│  ↑ A name to identify this token                                  │
│                                                                    │
│  Expiration: ┌──────────────────────────────────────────┐         │
│              │ 90 days ▼                                │         │
│              └──────────────────────────────────────────┘         │
│  ↑ Choose based on your security requirements                     │
│    • 30 days = More secure, requires frequent renewal             │
│    • 90 days = Good balance                                       │
│    • No expiration = ⚠️ Less secure, use only if needed          │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

#### Step 5: Select Required Scopes

**CRITICAL**: Select the correct scopes based on your runner scope:

```
┌───────────────────────────────────────────────────────────────────┐
│  Select scopes                                                     │
│  ─────────────                                                     │
│                                                                    │
│  FOR REPOSITORY RUNNERS:                                           │
│  ────────────────────────                                          │
│  ☑️ repo (Full control of private repositories)                   │
│     ☑️ repo:status                                                 │
│     ☑️ repo_deployment                                             │
│     ☑️ public_repo                                                 │
│     ☑️ repo:invite                                                 │
│     ☑️ security_events                                             │
│                                                                    │
│  ─────────────────────────────────────────────────────────────    │
│                                                                    │
│  FOR ORGANIZATION RUNNERS:                                         │
│  ──────────────────────────                                        │
│  ☑️ admin:org (Full control of orgs and teams)                    │
│     ☑️ write:org                                                   │
│     ☑️ read:org                                                    │
│     ☑️ manage_runners:org  ← IMPORTANT for runner groups          │
│                                                                    │
│  ─────────────────────────────────────────────────────────────    │
│                                                                    │
│  FOR ENTERPRISE RUNNERS:                                           │
│  ────────────────────────                                          │
│  ☑️ admin:enterprise                                               │
│     ☑️ manage_runners:enterprise                                   │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

**Scope Selection Summary:**

| Runner Scope | Required PAT Scopes |
|--------------|---------------------|
| Repository | `repo` |
| Organization | `admin:org`, `manage_runners:org` |
| Enterprise | `admin:enterprise`, `manage_runners:enterprise` |

#### Step 6: Generate and Save Token

1. Scroll down and click **Generate token**
2. **IMMEDIATELY COPY THE TOKEN** - You won't see it again!

```
┌───────────────────────────────────────────────────────────────────┐
│  ✅ Personal access token created                                  │
│  ────────────────────────────────                                  │
│                                                                    │
│  ⚠️ Make sure to copy your personal access token now.             │
│     You won't be able to see it again!                            │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   [📋 Copy]      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ⬆️ COPY THIS NOW! Save it somewhere safe (you'll need it later) │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

**⚠️ IMPORTANT**: 
- Never commit this token to Git
- Store it securely (we'll use Ansible Vault)
- Treat it like a password

---

## Ansible Environment Setup

### Option A: Using the Collection's Virtual Environment (Recommended)

If you cloned the `code3tech.devtools` repository:

```bash
# Navigate to the collection directory
cd /path/to/ansible-col-devtools

# Activate the virtual environment
# This script creates the venv if it doesn't exist
source activate.sh

# Verify Ansible is available
ansible --version
```

**Expected output:**

```
ansible [core 2.15.0]
  config file = /path/to/ansible-col-devtools/ansible.cfg
  configured module search path = ...
  ansible python module location = ...
  ansible collection location = ...
  executable location = ...
  python version = 3.11.x
```

### Option B: Manual Setup

```bash
# Create a new directory for your project
mkdir my-github-runners
cd my-github-runners

# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install Ansible
pip install ansible

# Verify installation
ansible --version
```

---

## Installing the Collection

### Method 1: From Ansible Galaxy (Production)

```bash
# Install the collection from Galaxy
ansible-galaxy collection install code3tech.devtools

# Install required dependencies
ansible-galaxy collection install community.general
```

### Method 2: From Source (Development)

```bash
# Clone the repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Install the collection locally
ansible-galaxy collection install .

# Or build and install
make build
make install-collection
```

### Verify Installation

```bash
# Check collection is installed
ansible-galaxy collection list | grep code3tech

# Expected output:
# code3tech.devtools  1.2.0
```

---

## Creating Your Inventory

### What is an Inventory?

An inventory tells Ansible **which servers** to manage:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Inventory Concept                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ANSIBLE CONTROLLER                    TARGET SERVERS                  │
│   (Your laptop/workstation)             (Where runners run)             │
│                                                                          │
│   ┌───────────────────┐                ┌───────────────────┐           │
│   │  Ansible          │ ─── SSH ────▶  │  server1          │           │
│   │  + Inventory      │                │  192.168.1.10     │           │
│   │  + Playbook       │                └───────────────────┘           │
│   │                   │                                                 │
│   │                   │                ┌───────────────────┐           │
│   │                   │ ─── SSH ────▶  │  server2          │           │
│   │                   │                │  192.168.1.11     │           │
│   └───────────────────┘                └───────────────────┘           │
│                                                                          │
│   Inventory defines: server1 = 192.168.1.10                             │
│                     server2 = 192.168.1.11                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Create Inventory File

Create a file named `inventory.ini`:

```ini
# inventory.ini
# Define the servers where GitHub runners will be installed

# ============================================================================
# RUNNER SERVERS
# ============================================================================
# List all servers that will run GitHub Actions runners
# Each line is a server - use hostnames or IP addresses

[github_runners]
# Format: hostname_or_ip  ansible_user=username

# Option 1: Using IP addresses
192.168.1.100  ansible_user=deploy
192.168.1.101  ansible_user=deploy

# Option 2: Using hostnames (requires DNS or /etc/hosts)
# runner01.example.com  ansible_user=deploy
# runner02.example.com  ansible_user=deploy

# Option 3: Single server (for testing)
# localhost  ansible_connection=local

# ============================================================================
# GROUP VARIABLES
# ============================================================================
# These settings apply to ALL servers in the [github_runners] group

[github_runners:vars]
# SSH settings
ansible_user=deploy                    # SSH username
ansible_become=true                    # Use sudo for privileged operations
ansible_python_interpreter=/usr/bin/python3

# Optional: SSH key location
# ansible_ssh_private_key_file=~/.ssh/id_rsa

# Optional: Custom SSH port
# ansible_port=22
```

### Alternative: YAML Inventory

Some people prefer YAML format. Create `inventory.yml`:

```yaml
# inventory.yml
# YAML format inventory for GitHub runners

all:
  children:
    github_runners:
      hosts:
        # Server 1: Production runner
        runner-prod-01:
          ansible_host: 192.168.1.100
          ansible_user: deploy
          
        # Server 2: Production runner
        runner-prod-02:
          ansible_host: 192.168.1.101
          ansible_user: deploy
          
        # Server 3: Development runner
        runner-dev-01:
          ansible_host: 192.168.1.110
          ansible_user: deploy

      vars:
        # Common settings for all runners
        ansible_become: true
        ansible_python_interpreter: /usr/bin/python3
```

### Test Connectivity

Before proceeding, verify Ansible can connect to your servers:

```bash
# Test connection to all servers
ansible github_runners -i inventory.ini -m ping

# Expected output (all green):
# 192.168.1.100 | SUCCESS => {
#     "ping": "pong"
# }
# 192.168.1.101 | SUCCESS => {
#     "ping": "pong"
# }
```

**If connection fails**, check:
1. SSH key is set up correctly
2. User has sudo access
3. Server is reachable (ping, firewall)

---

## Setting Up Ansible Vault

### Why Use Ansible Vault?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Why Encrypt Secrets?                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ❌ WITHOUT ENCRYPTION (DANGEROUS!)                                    │
│   ──────────────────────────────────                                     │
│   # playbook.yml                                                        │
│   vars:                                                                  │
│     github_token: "ghp_REAL_TOKEN_HERE"  # ← EXPOSED IN GIT!           │
│                                                                          │
│   Problems:                                                              │
│   • Token visible in plain text                                         │
│   • Accidentally committed to Git                                        │
│   • Anyone with repo access sees it                                      │
│   • Token could be scraped by bots                                       │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   ✅ WITH ANSIBLE VAULT (SECURE)                                        │
│   ───────────────────────────────                                        │
│   # playbook.yml                                                        │
│   vars:                                                                  │
│     github_token: "{{ vault_github_token }}"  # ← Reference only       │
│                                                                          │
│   # vars/secrets.yml (ENCRYPTED)                                        │
│   $ANSIBLE_VAULT;1.1;AES256                                             │
│   3936313531353738...  # ← Encrypted, safe to commit                    │
│                                                                          │
│   Benefits:                                                              │
│   • Secrets encrypted at rest                                           │
│   • Can be committed to Git safely                                      │
│   • Only decrypted at runtime                                           │
│   • Access controlled by vault password                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Vault Directory

```bash
# Create a vars directory for secrets
mkdir -p vars

# Create an empty vault file
touch vars/github_secrets.yml
```

### Step 2: Create the Encrypted Vault File

```bash
# Create and encrypt the secrets file
# You'll be prompted for a vault password - REMEMBER IT!
ansible-vault create vars/github_secrets.yml
```

When the editor opens, add your secrets:

```yaml
# vars/github_secrets.yml (this is what you type inside the editor)
---
# GitHub Personal Access Token
# Get this from: https://github.com/settings/tokens
vault_github_token: "ghp_PASTE_YOUR_TOKEN_HERE"

# Organization name
vault_github_org: "your-organization-name"

# Optional: Multiple tokens for different purposes
# vault_github_token_readonly: "ghp_ANOTHER_TOKEN"
```

**Save and exit the editor** (`:wq` in vim, `Ctrl+X` in nano).

### Step 3: Verify Encryption

```bash
# View the encrypted file (should be scrambled)
cat vars/github_secrets.yml

# Expected output (encrypted):
# $ANSIBLE_VAULT;1.1;AES256
# 3936313531353738326535323865393036363434353164353962323464343236
# ...
```

### Step 4: View/Edit Encrypted File

```bash
# View contents (requires password)
ansible-vault view vars/github_secrets.yml

# Edit contents (requires password)
ansible-vault edit vars/github_secrets.yml
```

### Step 5: Create Vault Password File (Optional but Recommended)

For CI/CD or automation, use a password file instead of typing:

```bash
# Create password file
echo "your-vault-password" > .vault_pass

# Secure it (IMPORTANT!)
chmod 600 .vault_pass

# Add to .gitignore (CRITICAL!)
echo ".vault_pass" >> .gitignore
```

Now you can run playbooks without typing the password:

```bash
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

### Alternative: Encrypt Single Variable

If you prefer to encrypt only specific values:

```bash
# Encrypt a single string
ansible-vault encrypt_string 'ghp_YOUR_TOKEN_HERE' --name 'vault_github_token'

# Output (copy this to your vars file):
# vault_github_token: !vault |
#           $ANSIBLE_VAULT;1.1;AES256
#           3936313531353738...
```

---

## Verification Checklist

Before proceeding, verify everything is set up correctly:

### Pre-Flight Checklist

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Pre-Flight Verification Checklist                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ☐ GITHUB PREPARATION                                                   │
│  ─────────────────────                                                   │
│  ☐ GitHub account with appropriate access                               │
│  ☐ Personal Access Token created                                        │
│  ☐ PAT has correct scopes for your runner scope                         │
│  ☐ PAT copied and saved securely                                        │
│                                                                          │
│  ☐ ANSIBLE ENVIRONMENT                                                  │
│  ──────────────────────                                                  │
│  ☐ Python 3.9+ installed                                                │
│  ☐ Ansible 2.15+ installed                                              │
│  ☐ Virtual environment activated                                         │
│  ☐ code3tech.devtools collection installed                              │
│                                                                          │
│  ☐ INVENTORY                                                            │
│  ───────────                                                             │
│  ☐ inventory.ini created with target servers                            │
│  ☐ SSH connectivity verified (ansible -m ping)                          │
│  ☐ Sudo access confirmed                                                │
│                                                                          │
│  ☐ SECRETS                                                              │
│  ─────────                                                               │
│  ☐ vars/github_secrets.yml created and encrypted                        │
│  ☐ vault_github_token variable set                                      │
│  ☐ Vault password remembered or saved in .vault_pass                    │
│  ☐ .vault_pass added to .gitignore                                      │
│                                                                          │
│  ☐ TARGET SERVERS                                                       │
│  ────────────────                                                        │
│  ☐ Servers running supported OS                                         │
│  ☐ Outbound internet access to github.com                               │
│  ☐ At least 2GB RAM, 20GB disk                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Quick Verification Commands

Run these commands to verify your setup:

```bash
# 1. Check Ansible version
ansible --version
# ✅ Should be 2.15 or higher

# 2. Check collection is installed
ansible-galaxy collection list | grep code3tech
# ✅ Should show code3tech.devtools

# 3. Check inventory is valid
ansible-inventory -i inventory.ini --list
# ✅ Should show your servers

# 4. Test SSH connectivity
ansible github_runners -i inventory.ini -m ping
# ✅ All servers should return "pong"

# 5. Test vault decryption
ansible-vault view vars/github_secrets.yml
# ✅ Should show your secrets (after entering password)

# 6. Test sudo access on servers
ansible github_runners -i inventory.ini -m command -a "whoami" --become
# ✅ Should return "root" for all servers
```

---

## Directory Structure Summary

After completing this setup, your directory should look like:

```
my-github-runners/                   # Your project directory
├── .vault_pass                      # Vault password (GITIGNORE!)
├── .gitignore                       # Ignore sensitive files
├── inventory.ini                    # Server inventory
├── vars/
│   └── github_secrets.yml           # Encrypted secrets (safe to commit)
└── playbooks/                       # Your playbooks (we'll create next)
    └── (empty for now)
```

### Sample .gitignore

```gitignore
# .gitignore
# Sensitive files
.vault_pass
*.retry

# Virtual environment
.venv/
venv/

# Python cache
__pycache__/
*.pyc

# Ansible temporary files
*.retry
.ansible/
```

---

## Summary: What You've Prepared

| Component | Status | Purpose |
|-----------|--------|---------|
| **GitHub PAT** | Created | Authentication to GitHub API |
| **Ansible** | Installed | Automation engine |
| **Collection** | Installed | GitHub runners role |
| **Inventory** | Created | Target server definitions |
| **Vault** | Configured | Secure secret storage |

---

**Next Section**: [Part 3: Basic Installation](03-basic-installation.md) →

← **Previous Section**: [Part 1: Introduction & Concepts](01-introduction.md)

---

[← Back to User Guides](../README.md)
