# Registry Authentication

Complete guide to configuring private container registry authentication with automatic permission handling.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Registry URL Formats](#registry-url-formats)
- [Permission Handling](#permission-handling)
- [Common Registries](#common-registries)
- [Insecure Registries](#insecure-registries)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Docker role supports **comprehensive** authentication to private container registries.

### Key Features

- ✅ Multiple registry support
- ✅ Secure credential handling with `no_log: true`
- ✅ Automatic permission fixes for user config files
- ✅ SELinux context restoration (RHEL/CentOS)
- ✅ Non-interactive authentication (perfect for CI/CD)

### How It Works

1. Role executes `community.docker.docker_login` module
2. Credentials are stored in `~/.docker/config.json`
3. Permission fix tasks run automatically
4. Files get correct user ownership
5. SELinux contexts restored (if enabled)

---

## Configuration

### Basic Configuration

```yaml
docker_registries_auth:
  - registry: "ghcr.io"
    username: "myuser"
    password: "{{ vault_github_token }}"
```

### Multiple Registries

```yaml
docker_registries_auth:
  # Docker Hub (IMPORTANT: Use full URL!)
  - registry: "https://index.docker.io/v1/"
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
  
  # Private Enterprise Registry
  - registry: "registry.company.com"
    username: "ci-service"
    password: "{{ vault_company_token }}"
```

### Variable Reference

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry URL (see format table below) |
| `username` | string | Yes | Registry username |
| `password` | string | Yes | Password or access token |
| `email` | string | No | User email (legacy, rarely needed) |

---

## Registry URL Formats

⚠️ **Critical:** Different registries require different URL formats!

| Registry | URL Format | Notes |
|----------|------------|-------|
| **Docker Hub** | `https://index.docker.io/v1/` | Full URL required! |
| **GitHub (GHCR)** | `ghcr.io` | Hostname only |
| **Quay.io** | `quay.io` | Hostname only |
| **Azure ACR** | `myregistry.azurecr.io` | Hostname only |
| **AWS ECR** | `123456789.dkr.ecr.region.amazonaws.com` | Full ECR URL |
| **Google GCR** | `gcr.io` or `us-docker.pkg.dev` | Hostname only |
| **Harbor** | `harbor.company.com` | Hostname only |
| **Nexus** | `nexus.company.com:5000` | Include port if non-standard |
| **Private HTTP** | `192.168.1.100:5000` | Also add to insecure_registries |

### Docker Hub Special Case

Docker Hub requires the **full API URL**:

```yaml
# ✅ CORRECT for Docker Hub
- registry: "https://index.docker.io/v1/"
  username: "myuser"
  password: "{{ vault_token }}"

# ❌ WRONG - will fail!
- registry: "docker.io"
  username: "myuser"
  password: "{{ vault_token }}"
```

---

## Permission Handling

### The Problem

On Linux systems, Docker login may create `~/.docker/config.json` as `root:root` when using sudo/become, causing permission denied errors for regular users.

### The Solution

The role **automatically fixes** file ownership and permissions:

```bash
# Before (❌ - permission denied)
-rw-------. 1 root    root    162 /home/user/.docker/config.json

# After (✅ - automatic fix)
-rw-------. 1 user    user    162 /home/user/.docker/config.json
```

### How It Works

1. Login tasks create config files (may be as root)
2. Permission fix tasks run **automatically after login**
3. Files get correct `user:user` ownership
4. SELinux contexts restored if enabled (RHEL/CentOS only)
5. Users can access Docker without permission errors

### Applies To

All supported distributions:
- Ubuntu 22.04+
- Debian 11+
- RHEL/CentOS/Rocky/AlmaLinux 9+

---

## Common Registries

### Docker Hub

```yaml
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"
    username: "your-dockerhub-username"
    password: "{{ vault_dockerhub_token }}"
```

**Create token:** https://hub.docker.com/settings/security

### GitHub Container Registry (GHCR)

```yaml
docker_registries_auth:
  - registry: "ghcr.io"
    username: "your-github-username"
    password: "{{ vault_github_token }}"
```

**Create token:** https://github.com/settings/tokens
- Required scope: `read:packages` (for pull)
- Additional scope: `write:packages` (for push)

### Quay.io

```yaml
docker_registries_auth:
  - registry: "quay.io"
    username: "myorg+robot"
    password: "{{ vault_quay_robot_token }}"
```

**Create robot account:** https://quay.io/organization/YOUR_ORG?tab=robots

### Azure Container Registry (ACR)

```yaml
docker_registries_auth:
  - registry: "myregistry.azurecr.io"
    username: "{{ azure_sp_app_id }}"
    password: "{{ vault_azure_sp_password }}"
```

**Tip:** Use Service Principal for automation.

### AWS ECR

```yaml
docker_registries_auth:
  - registry: "123456789.dkr.ecr.us-east-1.amazonaws.com"
    username: "AWS"
    password: "{{ ecr_auth_token }}"
```

**Note:** ECR tokens expire after 12 hours. Consider using credential helpers.

### Google Container Registry (GCR)

```yaml
docker_registries_auth:
  - registry: "gcr.io"
    username: "_json_key"
    password: "{{ vault_gcp_service_account_json }}"
```

### Harbor / Nexus / Private

```yaml
docker_registries_auth:
  - registry: "harbor.company.com"
    username: "ci-user"
    password: "{{ vault_harbor_password }}"
  
  - registry: "nexus.company.com:5000"
    username: "deployer"
    password: "{{ vault_nexus_password }}"
```

---

## Insecure Registries

For registries using HTTP or self-signed certificates:

### Configuration

```yaml
docker_insecure_registries:
  - "registry.internal.company.com:5000"
  - "192.168.1.100:5000"
  - "localhost:5000"

docker_registries_auth:
  - registry: "registry.internal.company.com:5000"
    username: "admin"
    password: "{{ vault_internal_registry_password }}"
```

### What This Does

Adds to `/etc/docker/daemon.json`:

```json
{
  "insecure-registries": [
    "registry.internal.company.com:5000",
    "192.168.1.100:5000"
  ]
}
```

### Security Warning

⚠️ **Only use for trusted internal networks!**

Insecure registries:
- Don't verify TLS certificates
- Allow HTTP (unencrypted) connections
- Are vulnerable to MITM attacks

**Recommendation:** Use proper TLS certificates in production.

---

## Complete Example

### Playbook with Multiple Registries

```yaml
---
- name: Docker with Registry Authentication
  hosts: docker_hosts
  become: true
  
  vars_files:
    - vars/registry_secrets.yml
  
  vars:
    docker_users:
      - developer
      - jenkins
    
    docker_insecure_registries:
      - "registry.internal.company.com:5000"
    
    docker_registries_auth:
      # Docker Hub
      - registry: "https://index.docker.io/v1/"
        username: "{{ dockerhub_username }}"
        password: "{{ vault_dockerhub_token }}"
      
      # GitHub Container Registry
      - registry: "ghcr.io"
        username: "{{ github_username }}"
        password: "{{ vault_github_token }}"
      
      # Internal Registry
      - registry: "registry.internal.company.com:5000"
        username: "ci-user"
        password: "{{ vault_internal_password }}"
  
  roles:
    - code3tech.devtools.docker
```

### Vault File (vars/registry_secrets.yml)

```yaml
# Encrypted with ansible-vault
vault_dockerhub_token: "dckr_pat_xxxxxxxxxxxxx"
vault_github_token: "ghp_xxxxxxxxxxxxxxxxxxxxx"
vault_internal_password: "secure_password_here"
```

---

## Troubleshooting

### Authentication Failed

```
Error response from daemon: unauthorized
```

**Causes & Solutions:**

1. **Wrong registry URL for Docker Hub:**
   ```yaml
   # ❌ Wrong
   registry: "docker.io"
   
   # ✅ Correct
   registry: "https://index.docker.io/v1/"
   ```

2. **Expired token:** Generate new token at registry provider

3. **Wrong credentials:** Verify username and password

### Permission Denied

```
permission denied while trying to connect to the Docker daemon
```

**Solution:** Ensure user is in `docker_users`:
```yaml
docker_users:
  - myuser
```

### Config File Permission Issues

```
error getting credentials - err: exit status 1, out: ``
```

**Solution:** Role handles this automatically, but manual fix:
```bash
sudo chown $USER:$USER ~/.docker/config.json
chmod 600 ~/.docker/config.json
```

### Registry Not Reachable

```
dial tcp: lookup registry.example.com: no such host
```

**Solutions:**
1. Check DNS resolution: `nslookup registry.example.com`
2. Check network connectivity: `curl -I https://registry.example.com/v2/`
3. For internal registries: Ensure proper DNS or use IP address

### Certificate Errors

```
x509: certificate signed by unknown authority
```

**Solutions:**
1. Add registry to `docker_insecure_registries` (not recommended)
2. Install CA certificate on host
3. Use proper TLS certificate on registry

---

## Best Practices

### 1. Always Use Vault

```bash
ansible-vault create vars/secrets.yml
```

### 2. Use Access Tokens, Not Passwords

| Registry | Token Type |
|----------|------------|
| Docker Hub | Personal Access Token (PAT) |
| GitHub | Personal Access Token |
| Quay.io | Robot Account Token |
| Azure | Service Principal |

### 3. Minimal Permissions

Only grant necessary scopes:
- Pull only: `read:packages`
- Push: `write:packages`
- Delete: `delete:packages`

### 4. Rotate Tokens Regularly

- Set expiration dates on tokens
- Rotate at least quarterly
- Automate rotation where possible

---

## Next Steps

- **[Daemon Configuration](05-daemon-config.md)** - Advanced daemon settings
- **[Production Deployment](06-production-deployment.md)** - Complete production playbooks
- **[Podman Registry Authentication](../podman/04-registry-auth.md)** - Podman-specific registry configuration

---

[← Back to Docker Documentation](README.md) | [Previous: Basic Installation](03-basic-installation.md) | [Next: Daemon Configuration →](05-daemon-config.md)
