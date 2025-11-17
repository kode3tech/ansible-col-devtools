# Private Registry Authentication

This document explains how to configure private container registry authentication for both Docker and Podman roles.

## 📋 Table of Contents

- [Overview](#overview)
- [Security Best Practices](#security-best-practices)
- [Docker Registry Authentication](#docker-registry-authentication)
- [Podman Registry Authentication](#podman-registry-authentication)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

## Overview

Both `docker` and `podman` roles support authenticating to private container registries. This is essential for:

- **CI/CD pipelines**: Pulling private images during builds
- **Enterprise deployments**: Accessing corporate registry
- **Multi-registry workflows**: Working with Docker Hub, GitHub Container Registry (GHCR), Quay.io, etc.

### Key Features

- ✅ Multiple registry support
- ✅ Secure credential handling with `no_log: true`
- ✅ Password or password file authentication
- ✅ Rootless Podman support (per-user authentication)
- ✅ Idempotent operations

### Requirements

#### Docker Role
- Collection: `community.docker` >= 3.4.0
- Module: `community.docker.docker_login`

#### Podman Role
- Collection: `containers.podman` >= 1.10.0
- Module: `containers.podman.podman_login`

Install dependencies:
```bash
ansible-galaxy collection install -r requirements.yml
```

## Security Best Practices

### ⚠️ CRITICAL: Never Commit Plain-Text Passwords!

**Always** use Ansible Vault to encrypt sensitive data.

### Using Ansible Vault

#### 1. Create Encrypted Variables

```bash
# Create vault file
ansible-vault create vars/registry_secrets.yml

# Add your passwords (inside vault editor):
vault_dockerhub_password: "dckr_pat_your_token_here"
vault_ghcr_token: "ghp_your_github_token"
vault_registry_password: "your_private_registry_password"
```

#### 2. Encrypt Individual Strings

```bash
# Encrypt a single password
ansible-vault encrypt_string 'my_secret_password' --name 'vault_registry_password'

# Output (add to your vars):
vault_registry_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted data...
```

#### 3. Reference Encrypted Variables

```yaml
# In your playbook or vars file
docker_registries_auth:
  - registry: "registry.example.com"
    username: "myuser"
    password: "{{ vault_registry_password }}"  # ✅ Safe!
```

#### 4. Run Playbook with Vault

```bash
# Interactive password prompt
ansible-playbook playbook.yml --ask-vault-pass

# Or use password file
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass

# Multiple vault IDs
ansible-playbook playbook.yml --vault-id prod@~/.vault_pass_prod
```

### Alternative: Password Files

For integration with external secret management (HashiCorp Vault, AWS Secrets Manager, etc.):

```yaml
docker_registries_auth:
  - registry: "registry.example.com"
    username: "ci-user"
    password_file: "/var/lib/jenkins/secrets/registry-password"
```

**Note**: Ensure the password file has appropriate permissions (600 or 400).

## Docker Registry Authentication

### ⚠️ Important: Docker CLI Web-Based Login vs API Login

**When testing manually**, the Docker CLI may use web-based authentication for Docker Hub:

```bash
$ docker login
# This prompts for web-based login (OAuth)
```

**However**, our Ansible role uses the `community.docker.docker_login` module which:
- ✅ Uses the Docker API directly (non-interactive)
- ✅ Works with username/password or tokens
- ✅ Does NOT require web browser authentication
- ✅ Perfect for automation and CI/CD

### Configuration

Add to your playbook or `group_vars`:

```yaml
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"  # Docker Hub (full URL required)
    username: "dockerhub-user"
    password: "{{ vault_dockerhub_token }}"
    email: "user@example.com"  # Optional
  
  - registry: "ghcr.io"  # GitHub Container Registry
    username: "github-user"
    password: "{{ vault_github_token }}"
  
  - registry: "registry.mycompany.com"  # Private registry (hostname only)
    username: "ci-user"
    password: "{{ vault_private_registry_password }}"
```

### Variable Reference

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry URL. Docker Hub: `https://index.docker.io/v1/`, others: hostname |
| `username` | string | Yes | Registry username |
| `password` | string | No* | User password or token |
| `password_file` | string | No* | Path to file containing password |
| `email` | string | No | User email (legacy, rarely needed) |

**Note**: Either `password` or `password_file` must be provided.

### How It Works

1. Role executes `community.docker.docker_login` module
2. Credentials are stored in `~/.docker/config.json`
3. Task uses `no_log: true` to prevent credential exposure in logs
4. Login is performed **system-wide** (affects all users)

### Example Playbook

```yaml
---
- name: Setup Docker with registry authentication
  hosts: docker_hosts
  become: true
  
  vars_files:
    - vars/registry_secrets.yml
  
  vars:
    docker_registries_auth:
      - registry: "registry.company.com"
        username: "{{ registry_username }}"
        password: "{{ vault_registry_password }}"
  
  roles:
    - kode3tech.devtools.docker
```

## Podman Registry Authentication

### Configuration

Podman supports both **root** and **rootless** authentication modes.

#### Root Mode (System-Wide)

When `podman_enable_rootless: false`:

```yaml
podman_registries_auth:
  - registry: "docker.io"
    username: "dockerhub-user"
    password: "{{ vault_dockerhub_token }}"
  
  - registry: "quay.io"
    username: "quay-user"
    password: "{{ vault_quay_password }}"
```

#### Rootless Mode (Per-User)

When `podman_enable_rootless: true` and users are configured:

```yaml
podman_enable_rootless: true
podman_rootless_users:
  - devuser
  - jenkins
  - deployer

podman_registries_auth:
  - registry: "docker.io"
    username: "dockerhub-user"
    password: "{{ vault_dockerhub_token }}"
  
  - registry: "registry.mycompany.com"
    username: "ci-user"
    password: "{{ vault_private_registry_password }}"
```

**Behavior**: Each user in `podman_rootless_users` will be authenticated to **all** registries in `podman_registries_auth`.

### Variable Reference

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry hostname. Docker Hub: `docker.io`, Quay: `quay.io`, private: `registry.example.com:5000` |
| `username` | string | Yes | Registry username |
| `password` | string | No* | User password or token |
| `password_file` | string | No* | Path to file containing password |

**Note**: Either `password` or `password_file` must be provided.

### How It Works

#### Root Mode
1. Role executes `containers.podman.podman_login` as root
2. Credentials stored in `/root/.config/containers/auth.json`
3. Available system-wide for root user

#### Rootless Mode
1. Role loops through `podman_rootless_users`
2. For each user, authenticates to each registry
3. Uses `become_user` to switch to target user
4. Credentials stored in user's `$XDG_RUNTIME_DIR/containers/auth.json`
5. Each user has isolated authentication

### Example Playbook

```yaml
---
- name: Setup Podman with rootless registry auth
  hosts: podman_hosts
  become: true
  
  vars_files:
    - vars/registry_secrets.yml
  
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - devuser
      - jenkins
    
    podman_registries_auth:
      - registry: "docker.io"
        username: "{{ dockerhub_username }}"
        password: "{{ vault_dockerhub_token }}"
      
      - registry: "registry.company.com"
        username: "{{ registry_username }}"
        password: "{{ vault_registry_password }}"
  
  roles:
    - kode3tech.devtools.podman
```

## Common Use Cases

### 1. Docker Hub Private Repositories

```yaml
# For Docker
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"  # Full URL required for Docker
    username: "your-dockerhub-username"
    password: "{{ vault_dockerhub_token }}"

# For Podman
podman_registries_auth:
  - registry: "docker.io"  # Hostname only for Podman
    username: "your-dockerhub-username"
    password: "{{ vault_dockerhub_token }}"
```

**Note**: Use Personal Access Token (PAT) instead of password. Create at: https://hub.docker.com/settings/security

### 2. GitHub Container Registry (GHCR)

```yaml
docker_registries_auth:
  - registry: "ghcr.io"
    username: "your-github-username"
    password: "{{ vault_github_token }}"
```

**Note**: Generate token with `read:packages` scope at: https://github.com/settings/tokens

### 3. Quay.io

```yaml
podman_registries_auth:
  - registry: "quay.io"
    username: "your-quay-username"
    password: "{{ vault_quay_robot_token }}"
```

**Tip**: Use Robot Accounts for CI/CD: https://quay.io/organization/YOUR_ORG?tab=robots

### 4. Self-Hosted Registry (Harbor, Nexus, Artifactory)

```yaml
docker_registries_auth:
  - registry: "harbor.company.com"
    username: "{{ registry_username }}"
    password: "{{ vault_harbor_password }}"

podman_registries_auth:
  - registry: "nexus.company.com:5000"
    username: "{{ registry_username }}"
    password: "{{ vault_nexus_password }}"
```

### 5. Multiple Registries with Same Credentials

```yaml
# Use YAML anchors to avoid repetition
_registry_auth: &registry_auth
  username: "{{ common_username }}"
  password: "{{ vault_common_password }}"

docker_registries_auth:
  - registry: "docker.io"
    <<: *registry_auth
  
  - registry: "quay.io"
    <<: *registry_auth
  
  - registry: "ghcr.io"
    <<: *registry_auth
```

## Troubleshooting

### Authentication Fails

#### Check Credentials
```bash
# Test manually on target host
docker login registry.example.com -u username -p password
podman login registry.example.com -u username -p password
```

#### Verify Registry URL Format
**Important**: Different tools use different URL formats!

| Registry | Docker (`registry`) | Podman (`registry`) |
|----------|---------------------|---------------------|
| Docker Hub | `https://index.docker.io/v1/` | `docker.io` |
| GitHub (GHCR) | `ghcr.io` | `ghcr.io` |
| Quay.io | `quay.io` | `quay.io` |
| Private | `registry.example.com` | `registry.example.com` |
| Private with port | `registry.example.com:5000` | `registry.example.com:5000` |

**Docker Special Case**: Docker Hub requires the full API URL `https://index.docker.io/v1/`, while Podman uses just `docker.io`.

#### Check Network Connectivity
```bash
curl -I https://registry.example.com/v2/
```

### Docker CLI Shows Web-Based Login

When testing `docker login` manually, you might see:

```bash
$ docker login
USING WEB-BASED LOGIN
Press ENTER to open your browser...
```

**This is normal!** Modern Docker CLI uses OAuth web-based authentication for Docker Hub by default.

**Our Ansible role uses the Docker API** (via `community.docker.docker_login`), which:
- ✅ Works without browser (non-interactive)
- ✅ Uses username/password or tokens directly
- ✅ Perfect for automation

**To test manually with username/password** (like our role does):
```bash
docker login -u <username>
# Then enter password when prompted
```

### Rootless Podman Issues

#### User Not Configured
Ensure user is in `podman_rootless_users`:
```yaml
podman_rootless_users:
  - myuser
```

#### Subuid/Subgid Not Set
Role automatically configures, but verify:
```bash
cat /etc/subuid | grep username
cat /etc/subgid | grep username
```

#### XDG_RUNTIME_DIR Not Set
Rootless Podman requires `XDG_RUNTIME_DIR`. Role handles this, but if issues persist:
```bash
# As the user
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

### Password File Not Found

If using `password_file`:
```yaml
- registry: "registry.example.com"
  username: "user"
  password_file: "/path/to/password"
```

Ensure:
1. File exists on target host
2. File is readable by the user performing login
3. File contains only the password (no newlines)

```bash
# Create password file
echo -n "my_password" > /secure/path/registry-password
chmod 600 /secure/path/registry-password
```

### Credentials Not Persisting

#### Docker
Credentials stored in `~/.docker/config.json`. If missing:
```bash
ls -la ~/.docker/config.json
cat ~/.docker/config.json
```

#### Podman (Root)
Credentials stored in `/root/.config/containers/auth.json`:
```bash
sudo cat /root/.config/containers/auth.json
```

#### Podman (Rootless)
Credentials stored in user's `~/.config/containers/auth.json`:
```bash
# As the user
cat ~/.config/containers/auth.json
```

### Vault Decryption Errors

```
ERROR! Attempting to decrypt but no vault secrets found
```

**Solution**: Ensure you're providing vault password:
```bash
ansible-playbook playbook.yml --ask-vault-pass
# or
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass
```

### Task Shows Changed Every Run

This is expected behavior. Login modules don't have proper idempotency detection. As long as login succeeds, this is normal.

To suppress:
```yaml
- name: Login to registries
  community.docker.docker_login:
    registry_url: "{{ item.registry }}"
    username: "{{ item.username }}"
    password: "{{ item.password }}"
  loop: "{{ docker_registries_auth }}"
  no_log: true
  changed_when: false  # ⚠️ Use with caution!
```

## References

- [Docker Login Module Documentation](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_login_module.html)
- [Podman Login Module Documentation](https://docs.ansible.com/ansible/latest/collections/containers/podman/podman_login_module.html)
- [Ansible Vault Documentation](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Docker Hub Personal Access Tokens](https://docs.docker.com/security/for-developers/access-tokens/)
- [GitHub Container Registry Authentication](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
- [Quay.io Robot Accounts](https://docs.quay.io/glossary/robot-accounts.html)

---

[← Back to User Guides](README.md)

**Security Reminder**: Always use Ansible Vault for sensitive data. Never commit passwords to version control! 🔒
