# Part 7: Security Best Practices

> 🎬 **Video Tutorial Section**: Security is critical when using self-hosted runners. This section covers token protection, network security, runner isolation, and hardening strategies.

## 📋 Table of Contents

- [Security Overview](#security-overview)
- [Token Security with Ansible Vault](#token-security-with-ansible-vault)
- [Role Security Features](#role-security-features)
- [Network Security](#network-security)
- [Runner Isolation](#runner-isolation)
- [Public Repository Security](#public-repository-security)
- [File System Security](#file-system-security)
- [Container Security](#container-security)
- [Hardening Checklist](#hardening-checklist)
- [Security Audit Playbook](#security-audit-playbook)

---

## Security Overview

### Why Security Matters for Runners

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Self-Hosted Runner Risks                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   WHAT CAN A MALICIOUS WORKFLOW DO?                                     │
│   ─────────────────────────────────                                      │
│                                                                          │
│   ┌─────────────────┐                                                   │
│   │  Malicious PR   │                                                   │
│   │  (workflow)     │                                                   │
│   └────────┬────────┘                                                   │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Self-Hosted Runner                                              │   │
│   │                                                                 │   │
│   │  ⚠️ Access to:                                                  │   │
│   │  • All environment variables (secrets)                          │   │
│   │  • File system (previous job artifacts)                         │   │
│   │  • Network (internal services)                                  │   │
│   │  • Other repositories' credentials                              │   │
│   │  • Docker socket (root access!)                                 │   │
│   │  • Host system resources                                        │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   DEFENSE STRATEGIES:                                                    │
│   ────────────────────                                                   │
│   ✅ Use runner groups with access control                              │
│   ✅ Use ephemeral runners for untrusted code                           │
│   ✅ Use repository-scoped runners for sensitive repos                  │
│   ✅ Clean up work folders between jobs                                 │
│   ✅ Isolate runners on dedicated servers                               │
│   ✅ Use network segmentation                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Security Principles

| Principle | Implementation |
|-----------|----------------|
| **Least Privilege** | Runners can only access what they need |
| **Defense in Depth** | Multiple layers of security |
| **Isolation** | Runners isolated from each other |
| **Ephemeral** | Clean state for each job |
| **Audit Trail** | Log all actions |

---

## Token Security with Ansible Vault

### ⚠️ NEVER Store Tokens in Plain Text

```yaml
# ❌ WRONG - Token exposed in playbook
github_actions_runners_token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ❌ WRONG - Token exposed in inventory
[github_runners:vars]
github_actions_runners_token=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ✅ CORRECT - Use Ansible Vault
github_actions_runners_token: "{{ vault_github_token }}"
```

### Creating Vault-Encrypted Secrets

#### Step 1: Create Vault File

```bash
# Create encrypted vars file
ansible-vault create vars/github_secrets.yml

# Enter vault password when prompted
# Then add your secrets:
```

```yaml
# Inside the vault editor - this content is encrypted!
---
vault_github_token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
vault_github_org: "myorganization"
```

#### Step 2: Encrypt Individual Values

```bash
# Encrypt a single value
echo -n 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' | ansible-vault encrypt_string --stdin-name 'vault_github_token'

# Output:
vault_github_token: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31366561626234373139373630346639623833326133316161386262343434636232653232316635
          3265373766316265336336343833356335313065376132380a623865396331636630356661346234
          ...
```

#### Step 3: Use Encrypted Variables

```yaml
---
# playbook.yml
- name: Deploy Runners with Encrypted Token
  hosts: github_runners
  become: true

  vars_files:
    - vars/github_secrets.yml     # Load vault-encrypted file

  vars:
    # Reference the vault variable
    github_actions_runners_token: "{{ vault_github_token }}"
    github_actions_runners_organization: "{{ vault_github_org }}"

  roles:
    - code3tech.devtools.github_actions_runners
```

#### Step 4: Run with Vault

```bash
# Interactive password prompt
ansible-playbook playbook.yml -i inventory.ini --ask-vault-pass

# Or use password file (recommended for CI/CD)
ansible-playbook playbook.yml -i inventory.ini --vault-password-file ~/.vault_pass

# Multiple vault IDs for different environments
ansible-playbook playbook.yml -i inventory.ini \
  --vault-id prod@~/.vault_pass_prod \
  --vault-id dev@~/.vault_pass_dev
```

### Vault Best Practices

| Practice | Description |
|----------|-------------|
| **Rotate regularly** | Change tokens every 90 days |
| **Separate files** | Different vault files for different environments |
| **Git ignore** | Never commit vault password files |
| **Strong password** | Use complex vault passwords |
| **Backup** | Securely backup vault passwords |

---

## Role Security Features

### no_log Protection

The role uses `no_log: true` on **15 sensitive operations** to prevent token exposure:

```yaml
# Example: Token never appears in logs
- name: Register runner
  ansible.builtin.command: ./config.sh --token {{ token }} ...
  no_log: true        # ← Token hidden from logs!
```

**Protected operations:**
1. ✅ Token validation
2. ✅ Runner registration
3. ✅ Runner removal
4. ✅ Group creation (token in API calls)
5. ✅ Group updates
6. ✅ Label management
7. ✅ All API calls with authentication

### Verification

```bash
# Run playbook with debug output
ansible-playbook playbook.yml -i inventory.ini -vvv 2>&1 | grep -i "token"

# Should return NOTHING - tokens are censored!
```

---

## Network Security

### Firewall Configuration

```yaml
# GitHub Actions requires outbound access to:
# - github.com (HTTPS/443)
# - api.github.com (HTTPS/443)
# - *.actions.githubusercontent.com (HTTPS/443)
# - *.blob.core.windows.net (HTTPS/443) - for runner downloads

# Example: UFW firewall (Ubuntu/Debian)
- name: Allow outbound to GitHub
  community.general.ufw:
    rule: allow
    direction: out
    proto: tcp
    port: "443"
    to_ip: "{{ item }}"
  loop:
    - "140.82.112.0/20"     # GitHub
    - "143.55.64.0/20"      # GitHub Actions
    # Get current list from: https://api.github.com/meta
```

### Network Segmentation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Recommended Network Architecture                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        INTERNET                                 │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│                               ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                  FIREWALL / LOAD BALANCER                       │   │
│   │              (Only outbound 443 to GitHub)                      │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│        ┌──────────────────────┼──────────────────────┐                  │
│        │                      │                      │                   │
│        ▼                      ▼                      ▼                   │
│   ┌─────────┐           ┌─────────┐           ┌─────────┐              │
│   │ RUNNER  │           │ RUNNER  │           │ RUNNER  │              │
│   │ ZONE    │           │ ZONE    │           │ ZONE    │              │
│   │ (DMZ)   │           │ (DEV)   │           │ (PROD)  │              │
│   │         │           │         │           │         │              │
│   │ ❌ No   │           │ ✅ Dev  │           │ ✅ Prod │              │
│   │ Internal│           │ Access  │           │ Access  │              │
│   │ Access  │           │ Only    │           │ Only    │              │
│   └─────────┘           └─────────┘           └─────────┘              │
│        │                      │                      │                   │
│        │                      ▼                      ▼                   │
│        │                ┌───────────────────────────────────────────┐   │
│        │                │         INTERNAL SERVICES                 │   │
│        │                │   (databases, APIs, artifacts)            │   │
│        ✗                └───────────────────────────────────────────┘   │
│   (blocked!)                                                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Internal Network Access

```yaml
# Restrict runners to specific internal networks
# Use firewall rules on each runner server

# Example: Only allow access to artifact server
- name: Allow artifact server access
  community.general.ufw:
    rule: allow
    direction: out
    proto: tcp
    port: "443"
    to_ip: "10.0.10.0/24"    # Artifact server network only

- name: Block all other internal access
  community.general.ufw:
    rule: deny
    direction: out
    proto: tcp
    to_ip: "10.0.0.0/8"      # Block all internal
```

---

## Runner Isolation

### User Isolation

```yaml
# Each runner runs as dedicated user
github_actions_runners_user: "ghrunner"
github_actions_runners_group: "ghrunner"

# The role creates user with:
# - No password login
# - No sudo access
# - Home directory = runner directory
# - Restricted shell (optional)
```

### File System Isolation

```
/opt/github-actions-runners/
├── runner-01/                  # Runner 1 owns this ONLY
│   ├── _work/                 # Job execution here
│   ├── _diag/                 # Logs
│   └── config.json            # Runner config
│
├── runner-02/                  # Runner 2 owns this ONLY
│   ├── _work/
│   ├── _diag/
│   └── config.json
│
└── runner-03/
    └── ...

# Each runner CANNOT access other runner directories
# Permissions: 700 (owner only)
```

### Docker Socket Security

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Docker Socket Security Risk                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ⚠️ WARNING: Docker socket access = ROOT ACCESS!                       │
│                                                                          │
│   If runner can access /var/run/docker.sock:                            │
│   • Can mount host filesystem                                           │
│   • Can run privileged containers                                       │
│   • Can access all Docker resources                                     │
│                                                                          │
│   MITIGATION OPTIONS:                                                    │
│   ────────────────────                                                   │
│                                                                          │
│   Option 1: No Docker on runners                                        │
│   • Use GitHub-hosted runners for Docker workflows                      │
│   • Self-hosted for non-Docker only                                     │
│                                                                          │
│   Option 2: Docker-in-Docker (DinD)                                     │
│   • Run Docker daemon inside container                                  │
│   • Isolated from host                                                  │
│                                                                          │
│   Option 3: Podman (rootless)                                           │
│   • No daemon socket                                                    │
│   • User namespace isolation                                            │
│   • Recommended for security-conscious environments                     │
│                                                                          │
│   Option 4: Accept risk (internal trusted repos only)                   │
│   • Only for 100% internal code                                         │
│   • Runner group restricted to trusted repos                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Public Repository Security

### The Risk

```yaml
# PUBLIC REPOSITORY WORKFLOW:
#
# 1. Attacker forks your repo
# 2. Attacker adds malicious workflow
# 3. Attacker opens Pull Request
# 4. Workflow runs on YOUR self-hosted runner
# 5. Attacker has access to your infrastructure!
```

### Protection Strategies

#### Strategy 1: Never Use Self-Hosted for Public Repos

```yaml
# Most secure - just don't allow it
github_actions_runners_groups:
  - name: "internal-only"
    visibility: "all"
    allows_public_repos: false    # ← BLOCKED!
```

#### Strategy 2: Ephemeral + Isolated Runners

```yaml
# If you must support public repos:
github_actions_runners_groups:
  - name: "public-repos"
    visibility: "selected"
    selected_repositories:
      - "open-source-project"     # Specific repos only
    allows_public_repos: true

github_actions_runners_list:
  - name: "oss-runner-01"
    ephemeral: true               # Clean after each job
    runner_group: "public-repos"
```

#### Strategy 3: Require Approval for External Contributors

In repository settings (`Settings → Actions → General`):

```
Fork pull request workflows:
☑ Require approval for all outside collaborators
```

### Decision Matrix

| Scenario | Self-Hosted OK? | Configuration |
|----------|-----------------|---------------|
| Internal repo only | ✅ Yes | `allows_public_repos: false` |
| Public + trusted contributors | ⚠️ Careful | Ephemeral + approval |
| Public + external contributors | ❌ No | Use GitHub-hosted runners |
| Open source project | ⚠️ Careful | Ephemeral + isolated network |

---

## File System Security

### Sensitive File Locations

```
Runner Directory:
/opt/github-actions-runners/runner-01/
├── .credentials              # ⚠️ Runner credentials
├── .credentials_rsaparams    # ⚠️ RSA parameters
├── .runner                   # Runner identity
├── .path                     # PATH configuration
├── _diag/                    # Logs (may contain secrets)
└── _work/                    # Job data (may contain secrets)
```

### File Permissions

```yaml
# Role sets secure permissions:
# Runner directory: 700 (owner only)
# Credential files: 600 (owner read/write)
# Executable files: 700 (owner execute)
```

### Secure Cleanup

```yaml
# Enable cleanup to prevent data leakage
github_actions_runners_work_folder_cleanup_days: 1    # Daily cleanup

# What gets deleted:
# - Repository clones (may contain secrets in code)
# - Build artifacts
# - Downloaded tools
# - Temporary files
```

---

## Container Security

### Running Docker Securely

```yaml
# In your workflow, use security best practices:
jobs:
  build:
    runs-on: [self-hosted, docker]
    container:
      image: node:18
      options: >-
        --security-opt no-new-privileges
        --cap-drop ALL
        --read-only
```

### Using Podman Instead

```yaml
# Podman is more secure for self-hosted runners:
# - Rootless by default
# - No daemon socket
# - User namespace isolation

# Install Podman on runners with code3tech.devtools.podman role
- name: Setup Secure Container Runtime
  hosts: github_runners
  become: true

  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - ghrunner          # Runner user can use Podman

  roles:
    - code3tech.devtools.podman
```

---

## Hardening Checklist

### Server Hardening

```bash
# ☐ Operating System
- [ ] Regular security updates (unattended-upgrades)
- [ ] Minimal packages installed
- [ ] Remove unnecessary services
- [ ] Enable SELinux or AppArmor

# ☐ SSH Hardening
- [ ] Disable root login
- [ ] Use key-based authentication only
- [ ] Change default SSH port
- [ ] Use fail2ban

# ☐ Firewall
- [ ] Allow only required ports
- [ ] Block all inbound except SSH
- [ ] Restrict outbound to GitHub only
- [ ] Network segmentation
```

### Runner Hardening

```bash
# ☐ Runner Configuration
- [ ] Use dedicated runner user (no root)
- [ ] No sudo access for runner user
- [ ] Ephemeral mode for untrusted workflows
- [ ] Regular work folder cleanup
- [ ] Isolated runner groups

# ☐ Access Control
- [ ] Runner groups with selected repos
- [ ] Never allow public repos on persistent runners
- [ ] Require approval for fork PRs
- [ ] Audit runner access regularly
```

### Token Security

```bash
# ☐ Token Management
- [ ] Use Ansible Vault for all tokens
- [ ] Rotate tokens every 90 days
- [ ] Use fine-grained PATs with minimal scope
- [ ] Never commit tokens to git
- [ ] Different tokens for different environments
```

---

## Security Audit Playbook

### Comprehensive Security Check

```yaml
---
# security-audit.yml
# Audit security configuration of GitHub Actions runners

- name: Security Audit - GitHub Actions Runners
  hosts: github_runners
  become: true

  tasks:
    - name: "AUDIT: Check runner user privileges"
      ansible.builtin.command: id ghrunner
      changed_when: false
      register: runner_user

    - name: "AUDIT: Verify runner user has no sudo"
      ansible.builtin.shell: sudo -l -U ghrunner 2>&1 || true
      changed_when: false
      register: sudo_check

    - name: "AUDIT: Check file permissions on runner directories"
      ansible.builtin.find:
        paths: /opt/github-actions-runners
        file_type: directory
        recurse: false
      register: runner_dirs

    - name: "AUDIT: Verify credentials are protected"
      ansible.builtin.stat:
        path: "{{ item.path }}/.credentials"
      loop: "{{ runner_dirs.files }}"
      loop_control:
        label: "{{ item.path }}"
      register: cred_perms

    - name: "AUDIT: Check Docker socket access"
      ansible.builtin.stat:
        path: /var/run/docker.sock
      register: docker_sock

    - name: "AUDIT: Check runner group membership for Docker"
      ansible.builtin.shell: groups ghrunner | grep -w docker || true
      changed_when: false
      register: docker_group

    - name: "AUDIT: Verify firewall is active"
      ansible.builtin.command: ufw status
      changed_when: false
      register: firewall_status

    - name: "AUDIT: Check running services"
      ansible.builtin.shell: systemctl list-units 'actions.runner.*' --no-pager
      changed_when: false
      register: runner_services

    - name: "AUDIT: Check for pending security updates"
      ansible.builtin.shell: apt list --upgradable 2>/dev/null | grep -i security || true
      changed_when: false
      register: security_updates

    # ===========================================================================
    # GENERATE REPORT
    # ===========================================================================
    - name: Generate security audit report
      ansible.builtin.debug:
        msg: |
          
          ══════════════════════════════════════════════════════════════════
          SECURITY AUDIT REPORT - {{ inventory_hostname }}
          ══════════════════════════════════════════════════════════════════
          
          📋 RUNNER USER
          ─────────────────────────────────────────────────────────────────
          User info: {{ runner_user.stdout }}
          Sudo access: {{ 'NONE (✅ SECURE)' if 'not allowed' in sudo_check.stdout else '⚠️ HAS SUDO ACCESS!' }}
          
          🐳 DOCKER ACCESS
          ─────────────────────────────────────────────────────────────────
          Docker socket exists: {{ docker_sock.stat.exists | default(false) }}
          Runner in docker group: {{ '⚠️ YES' if docker_group.stdout else '✅ NO' }}
          
          🔥 FIREWALL
          ─────────────────────────────────────────────────────────────────
          Status: {{ firewall_status.stdout_lines[0] | default('UNKNOWN') }}
          
          🔄 PENDING UPDATES
          ─────────────────────────────────────────────────────────────────
          Security updates: {{ security_updates.stdout_lines | length }} pending
          
          🏃 RUNNER SERVICES
          ─────────────────────────────────────────────────────────────────
          {{ runner_services.stdout }}
          
          ══════════════════════════════════════════════════════════════════
```

Run the audit:

```bash
ansible-playbook security-audit.yml -i inventory.ini
```

---

## Summary

| Security Layer | Implementation |
|----------------|----------------|
| **Token Protection** | Ansible Vault, `no_log: true` |
| **User Isolation** | Dedicated user, no sudo |
| **File Security** | 700/600 permissions, cleanup |
| **Network** | Firewall, segmentation |
| **Access Control** | Runner groups, selected repos |
| **Public Repos** | Ephemeral runners, approval |
| **Containers** | Podman rootless, security options |
| **Auditing** | Regular security checks |

---

**Next Section**: [Part 8: Troubleshooting](08-troubleshooting.md) →

← **Previous Section**: [Part 6: Advanced Features](06-advanced-features.md)

---

[← Back to User Guides](../README.md)
