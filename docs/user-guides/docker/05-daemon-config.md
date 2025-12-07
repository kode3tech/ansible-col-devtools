# Daemon Configuration

Complete guide to Docker daemon configuration with optimized settings for production environments.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Basic Configuration](#basic-configuration)
- [Storage Configuration](#storage-configuration)
- [Logging Configuration](#logging-configuration)
- [Network Configuration](#network-configuration)
- [Resource Limits](#resource-limits)
- [Complete Examples](#complete-examples)

---

## Overview

The Docker daemon is configured via the `docker_daemon_config` variable, which generates `/etc/docker/daemon.json`.

### Default Configuration

The role includes **sensible defaults** out of the box:

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

### How It Works

1. Role creates `/etc/docker/daemon.json` from configuration
2. Docker service is restarted to apply changes
3. Configuration is validated before restart

---

## Basic Configuration

### Minimal Custom Config

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

### Extended Config

```yaml
docker_daemon_config:
  # Logging
  log-driver: "json-file"
  log-opts:
    max-size: "50m"
    max-file: "5"
    compress: "true"
  
  # Storage
  storage-driver: "overlay2"
  data-root: "/var/lib/docker"
  
  # Network
  userland-proxy: false
  iptables: true
  
  # Performance
  max-concurrent-downloads: 10
  max-concurrent-uploads: 5
```

---

## Storage Configuration

### Storage Driver

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
```

**Recommended:** `overlay2` for all modern Linux systems.

### Custom Data Directory

```yaml
docker_daemon_config:
  data-root: "/data/docker"
```

**Use cases:**
- Separate partition for Docker data
- SSD storage for better performance
- More disk space available

**Important:** If changing `data-root`:
1. Stop Docker service
2. Copy existing data: `rsync -av /var/lib/docker/ /data/docker/`
3. Update configuration
4. Start Docker service

### Storage Driver Options

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
  storage-opts:
    - "overlay2.override_kernel_check=true"
```

---

## Logging Configuration

### JSON File Driver (Default)

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
```

### Production Logging

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "50m"
    max-file: "5"
    compress: "true"
    mode: "non-blocking"
    max-buffer-size: "4m"
```

**Options explained:**
| Option | Description | Recommended |
|--------|-------------|-------------|
| `max-size` | Max log file size | `10m` - `100m` |
| `max-file` | Number of log files to keep | `3` - `5` |
| `compress` | Compress rotated logs | `true` |
| `mode` | Logging mode | `non-blocking` |
| `max-buffer-size` | Buffer for non-blocking | `4m` |

### Syslog Driver

```yaml
docker_daemon_config:
  log-driver: "syslog"
  log-opts:
    syslog-address: "udp://logserver:514"
    syslog-facility: "daemon"
    tag: "docker/{{.Name}}"
```

### Fluentd Driver

```yaml
docker_daemon_config:
  log-driver: "fluentd"
  log-opts:
    fluentd-address: "localhost:24224"
    fluentd-async: "true"
    tag: "docker.{{.Name}}"
```

---

## Network Configuration

### Basic Network Settings

```yaml
docker_daemon_config:
  # Disable userland proxy for better performance
  userland-proxy: false
  
  # Enable iptables management
  iptables: true
  
  # Enable IPv6 (optional)
  ipv6: false
```

### Custom Bridge Network

```yaml
docker_daemon_config:
  bip: "172.17.0.1/16"
  fixed-cidr: "172.17.0.0/16"
  default-address-pools:
    - base: "172.18.0.0/16"
      size: 24
```

### DNS Configuration

```yaml
docker_daemon_config:
  dns:
    - "8.8.8.8"
    - "8.8.4.4"
  dns-opts:
    - "ndots:1"
    - "timeout:3"
  dns-search:
    - "company.com"
```

### MTU Configuration

```yaml
docker_daemon_config:
  mtu: 1450
```

**When to change MTU:**
- Running in cloud environments (AWS, GCP, Azure)
- VPN or overlay networks
- Network performance issues

---

## Resource Limits

### Default Container Limits

```yaml
docker_daemon_config:
  default-ulimits:
    nofile:
      Hard: 65535
      Soft: 65535
    nproc:
      Hard: 65535
      Soft: 65535
```

### Shared Memory Size

```yaml
docker_daemon_config:
  default-shm-size: "128M"
```

---

## Concurrency Settings

### Download/Upload Parallelism

```yaml
docker_daemon_config:
  max-concurrent-downloads: 10
  max-concurrent-uploads: 5
```

**Impact:**
- Higher values = faster image pulls (more bandwidth)
- Lower values = less network contention

---

## Security Settings

### Seccomp Profile

```yaml
docker_daemon_config:
  seccomp-profile: "/etc/docker/seccomp/default.json"
```

### User Namespace Remapping

```yaml
docker_daemon_config:
  userns-remap: "default"
```

**Note:** User namespace remapping provides additional isolation but may require adjustments for volume permissions.

### Live Restore

```yaml
docker_daemon_config:
  live-restore: true
```

**Benefit:** Containers continue running during Docker daemon upgrades.

---

## Metrics and Monitoring

### Enable Prometheus Metrics

```yaml
docker_daemon_config:
  metrics-addr: "0.0.0.0:9323"
  experimental: true
```

**Access:** `http://docker-host:9323/metrics`

**Prometheus scrape config:**
```yaml
scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['docker-host:9323']
```

---

## Container Runtime

### Default Runtime

```yaml
docker_daemon_config:
  default-runtime: "runc"
```

### Alternative Runtime (crun)

```yaml
docker_daemon_config:
  default-runtime: "crun"
  runtimes:
    crun:
      path: "/usr/bin/crun"
```

**Benefits of crun:**
- Faster container startup
- Lower memory footprint
- Written in C (vs Go for runc)

---

## Complete Examples

### Development Environment

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
  max-concurrent-downloads: 5
```

### Production Environment

```yaml
docker_daemon_config:
  # Logging - Production optimized
  log-driver: "json-file"
  log-opts:
    max-size: "50m"
    max-file: "5"
    compress: "true"
    mode: "non-blocking"
    max-buffer-size: "4m"
  
  # Storage - Performance optimized
  storage-driver: "overlay2"
  data-root: "/data/docker"
  
  # Network - Performance optimized
  userland-proxy: false
  iptables: true
  dns:
    - "10.0.0.2"
    - "8.8.8.8"
  
  # Concurrency
  max-concurrent-downloads: 10
  max-concurrent-uploads: 5
  
  # Reliability
  live-restore: true
  
  # Resource Limits
  default-ulimits:
    nofile:
      Hard: 65535
      Soft: 65535
  default-shm-size: "128M"
  
  # Monitoring
  metrics-addr: "0.0.0.0:9323"
  experimental: true
```

### CI/CD Environment

```yaml
docker_daemon_config:
  # Fast logging
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "2"
  
  # Performance
  storage-driver: "overlay2"
  max-concurrent-downloads: 20
  max-concurrent-uploads: 10
  
  # Network
  userland-proxy: false
  
  # Faster startup
  default-runtime: "crun"
  runtimes:
    crun:
      path: "/usr/bin/crun"
```

### High-Security Environment

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "100m"
    max-file: "10"
  
  storage-driver: "overlay2"
  
  # Security
  userns-remap: "default"
  no-new-privileges: true
  seccomp-profile: "/etc/docker/seccomp/default.json"
  
  # Network isolation
  icc: false
  userland-proxy: false
  
  # Audit logging
  log-level: "info"
```

---

## Playbook Example

### Apply Custom Daemon Config

```yaml
---
- name: Docker with Custom Daemon Configuration
  hosts: docker_hosts
  become: true
  
  vars:
    docker_users:
      - developer
    
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "50m"
        max-file: "5"
        compress: "true"
      storage-driver: "overlay2"
      data-root: "/data/docker"
      userland-proxy: false
      iptables: true
      max-concurrent-downloads: 10
      live-restore: true
  
  roles:
    - code3tech.devtools.docker
```

---

## Validation

### Check Current Configuration

```bash
docker info
docker system info --format '{{json .}}'
```

### Verify Daemon.json

```bash
sudo cat /etc/docker/daemon.json | jq
```

### Check Logging Driver

```bash
docker info --format '{{.LoggingDriver}}'
```

### Check Storage Driver

```bash
docker info --format '{{.Driver}}'
```

---

## Troubleshooting

### Invalid JSON

```
unable to configure the Docker daemon with file /etc/docker/daemon.json: 
invalid character '}' looking for beginning of object key string
```

**Solution:** Validate JSON syntax:
```bash
cat /etc/docker/daemon.json | jq
```

### Storage Driver Mismatch

```
Error starting daemon: error initializing graphdriver: 
driver not supported
```

**Solution:** Ensure kernel supports overlay2:
```bash
modprobe overlay
lsmod | grep overlay
```

### Data Directory Issues

```
Error starting daemon: unable to find data root: 
stat /data/docker: no such file or directory
```

**Solution:** Create directory with correct permissions:
```bash
sudo mkdir -p /data/docker
sudo chmod 711 /data/docker
```

---

## Next Steps

- **[Production Deployment](06-production-deployment.md)** - Complete production playbooks
- **[Performance & Security](07-performance-security.md)** - Optimization techniques

---

[← Back to Docker Documentation](README.md) | [Previous: Registry Auth](04-registry-auth.md) | [Next: Production Deployment →](06-production-deployment.md)
