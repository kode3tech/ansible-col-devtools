# Part 7: Security Best Practices

## 📋 Table of Contents

- [Token Security](#token-security)
- [Runner Isolation](#runner-isolation)
- [Network Security](#network-security)
- [Access Control](#access-control)
- [Audit and Compliance](#audit-and-compliance)
- [Security Checklist](#security-checklist)

---

## Token Security

### The Golden Rule

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      🔐 NEVER COMMIT TOKENS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ❌ WRONG:                                                              │
│   vars/gitlab.yml:                                                       │
│     gitlab_api_token: glpat-xxxxxxxxxxxxxxxxxxxx  # EXPOSED!            │
│                                                                          │
│   ✅ CORRECT:                                                            │
│   vars/vault.yml (encrypted):                                           │
│     $ANSIBLE_VAULT;1.1;AES256                                           │
│     66633...encrypted...data...                                         │
│                                                                          │
│   vars/gitlab.yml (safe):                                               │
│     gitlab_api_token: "{{ vault_gitlab_api_token }}"                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Token Scopes (Least Privilege)

| Runner Type | Minimum Required Scopes |
|-------------|-------------------------|
| **Project** | `api`, `read_api`, `create_runner` (project-level PAT) |
| **Group** | `api`, `read_api`, `create_runner` (group-level PAT) |
| **Instance** | `api` (admin token) |

**Never use:**
- ❌ `sudo` scope (unless absolutely necessary)
- ❌ Personal admin tokens for group/project runners
- ❌ Tokens with broader access than needed

### Token Rotation

```yaml
# vars/vault.yml - Rotate every 90 days
---
# Current token (expires 2025-04-15)
vault_gitlab_api_token: "glpat-current123"

# Old tokens (keep for 7 days during transition)
# vault_gitlab_api_token_old: "glpat-old456"
```

**Rotation procedure:**
1. Create new PAT with same scopes
2. Update vault.yml with new token
3. Run playbook (updates runners)
4. Verify all runners working
5. Revoke old token after 7 days

### Ansible Vault Setup

```bash
# Create vault password file (NEVER commit this!)
echo "SecureVaultPassword123!" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass

# Add to .gitignore
echo ".ansible_vault_pass" >> .gitignore
echo "*.vault" >> .gitignore

# Encrypt secrets
ansible-vault create vars/vault.yml \
  --vault-password-file ~/.ansible_vault_pass

# Edit encrypted file
ansible-vault edit vars/vault.yml \
  --vault-password-file ~/.ansible_vault_pass
```

---

## Runner Isolation

### Executor Security Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Executor Security Levels                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DOCKER EXECUTOR (✅ Recommended)                                       │
│   ─────────────────────────                                              │
│   Security: 🟢 HIGH                                                      │
│                                                                          │
│   ✅ Each job runs in isolated container                                │
│   ✅ No persistence between jobs                                        │
│   ✅ Limited host access                                                │
│   ✅ Resource limits (CPU, memory)                                      │
│   ⚠️  Privileged mode disabled by default                               │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   SHELL EXECUTOR (⚠️  Use with caution)                                  │
│   ───────────────────                                                    │
│   Security: 🟡 MEDIUM                                                    │
│                                                                          │
│   ⚠️  Jobs run directly on host                                         │
│   ⚠️  Can access host filesystem                                        │
│   ⚠️  Can install packages                                              │
│   ⚠️  Shared environment between jobs                                   │
│   ✅ Good for deployments (needs host access)                           │
│                                                                          │
│   ─────────────────────────────────────────────────────────────────     │
│                                                                          │
│   KUBERNETES EXECUTOR (✅ Enterprise)                                    │
│   ──────────────────────                                                 │
│   Security: 🟢 HIGH                                                      │
│                                                                          │
│   ✅ Each job in isolated pod                                           │
│   ✅ Network policies                                                   │
│   ✅ Resource quotas                                                    │
│   ✅ RBAC integration                                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Secure Docker Executor Configuration

```yaml
gitlab_ci_runners_runners_list:
  - name: "secure-docker-runner"
    tags: [docker, secure, linux]
    executor: "docker"
```

**Note:** Docker executor settings (image, volumes, privileged mode, resource limits, network mode) must be configured manually in `/etc/gitlab-runner/secure-docker-runner/config.toml` after runner registration.

**Example manual Docker configuration** for security hardening:

```toml
[[runners]]
  [runners.docker]
    image = "alpine:latest"
    privileged = false  # NEVER enable unless absolutely required
    disable_cache = false
    volumes = ["/etc/ssl/certs:/etc/ssl/certs:ro"]  # Read-only host mounts
    cpus = "2.0"  # Max 2 CPUs per container
    memory = "2g"  # Max 2GB RAM per container
    network_mode = "bridge"  # Isolate containers
```

### Privileged Mode Warning

```
⚠️  WARNING: docker_privileged: true

Enables FULL host access:
• Access to all devices
• Can mount host filesystem
• Can load kernel modules
• Essentially root on host

ONLY use if you MUST:
• Docker-in-Docker (DinD)
• Kubernetes-in-Docker (KinD)
• Hardware device access

NEVER use for regular builds/tests!
```

---

## Network Security

### Firewall Rules

```bash
# On runner host - RESTRICTIVE rules
# Allow outbound HTTPS to GitLab
sudo ufw allow out 443/tcp

# Allow outbound to Docker Hub (if needed)
sudo ufw allow out to registry-1.docker.io port 443 proto tcp

# DENY all other outbound by default
sudo ufw default deny outgoing

# Allow SSH for management
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Network Segmentation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Network Security Zones                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   INTERNET                                                               │
│   ────────                                                               │
│      │                                                                   │
│      ▼                                                                   │
│   ┌──────────────┐                                                      │
│   │  Firewall    │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          │ HTTPS only                                                    │
│          ▼                                                               │
│   ┌──────────────────────┐                                              │
│   │  DMZ / Runner Zone   │ ← Runners HERE (isolated)                    │
│   │                      │                                              │
│   │  • ci-runner-01      │ ✅ Can reach GitLab                          │
│   │  • ci-runner-02      │ ❌ CANNOT reach internal DB                  │
│   │  • ci-runner-03      │ ❌ CANNOT reach private APIs                 │
│   └──────┬───────────────┘                                              │
│          │                                                               │
│          │ Firewall rules                                               │
│          ▼                                                               │
│   ┌──────────────────────┐                                              │
│   │  Internal Network    │                                              │
│   │                      │                                              │
│   │  • Databases         │ ← Production resources                       │
│   │  • Internal APIs     │   (runners CANNOT access)                    │
│   │  • File servers      │                                              │
│   └──────────────────────┘                                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Proxy Configuration (Optional)

```yaml
# Runners that need proxy access
gitlab_ci_runners_runners_list:
  - name: "proxied-runner"
    tags: [docker, linux]
```

**Note:** Proxy environment variables must be configured manually in `/etc/gitlab-runner/proxied-runner/config.toml`:

```toml
[[runners]]
  environment = [
    "HTTP_PROXY=http://proxy.company.com:8080",
    "HTTPS_PROXY=http://proxy.company.com:8080",
    "NO_PROXY=localhost,127.0.0.1"
  ]
```

---

## Access Control

### Protected Branches and Runners

```yaml
# Production deployment runner
gitlab_ci_runners_runners_list:
  - name: "prod-deploy-runner"
    tags: [deploy, production]
    access_level: "ref_protected"  # ← Protected branches ONLY
    locked: true                    # ← Cannot be shared
    run_untagged: false            # ← Explicit tags required
```

**In GitLab project:**
1. Settings → Repository → Protected Branches
2. Protect `main`, `production` branches
3. Only maintainers can push
4. Only runners with `ref_protected` can deploy

### Runner Groups (Enterprise)

```
NOT available on gitlab.com
Available on GitLab Premium/Ultimate (self-hosted)

Allows:
• Group runners by function (dev, prod, deploy)
• Assign runners to specific projects
• Granular access control
```

### User Permissions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      GitLab Role Requirements                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PROJECT RUNNER                                                         │
│   ──────────────                                                         │
│   • Maintainer role in project (minimum)                                │
│   • Can create/edit/delete project runners                              │
│   • Cannot affect other projects                                        │
│                                                                          │
│   GROUP RUNNER                                                           │
│   ────────────                                                           │
│   • Owner or Maintainer role in group (minimum)                         │
│   • Can create/edit/delete group runners                                │
│   • Affects all projects in group                                       │
│                                                                          │
│   INSTANCE RUNNER                                                        │
│   ───────────────                                                        │
│   • Administrator access to GitLab instance                             │
│   • Can create/edit/delete instance runners                             │
│   • Affects entire GitLab instance                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Audit and Compliance

### Logging

```yaml
# Enable comprehensive logging
gitlab_ci_runners_list:
  - name: "audited-runner"
    tags: [docker, audited, linux]
    log_level: "info"  # Options: debug, info, warn, error
    log_format: "json"  # Structured logs for SIEM
```

**View logs:**
```bash
# Systemd journal (structured)
journalctl -u gitlab-runner-audited-runner.service -o json

# Recent errors
journalctl -u gitlab-runner-audited-runner.service -p err --since "24 hours ago"

# Follow live logs
journalctl -u gitlab-runner-audited-runner.service -f
```

### Configuration Backup

```bash
# Backup runner configurations
#!/bin/bash
BACKUP_DIR="/backup/gitlab-runners/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup all runner configs
cp -r /etc/gitlab-runner/* "$BACKUP_DIR/"

# Backup systemd services
cp /etc/systemd/system/gitlab-runner-*.service "$BACKUP_DIR/"

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.txt" <<EOF
Backup Date: $(date)
Host: $(hostname)
Runners: $(systemctl list-units --type=service | grep gitlab-runner | wc -l)
EOF

echo "✅ Backup complete: $BACKUP_DIR"
```

### Compliance Checklist

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Compliance Checklist                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   [ ] Tokens stored in Ansible Vault (encrypted)                        │
│   [ ] Vault password NOT committed to git                               │
│   [ ] Token scopes follow least privilege                               │
│   [ ] Token rotation schedule established (90 days)                     │
│   [ ] Docker executor used (not shell, unless required)                 │
│   [ ] Privileged mode disabled (docker_privileged: false)               │
│   [ ] Firewall rules configured (deny by default)                       │
│   [ ] Production runners use ref_protected                              │
│   [ ] Production runners are locked                                     │
│   [ ] Logging enabled and centralized                                   │
│   [ ] Configuration backups automated                                   │
│   [ ] Runner hosts in DMZ / isolated network                            │
│   [ ] No sensitive data in pipeline logs                                │
│   [ ] Regular security updates (OS + GitLab Runner)                     │
│   [ ] Monitoring and alerting configured                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Security Checklist

### Pre-Deployment Security Review

```yaml
# Secure production runner template
- name: "secure-prod-runner"
  description: "Production runner with security hardening"
  
  # Scope and access
  api_runner_type: "group_type"  # or project_type for highest isolation
  api_group_full_path: "production"
  
  # Tags and permissions
  tags:
    - docker
    - production
    - secure
  access_level: "ref_protected"  # ✅ Protected branches only
  locked: true                   # ✅ Cannot be shared
  run_untagged: false           # ✅ Explicit tags required
  
  # Executor configuration
  executor: "docker"             # ✅ Isolated execution
  docker_image: "alpine:latest"
  docker_privileged: false       # ✅ No host access
  
  # Resource limits
  docker_cpus: "2.0"
  docker_memory: "2g"
  
  # Performance
  concurrent: 1  # One job at a time for production
  
  # Logging
  log_level: "info"
  log_format: "json"
```

---

## Next Steps

Secure your runners, then:

- **[Part 8: Troubleshooting](08-troubleshooting.md)** - Common issues and solutions

---

[← Back to Guide Index](README.md)
