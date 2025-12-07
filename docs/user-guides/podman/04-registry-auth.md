# Registry Authentication

Configure authentication to private container registries for both root and rootless modes.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Root vs Rootless Authentication](#root-vs-rootless-authentication)
- [Common Registries](#common-registries)
- [Insecure Registries](#insecure-registries)
- [Troubleshooting](#troubleshooting)

---

## Overview

Podman supports authentication to private container registries in both root and rootless modes.

### Key Features

- ✅ Multiple registry support
- ✅ Per-user authentication (rootless)
- ✅ Secure credential handling with `no_log: true`
- ✅ Automatic permission fixes
- ✅ Credential cleanup option

### How It Works

| Mode | Auth File Location |
|------|-------------------|
| Root | `/root/.config/containers/auth.json` |
| Rootless | `~/.config/containers/auth.json` or `$XDG_RUNTIME_DIR/containers/auth.json` |

---

## Configuration

### Basic Configuration

```yaml
podman_registries_auth:
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_dockerhub_token }}"
```

### Multiple Registries

```yaml
podman_registries_auth:
  # Docker Hub
  - registry: "docker.io"
    username: "dockerhub-user"
    password: "{{ vault_dockerhub_token }}"
  
  # GitHub Container Registry
  - registry: "ghcr.io"
    username: "github-user"
    password: "{{ vault_github_token }}"
  
  # Quay.io
  - registry: "quay.io"
    username: "myorg+robot"
    password: "{{ vault_quay_token }}"
  
  # Private Registry
  - registry: "registry.company.com"
    username: "ci-service"
    password: "{{ vault_company_token }}"
```

### Variable Reference

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry hostname |
| `username` | string | Yes | Username or service account |
| `password` | string | Yes | Password or access token |

---

## Root vs Rootless Authentication

### Root Mode

When `podman_enable_rootless: false` or no rootless users configured:

```yaml
podman_registries_auth:
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_token }}"
```

**Behavior:**
- Authentication performed as root
- Credentials stored in `/root/.config/containers/auth.json`
- Available system-wide for root user

### Rootless Mode

When `podman_enable_rootless: true` and users configured:

```yaml
podman_enable_rootless: true
podman_rootless_users:
  - developer
  - jenkins

podman_registries_auth:
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_token }}"
```

**Behavior:**
- Role loops through each user in `podman_rootless_users`
- Each user authenticates to ALL registries in `podman_registries_auth`
- Uses `become_user` to switch to target user
- Credentials stored in user's auth file
- Each user has **isolated** authentication

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  ROOTLESS AUTHENTICATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   podman_rootless_users:        podman_registries_auth:     │
│   ┌──────────────────┐          ┌──────────────────┐        │
│   │ - developer      │          │ - docker.io      │        │
│   │ - jenkins        │          │ - ghcr.io        │        │
│   │ - deployer       │          │ - quay.io        │        │
│   └────────┬─────────┘          └────────┬─────────┘        │
│            │                             │                   │
│            └─────────────┬───────────────┘                   │
│                          │                                   │
│                          ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  For each USER, authenticate to each REGISTRY       │   │
│   │                                                      │   │
│   │  developer → docker.io, ghcr.io, quay.io            │   │
│   │  jenkins   → docker.io, ghcr.io, quay.io            │   │
│   │  deployer  → docker.io, ghcr.io, quay.io            │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Registries

### Docker Hub

```yaml
podman_registries_auth:
  - registry: "docker.io"
    username: "your-dockerhub-username"
    password: "{{ vault_dockerhub_token }}"
```

**Note:** Use Personal Access Token (PAT) instead of password.
**Create at:** https://hub.docker.com/settings/security

### GitHub Container Registry (GHCR)

```yaml
podman_registries_auth:
  - registry: "ghcr.io"
    username: "your-github-username"
    password: "{{ vault_github_token }}"
```

**Create at:** https://github.com/settings/tokens
- `read:packages` - Pull images
- `write:packages` - Push images

### Quay.io

```yaml
podman_registries_auth:
  - registry: "quay.io"
    username: "myorg+robot"
    password: "{{ vault_quay_robot_token }}"
```

**Tip:** Use Robot Accounts for automation.
**Create at:** https://quay.io/organization/YOUR_ORG?tab=robots

### Azure Container Registry

```yaml
podman_registries_auth:
  - registry: "myregistry.azurecr.io"
    username: "{{ azure_sp_app_id }}"
    password: "{{ vault_azure_sp_password }}"
```

### AWS ECR

```yaml
podman_registries_auth:
  - registry: "123456789.dkr.ecr.us-east-1.amazonaws.com"
    username: "AWS"
    password: "{{ ecr_auth_token }}"
```

**Note:** ECR tokens expire after 12 hours.

### Private Registry

```yaml
podman_registries_auth:
  - registry: "registry.company.com"
    username: "ci-user"
    password: "{{ vault_private_registry_password }}"
  
  - registry: "harbor.company.com:5000"
    username: "deployer"
    password: "{{ vault_harbor_password }}"
```

---

## Insecure Registries

For registries using HTTP or self-signed certificates.

### Configuration

```yaml
podman_insecure_registries:
  - "registry.internal.company.com:5000"
  - "192.168.1.100:5000"
  - "localhost:5000"

podman_registries_auth:
  - registry: "registry.internal.company.com:5000"
    username: "admin"
    password: "{{ vault_internal_password }}"
```

### What This Creates

In `/etc/containers/registries.conf`:

```toml
[[registry]]
location = "registry.internal.company.com:5000"
insecure = true

[[registry]]
location = "192.168.1.100:5000"
insecure = true
```

### Security Warning

⚠️ **Only use for trusted internal networks!**

Insecure registries:
- Don't verify TLS certificates
- Allow HTTP (unencrypted) connections
- Are vulnerable to MITM attacks

---

## Credential Management

### Clean Credentials Before Re-Auth

When rotating passwords or fixing credential issues:

```yaml
podman_clean_credentials: true
```

This removes existing credentials before authenticating.

### Credential Storage

| Mode | Path |
|------|------|
| Root | `/root/.config/containers/auth.json` |
| Rootless (XDG) | `$XDG_RUNTIME_DIR/containers/auth.json` |
| Rootless (Config) | `~/.config/containers/auth.json` |

### View Stored Credentials

```bash
# Root mode
sudo cat /root/.config/containers/auth.json

# Rootless mode
cat ~/.config/containers/auth.json
```

---

## Complete Example

### Playbook with Multiple Registries and Users

```yaml
---
- name: Podman with Registry Authentication
  hosts: podman_hosts
  become: true
  
  vars_files:
    - vars/secrets.yml
  
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
      - jenkins
      - deployer
    
    podman_registries_auth:
      # Docker Hub
      - registry: "docker.io"
        username: "{{ dockerhub_username }}"
        password: "{{ vault_dockerhub_token }}"
      
      # GitHub Container Registry
      - registry: "ghcr.io"
        username: "{{ github_username }}"
        password: "{{ vault_github_token }}"
      
      # Internal Registry
      - registry: "registry.company.com"
        username: "ci-service"
        password: "{{ vault_company_token }}"
    
    podman_insecure_registries:
      - "registry.internal.company.com:5000"
  
  roles:
    - code3tech.devtools.podman
```

### Vault File (vars/secrets.yml)

```yaml
# Encrypted with ansible-vault
vault_dockerhub_token: "dckr_pat_xxxxxxxxxxxxx"
vault_github_token: "ghp_xxxxxxxxxxxxxxxxxxxxx"
vault_company_token: "company_token_here"
```

---

## Troubleshooting

### Authentication Failed

```
Error: unauthorized: authentication required
```

**Solutions:**

1. Verify credentials are correct:
   ```bash
   podman login docker.io
   ```

2. Check registry hostname format:
   ```yaml
   # ✅ Correct for Podman
   registry: "docker.io"
   
   # ❌ Wrong (Docker format)
   registry: "https://index.docker.io/v1/"
   ```

3. Regenerate token at registry provider

### Permission Denied on Auth File

```
Error: permission denied reading auth.json
```

**Cause:** Auth file created as root but user can't read.

**Solution:** Role handles this automatically. Manual fix:
```bash
sudo chown $USER:$USER ~/.config/containers/auth.json
chmod 600 ~/.config/containers/auth.json
```

### XDG_RUNTIME_DIR Error

```
Error: XDG_RUNTIME_DIR not set
```

**Solution:** Set environment variable:
```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

### Registry Not in Search List

```
Error: short-name resolution failed
```

**Solution:** Add registry to search list:
```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io
    - ghcr.io  # Add your registry
```

Or use fully qualified name:
```bash
podman pull docker.io/library/alpine
```

---

## Best Practices

### 1. Always Use Vault

```bash
ansible-vault create vars/secrets.yml
```

### 2. Use Access Tokens

| Registry | Token Type |
|----------|------------|
| Docker Hub | Personal Access Token |
| GitHub | PAT with minimal scope |
| Quay | Robot Account Token |
| Azure | Service Principal |

### 3. Minimal Permissions

Only grant necessary scopes:
- Pull: `read:packages`
- Push: `write:packages`

### 4. Rotate Regularly

- Set expiration on tokens
- Use `podman_clean_credentials: true` when rotating

---

## Next Steps

- **[Rootless Configuration](05-rootless-config.md)** - Per-user setup
- **[Production Deployment](06-production-deployment.md)** - Complete playbooks

---

[← Back to Podman Documentation](README.md) | [Previous: Basic Installation](03-basic-installation.md) | [Next: Rootless Configuration →](05-rootless-config.md)
