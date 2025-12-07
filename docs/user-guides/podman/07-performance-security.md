# Performance & Security

Optimization techniques and security best practices for Podman deployments.

---

## 📋 Table of Contents

- [Performance Optimization](#performance-optimization)
  - [crun Runtime](#crun-runtime)
  - [Storage Optimization](#storage-optimization)
  - [Network Performance](#network-performance)
  - [Parallel Downloads](#parallel-downloads)
- [Security Best Practices](#security-best-practices)
  - [Rootless Mode](#rootless-mode)
  - [Image Security](#image-security)
  - [Network Security](#network-security)
  - [Credential Management](#credential-management)
- [Monitoring](#monitoring)
- [Resource Management](#resource-management)

---

## Performance Optimization

### crun Runtime

The role uses `crun` by default for better performance.

#### crun vs runc Comparison

| Aspect | runc | crun |
|--------|------|------|
| **Language** | Go | C |
| **Startup Time** | Baseline | 20-30% faster |
| **Memory Usage** | Higher | 30-50% lower |
| **Compatibility** | Maximum | Very high |
| **Maintenance** | Docker/Kubernetes | Red Hat |

#### Configuration

```yaml
podman_storage_conf:
  engine:
    runtime: "crun"
```

#### Verify Runtime

```bash
podman info | grep -i runtime
# Expected: crun
```

#### When to Use crun

- ✅ High-density workloads (many containers)
- ✅ Serverless/FaaS (fast startup matters)
- ✅ Memory-constrained environments
- ✅ LXC containers (better compatibility)
- ✅ Default recommendation

#### When to Use runc

- Only if specific compatibility issues arise
- Some edge cases with older kernel features

---

### Storage Optimization

#### metacopy=on

This is the most impactful performance setting:

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    options:
      overlay:
        mountopt: "nodev,metacopy=on"
```

**What it does:**
- Copies only file metadata, not actual data
- Data is referenced from lower layer
- **30-50% I/O reduction**

**Requirements:**
- Kernel 4.19+ (Ubuntu 20.04+, RHEL 9+)
- ext4 or xfs filesystem
- overlay driver

#### SSD Storage

Use SSD for better performance:

```yaml
podman_storage_conf:
  storage:
    graphroot: "/ssd/podman/storage"
```

**Recommendations:**
- Dedicate SSD for container storage
- Use separate partition from OS
- Monitor disk usage

#### Storage Cleanup

Regular cleanup improves performance:

```bash
# Remove unused data
podman system prune -af

# Remove only unused images
podman image prune -a

# Check disk usage
podman system df
```

---

### Network Performance

#### slirp4netns Optimization

For rootless mode, slirp4netns handles networking:

```yaml
# Configuration in containers.conf
[network]
default_rootless_network_cmd = "slirp4netns"
```

**Performance Tips:**
- Use pasta for newer kernels (faster than slirp4netns)
- Consider host networking for maximum performance
- Use port ranges instead of individual ports

#### Host Networking (Maximum Performance)

```bash
# Use host network (no NAT overhead)
podman run --network=host nginx
```

⚠️ **Security tradeoff:** Container shares host network namespace.

---

### Parallel Downloads

Increase concurrent image layer downloads:

```yaml
podman_storage_conf:
  engine:
    image_parallel_copies: 10
```

**Tuning Guide:**

| Network Speed | Recommended Value |
|---------------|-------------------|
| 1 Gbps+ | 20 |
| 100 Mbps | 10 |
| 10 Mbps | 5 |
| Slow/metered | 3 |

**Impact:**
- **200-300% faster** image pulls on fast networks

---

### Complete Performance Configuration

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    graphroot: "/data/podman/storage"  # SSD mount
    runroot: "/run/containers/storage"  # tmpfs
    options:
      overlay:
        mountopt: "nodev,metacopy=on"  # +30-50% I/O
  
  engine:
    runtime: "crun"                     # +20-30% startup
    events_logger: "file"               # Lower overhead
    cgroup_manager: "systemd"           # Better integration
    num_locks: 2048                     # Support many containers
    image_parallel_copies: 10           # Fast pulls
```

---

## Security Best Practices

### Rootless Mode

**The #1 security recommendation: Use rootless mode!**

```yaml
podman_enable_rootless: true
podman_rootless_users:
  - developer
  - jenkins
```

#### Benefits

- No root daemon
- User namespace isolation
- Per-user container separation
- Reduced attack surface

#### Comparison

| Risk | Root Mode | Rootless Mode |
|------|-----------|---------------|
| Container escape | Full root | User only |
| Daemon compromise | Full system | User only |
| Privilege escalation | Possible | Mitigated |
| Multi-tenant safety | Low | High |

---

### Image Security

#### Use Trusted Registries

```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io       # Official Docker Hub
    - quay.io         # Red Hat Quay (verified)
    - ghcr.io         # GitHub verified
    # Avoid unknown registries
```

#### Image Scanning

Scan images for vulnerabilities:

```bash
# Using Trivy
trivy image myimage:latest

# Using Podman's built-in
podman image inspect myimage:latest
```

#### Minimal Base Images

```dockerfile
# Good: Minimal image
FROM alpine:3.19

# Better: Distroless
FROM gcr.io/distroless/static-debian12

# Best for compiled binaries
FROM scratch
```

#### Verify Image Signatures

```bash
# Check signature
podman image trust show docker.io/library/alpine

# Pull with verification
podman pull --tls-verify docker.io/library/alpine
```

---

### Network Security

#### Limit Registry Access

Only allow trusted registries:

```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io
    # Don't add untrusted registries
```

#### Avoid Insecure Registries

Only for internal networks:

```yaml
# ONLY for trusted internal networks
podman_insecure_registries:
  - "internal-registry.company.local:5000"
```

⚠️ **Never** use insecure registries for external traffic.

#### Network Isolation

```bash
# Isolated network
podman network create --internal isolated-net

# Run container in isolated network
podman run --network=isolated-net myapp
```

---

### Credential Management

#### Always Use Ansible Vault

```bash
# Create encrypted secrets
ansible-vault create vars/secrets.yml
```

#### Use Access Tokens

| Registry | Token Type | Expiration |
|----------|------------|------------|
| Docker Hub | PAT | Optional |
| GitHub | PAT | Recommended |
| Quay | Robot Account | Never |
| Azure | Service Principal | Configurable |

#### Minimal Permissions

Only grant necessary scopes:
- **Pull only:** `read:packages`
- **Push:** `write:packages`
- **Admin:** Avoid unless necessary

#### Rotate Credentials

```yaml
# When rotating
podman_clean_credentials: true
```

#### Monitor Access

Regularly audit registry access:
- Check login history
- Review token usage
- Revoke unused tokens

---

## Monitoring

### Health Check Script

```bash
#!/bin/bash
echo "=== Podman Health Check ==="

echo -e "\n1. Version:"
podman --version

echo -e "\n2. Runtime:"
podman info --format '{{.Host.OCIRuntime.Name}}'

echo -e "\n3. Storage:"
podman info --format '{{.Store.GraphDriverName}}'

echo -e "\n4. Containers:"
podman ps -a --format "table {{.Names}}\t{{.Status}}"

echo -e "\n5. Disk Usage:"
podman system df
```

### Container Metrics

```bash
# Real-time stats
podman stats

# Single snapshot
podman stats --no-stream
```

### System Events

```bash
# Watch events
podman events

# Filter by type
podman events --filter event=start
```

### Logging

#### Event Logger

```yaml
podman_storage_conf:
  engine:
    events_logger: "file"  # or "journald"
```

- `file`: Lower overhead, stored in container storage
- `journald`: Centralized, uses systemd journal

#### Container Logs

```bash
# View logs
podman logs mycontainer

# Follow logs
podman logs -f mycontainer

# With timestamps
podman logs -t mycontainer
```

---

## Resource Management

### Container Limits

```bash
# Memory limit
podman run --memory=512m nginx

# CPU limit
podman run --cpus=2 nginx

# Combined
podman run --memory=512m --cpus=2 nginx
```

### User Storage Quotas

For rootless users, consider disk quotas:

```bash
# Set user quota (requires quota system)
setquota -u developer 10G 15G 0 0 /home
```

### Cleanup Automation

```yaml
# Ansible task for scheduled cleanup
- name: Schedule Podman cleanup
  ansible.builtin.cron:
    name: "Podman cleanup"
    minute: "0"
    hour: "3"
    job: "podman system prune -af --filter 'until=168h' > /dev/null 2>&1"
    user: "{{ item }}"
  loop: "{{ podman_rootless_users }}"
```

---

## Performance Summary

### Quick Wins

| Setting | Impact | Enabled by Default |
|---------|--------|-------------------|
| `runtime: crun` | +20-30% startup | ✅ Yes |
| `metacopy=on` | +30-50% I/O | ✅ Yes |
| `image_parallel_copies: 10` | +200-300% pull speed | ✅ Yes |
| SSD graphroot | Significant I/O improvement | ❌ Configure manually |
| Rootless mode | Better security | ✅ Yes |

### Recommended Production Config

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    graphroot: "/data/podman/storage"
    runroot: "/run/containers/storage"
    options:
      overlay:
        mountopt: "nodev,metacopy=on"
  
  engine:
    runtime: "crun"
    events_logger: "file"
    cgroup_manager: "systemd"
    num_locks: 2048
    image_parallel_copies: 10
```

---

## Security Checklist

### Essential

- [ ] Use rootless mode
- [ ] Encrypt credentials with Vault
- [ ] Use access tokens (not passwords)
- [ ] Only trusted registries
- [ ] Keep Podman updated

### Recommended

- [ ] Enable image scanning
- [ ] Set resource limits
- [ ] Use minimal base images
- [ ] Regular credential rotation
- [ ] Monitor container activity

### Advanced

- [ ] SELinux/AppArmor enabled
- [ ] Image signature verification
- [ ] Network isolation
- [ ] User storage quotas
- [ ] Automated cleanup

---

## Next Steps

- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions
- **[Production Deployment](06-production-deployment.md)** - Complete deployment guide

---

[← Back to Podman Documentation](README.md) | [Previous: Production Deployment](06-production-deployment.md) | [Next: Troubleshooting →](08-troubleshooting.md)
