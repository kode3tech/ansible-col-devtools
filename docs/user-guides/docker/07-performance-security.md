# Performance & Security

Complete guide to Docker performance optimization and security hardening.

---

## 📋 Table of Contents

- [Performance Optimization](#performance-optimization)
  - [Storage Performance](#storage-performance)
  - [Network Performance](#network-performance)
  - [Build Performance](#build-performance)
  - [Container Runtime](#container-runtime)
- [Security Best Practices](#security-best-practices)
  - [Docker Group Security](#docker-group-security)
  - [Container Security](#container-security)
  - [Image Security](#image-security)
  - [Network Security](#network-security)
- [Monitoring](#monitoring)
- [Resource Management](#resource-management)

---

## Performance Optimization

### Storage Performance

#### SSD Storage

For best performance, use SSD storage for Docker data:

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
  data-root: "/ssd/docker"  # SSD mount point
```

#### Overlay2 Driver

Always use `overlay2` - it's the most performant:

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
```

**Benefits:**
- Native kernel support
- Efficient layer caching
- Lower memory usage
- Better I/O performance

#### Storage Cleanup

Regular cleanup improves performance:

```bash
# Remove unused data
docker system prune -af --volumes

# Remove dangling images only
docker image prune -f

# Check disk usage
docker system df
```

### Network Performance

#### Disable Userland Proxy

The userland proxy adds overhead. Disable for better performance:

```yaml
docker_daemon_config:
  userland-proxy: false
  iptables: true
```

**Impact:** 10-20% better network throughput for exposed ports.

#### MTU Optimization

Set correct MTU for your network:

```yaml
docker_daemon_config:
  mtu: 1450  # For cloud environments (AWS, GCP, Azure)
  # mtu: 1500  # For bare metal
```

#### DNS Optimization

Use local DNS for faster resolution:

```yaml
docker_daemon_config:
  dns:
    - "10.0.0.2"      # Internal DNS
    - "8.8.8.8"       # Fallback
  dns-opts:
    - "ndots:1"
    - "timeout:3"
    - "attempts:2"
```

### Build Performance

#### BuildKit

BuildKit is enabled by default in this role:

```yaml
docker_buildkit_enabled: true
```

**Benefits:**
- Parallel build stages
- Better caching
- Build secrets support
- Faster builds

#### Concurrent Downloads

Increase parallelism for faster image pulls:

```yaml
docker_daemon_config:
  max-concurrent-downloads: 10  # Default: 3
  max-concurrent-uploads: 5     # Default: 5
```

#### Build Cache

Optimize build cache in Dockerfiles:

```dockerfile
# Good: Dependencies first (cached)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Then application code (changes often)
COPY . .
```

### Container Runtime

#### crun Runtime

`crun` is faster than `runc`:

```yaml
docker_daemon_config:
  default-runtime: "crun"
  runtimes:
    crun:
      path: "/usr/bin/crun"
```

**Benefits:**
- 50% faster container startup
- Lower memory footprint
- Written in C (vs Go)

**Installation (RHEL/CentOS):**
```bash
sudo dnf install crun
```

**Installation (Ubuntu/Debian):**
```bash
sudo apt install crun
```

#### Live Restore

Keep containers running during daemon upgrades:

```yaml
docker_daemon_config:
  live-restore: true
```

---

## Security Best Practices

### Docker Group Security

⚠️ **WARNING:** Users in the `docker` group have **root-equivalent privileges!**

#### Risk Explanation

```bash
# Any docker user can become root
docker run -v /:/host -it alpine chroot /host
```

#### Mitigation Strategies

1. **Limit docker group membership:**
   ```yaml
   docker_users:
     - ci-service      # Only automation accounts
     # NOT regular developers
   ```

2. **Use rootless Docker (experimental):**
   ```yaml
   docker_daemon_config:
     userns-remap: "default"
   ```

3. **Consider Podman for developers:**
   - Truly rootless
   - No daemon
   - Drop-in Docker replacement

### Container Security

#### Resource Limits

Set default limits to prevent resource abuse:

```yaml
docker_daemon_config:
  default-ulimits:
    nofile:
      Hard: 65535
      Soft: 65535
    nproc:
      Hard: 4096
      Soft: 4096
  default-shm-size: "128M"
```

#### Seccomp Profile

Use default seccomp profile:

```yaml
docker_daemon_config:
  seccomp-profile: "/etc/docker/seccomp/default.json"
```

#### No New Privileges

Prevent privilege escalation:

```yaml
docker_daemon_config:
  no-new-privileges: true
```

#### User Namespace Remapping

Isolate container users from host:

```yaml
docker_daemon_config:
  userns-remap: "default"
```

**Note:** May require permission adjustments for volumes.

### Image Security

#### Trusted Images Only

```yaml
# In container runtime, enforce signed images
docker_daemon_config:
  content-trust:
    mode: "strict"
```

#### Image Scanning

Integrate vulnerability scanning:

```bash
# Using Trivy
trivy image myimage:latest

# Using Docker Scout
docker scout cves myimage:latest
```

#### Minimal Base Images

Use minimal images to reduce attack surface:

```dockerfile
# Good: Minimal image
FROM alpine:3.19

# Better: Distroless
FROM gcr.io/distroless/static-debian12

# Best: Scratch (for Go binaries)
FROM scratch
```

### Network Security

#### Disable Inter-Container Communication

```yaml
docker_daemon_config:
  icc: false
```

**Note:** Containers must explicitly link or use networks.

#### Custom Bridge Configuration

```yaml
docker_daemon_config:
  bip: "172.17.0.1/16"
  fixed-cidr: "172.17.0.0/16"
  default-address-pools:
    - base: "172.18.0.0/16"
      size: 24
```

#### Firewall Configuration

```bash
# Allow Docker bridge
sudo ufw allow in on docker0

# Limit Docker port exposure
sudo ufw deny from any to any port 2375
sudo ufw deny from any to any port 2376
```

---

## Monitoring

### Prometheus Metrics

Enable metrics endpoint:

```yaml
docker_daemon_config:
  metrics-addr: "0.0.0.0:9323"
  experimental: true
```

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets:
        - 'docker-host-01:9323'
        - 'docker-host-02:9323'
        - 'docker-host-03:9323'
```

### Key Metrics

| Metric | Description |
|--------|-------------|
| `engine_daemon_container_states_containers` | Container count by state |
| `engine_daemon_image_actions_seconds` | Image operation latency |
| `engine_daemon_network_actions_seconds` | Network operation latency |
| `process_resident_memory_bytes` | Docker daemon memory |
| `process_cpu_seconds_total` | Docker daemon CPU |

### Grafana Dashboard

Use official Docker dashboard: **ID 1229**

```bash
# Import in Grafana
Dashboard → Import → ID: 1229
```

### cAdvisor Integration

For container-level metrics:

```yaml
# docker-compose.yml for cAdvisor
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
```

### Log Monitoring

#### JSON Logging with Labels

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "50m"
    max-file: "5"
    labels: "service,environment"
    env: "SERVICE_NAME,ENVIRONMENT"
```

#### Centralized Logging

**Fluentd:**
```yaml
docker_daemon_config:
  log-driver: "fluentd"
  log-opts:
    fluentd-address: "localhost:24224"
    fluentd-async: "true"
    tag: "docker.{{.Name}}"
```

**Syslog:**
```yaml
docker_daemon_config:
  log-driver: "syslog"
  log-opts:
    syslog-address: "udp://logserver:514"
    tag: "docker/{{.Name}}"
```

---

## Resource Management

### Memory Limits

Default container memory limits:

```yaml
# In docker run or compose
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### CPU Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
        reservations:
          cpus: '0.5'
```

### Storage Quotas

Limit container storage:

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
  storage-opts:
    - "overlay2.size=10G"  # Per container limit
```

### Cleanup Automation

Create cron job for cleanup:

```yaml
# In Ansible
- name: Create Docker cleanup cron
  ansible.builtin.cron:
    name: "Docker cleanup"
    minute: "0"
    hour: "3"
    job: "docker system prune -af --filter 'until=168h' > /dev/null 2>&1"
    user: root
```

---

## Performance Tuning Summary

### Quick Wins

| Setting | Impact | Default |
|---------|--------|---------|
| `userland-proxy: false` | +10-20% network | ✅ |
| `storage-driver: overlay2` | Best storage perf | ✅ |
| `max-concurrent-downloads: 10` | Faster pulls | ❌ |
| `live-restore: true` | Zero-downtime updates | ❌ |
| BuildKit enabled | 2-3x faster builds | ✅ |

### Production Config

```yaml
docker_daemon_config:
  # Storage
  storage-driver: "overlay2"
  data-root: "/data/docker"
  
  # Logging
  log-driver: "json-file"
  log-opts:
    max-size: "50m"
    max-file: "5"
    compress: "true"
    mode: "non-blocking"
  
  # Network
  userland-proxy: false
  iptables: true
  
  # Performance
  max-concurrent-downloads: 10
  live-restore: true
  
  # Security
  no-new-privileges: true
  default-ulimits:
    nofile:
      Hard: 65535
      Soft: 65535
  
  # Monitoring
  metrics-addr: "0.0.0.0:9323"
  experimental: true
```

---

## Security Checklist

### Essential

- [ ] Limit `docker_users` to necessary accounts
- [ ] Use Ansible Vault for registry credentials
- [ ] Enable logging with rotation
- [ ] Keep Docker updated
- [ ] Use minimal base images

### Recommended

- [ ] Enable Prometheus metrics
- [ ] Implement image scanning
- [ ] Set resource limits
- [ ] Disable `icc` if not needed
- [ ] Use networks instead of links

### Advanced

- [ ] Enable `userns-remap`
- [ ] Use custom seccomp profiles
- [ ] Implement content trust
- [ ] Use rootless Docker or Podman

---

## Next Steps

- **[Troubleshooting](08-troubleshooting.md)** - Common issues and solutions
- **[Production Deployment](06-production-deployment.md)** - Complete deployment guide

---

[← Back to Docker Documentation](README.md) | [Previous: Production Deployment](06-production-deployment.md) | [Next: Troubleshooting →](08-troubleshooting.md)
