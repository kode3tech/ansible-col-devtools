# Docker Complete Guide - Production Deployment

A comprehensive guide to installing and configuring Docker Engine with the `code3tech.devtools` Ansible collection. This guide covers everything from basic concepts to production deployment with performance optimization.

## 📋 Table of Contents

- [Overview](#overview)
  - [What is Docker?](#what-is-docker)
  - [Docker Architecture](#docker-architecture)
  - [Docker vs Podman](#docker-vs-podman)
- [Quick Start](#quick-start)
- [Installation and Basic Configuration](#installation-and-basic-configuration)
  - [Minimal Installation](#minimal-installation)
  - [Installation with Users](#installation-with-users)
- [Complete Variable Reference](#complete-variable-reference)
  - [Package Configuration](#package-configuration)
  - [User Configuration](#user-configuration)
  - [Daemon Configuration](#daemon-configuration)
  - [Registry Configuration](#registry-configuration)
  - [Authentication Configuration](#authentication-configuration)
- [Production Playbook Explained](#production-playbook-explained)
  - [Pre-Tasks: Environment Preparation](#pre-tasks-environment-preparation)
  - [Role Configuration](#role-configuration)
  - [Post-Tasks: Validation](#post-tasks-validation)
- [Performance Optimization](#performance-optimization)
  - [Storage Performance](#storage-performance)
  - [Network Performance](#network-performance)
  - [Concurrency Settings](#concurrency-settings)
  - [Logging Optimization](#logging-optimization)
  - [BuildKit](#buildkit)
- [Security Best Practices](#security-best-practices)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Troubleshooting](#troubleshooting)
- [Complete Examples](#complete-examples)

---

## Overview

### What is Docker?

Docker is a **container runtime platform** that enables you to package, distribute, and run applications in isolated environments called containers. Key characteristics:

- **Client-Server Architecture**: Docker daemon (dockerd) runs as a background service
- **OCI-Compliant**: Uses industry-standard container images
- **Ecosystem**: Largest container ecosystem with Docker Hub
- **BuildKit**: Modern build engine for faster, more efficient builds
- **Compose**: Multi-container application orchestration

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DOCKER ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────┐         ┌──────────────────────────────────────┐   │
│    │  Docker  │◄───────►│         Docker Daemon (dockerd)       │   │
│    │   CLI    │ REST    │  ┌────────────────────────────────┐  │   │
│    └──────────┘  API    │  │     Container Runtime (runc)    │  │   │
│                         │  └────────────────────────────────┘  │   │
│    ┌──────────┐         │  ┌────────────────────────────────┐  │   │
│    │  Docker  │◄───────►│  │   Image Management (containerd) │  │   │
│    │ Compose  │         │  └────────────────────────────────┘  │   │
│    └──────────┘         │  ┌────────────────────────────────┐  │   │
│                         │  │   Network & Storage Drivers     │  │   │
│                         │  └────────────────────────────────┘  │   │
│                         └──────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| **Architecture** | Client-Server (daemon) | Daemonless (fork-exec) |
| **Root Required** | Daemon runs as root | Supports rootless |
| **Security** | Daemon is attack surface | Smaller attack surface |
| **Systemd Integration** | Limited | Native |
| **Ecosystem** | Largest | Growing |
| **CLI Compatibility** | Native | Compatible with Docker |
| **Compose** | Native | podman-compose |

---

## Quick Start

### Minimal Installation (5 minutes)

```yaml
---
- name: Install Docker - Quick Start
  hosts: all
  become: true
  roles:
    - code3tech.devtools.docker
```

That's it! This will:
- Install Docker Engine, CLI, and plugins
- Configure overlay2 storage driver
- Enable BuildKit for faster builds
- Apply sensible defaults

### With User Configuration

```yaml
---
- name: Install Docker with Users
  hosts: all
  become: true
  vars:
    docker_users:
      - developer
      - jenkins
  roles:
    - code3tech.devtools.docker
```

---

## Installation and Basic Configuration

### Minimal Installation

The simplest playbook to install Docker:

```yaml
---
- name: Docker Minimal Installation
  hosts: all
  become: true
  roles:
    - code3tech.devtools.docker
```

**What this does:**
1. Installs packages: `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`
2. Configures storage: overlay2 driver with log rotation
3. Enables BuildKit for builds
4. Starts and enables Docker service

### Installation with Users

```yaml
---
- name: Docker with User Configuration
  hosts: all
  become: true
  vars:
    docker_users:
      - developer
      - deploy
      - jenkins
  roles:
    - code3tech.devtools.docker
```

**What this does:**
1. All steps from minimal installation
2. Adds specified users to `docker` group
3. Each user can now run `docker` without sudo

**⚠️ Security Warning:** Users in the `docker` group have root-equivalent privileges! Only add trusted users.

---

## Complete Variable Reference

### Package Configuration

#### `docker_edition`
**Type:** String  
**Default:** `"ce"`

**Description:** Docker edition to install.

| Value | Description |
|-------|-------------|
| `ce` | Community Edition (free, open-source) |
| `ee` | Enterprise Edition (requires license) |

```yaml
docker_edition: "ce"  # Community Edition
```

---

#### `docker_packages`
**Type:** List  
**Default:**
```yaml
docker_packages:
  - "docker-{{ docker_edition }}"
  - "docker-{{ docker_edition }}-cli"
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin
```

**Description:** Packages to install. Default includes:

| Package | Description |
|---------|-------------|
| `docker-ce` | Docker Engine |
| `docker-ce-cli` | Command-line interface |
| `containerd.io` | Container runtime |
| `docker-buildx-plugin` | Extended build capabilities |
| `docker-compose-plugin` | Multi-container orchestration |

---

### User Configuration

#### `docker_users`
**Type:** List  
**Default:** `[]`

**Description:** Users to add to the `docker` group.

```yaml
docker_users:
  - developer      # Development user
  - jenkins        # CI/CD user
  - deploy         # Deployment user
  - "{{ ansible_user }}"  # Current SSH user
```

**⚠️ Security Warning:** Docker group members have root-equivalent privileges!

---

### Daemon Configuration

#### `docker_daemon_config`
**Type:** Dictionary  
**Default:** Performance-optimized configuration

**Description:** Complete Docker daemon configuration (`/etc/docker/daemon.json`).

```yaml
docker_daemon_config:
  # ==================================================================
  # STORAGE CONFIGURATION
  # ==================================================================
  
  # Custom data directory (recommended: SSD)
  data-root: "/var/lib/docker"      # Default location
  # data-root: "/opt/docker-data"   # Custom SSD location
  
  # Storage driver (overlay2 is fastest for most systems)
  storage-driver: "overlay2"
  
  # ==================================================================
  # LOGGING CONFIGURATION
  # ==================================================================
  
  log-driver: "json-file"
  log-opts:
    max-size: "10m"      # Maximum log file size
    max-file: "3"        # Number of rotated files
    compress: "true"     # Compress rotated logs
    mode: "non-blocking" # Non-blocking log writes
  
  # ==================================================================
  # NETWORK CONFIGURATION
  # ==================================================================
  
  bridge: "docker0"
  iptables: true
  ip-forward: true
  userland-proxy: false  # CRITICAL: Better performance
  ip-masq: true
  
  # DNS Configuration
  dns:
    - "1.1.1.1"          # Cloudflare (fastest)
    - "8.8.8.8"          # Google
  
  # ==================================================================
  # CONCURRENCY SETTINGS
  # ==================================================================
  
  max-concurrent-downloads: 10   # Parallel layer downloads
  max-concurrent-uploads: 5      # Parallel layer uploads
  max-download-attempts: 5       # Retry failed downloads
  
  # ==================================================================
  # PRODUCTION SETTINGS
  # ==================================================================
  
  # Containers survive daemon restart
  live-restore: true
  
  # Init process for proper signal handling
  init: true
  
  # Graceful shutdown timeout
  shutdown-timeout: 30
  
  # Shared memory for builds
  default-shm-size: "256M"
  
  # ==================================================================
  # CGROUP CONFIGURATION
  # ==================================================================
  
  exec-opts:
    - "native.cgroupdriver=systemd"
```

**Explanation of Key Options:**

| Option | Value | Performance Impact |
|--------|-------|-------------------|
| `storage-driver: overlay2` | Best for most systems | Native, fast, copy-on-write |
| `userland-proxy: false` | Disable userland proxy | **+20-30% network performance** |
| `max-concurrent-downloads` | Parallel downloads | **+200-300% faster pulls** |
| `live-restore: true` | Survive daemon restart | Zero downtime updates |
| `mode: non-blocking` | Non-blocking logging | Prevents application blocking |

---

### Registry Configuration

#### `docker_insecure_registries`
**Type:** List  
**Default:** `[]`

**Description:** Registries that use HTTP or self-signed certificates.

```yaml
docker_insecure_registries:
  - "registry.internal.company.com:5000"
  - "192.168.1.100:5000"
  - "localhost:5000"
```

**⚠️ Security Warning:** Only use for internal/trusted networks!

**Result in `/etc/docker/daemon.json`:**
```json
{
  "insecure-registries": [
    "registry.internal.company.com:5000",
    "192.168.1.100:5000"
  ]
}
```

---

#### `docker_registry_mirrors`
**Type:** List  
**Default:** `[]`

**Description:** Mirror registries for Docker Hub.

```yaml
docker_daemon_config:
  registry-mirrors:
    - "https://mirror.gcr.io"
    - "https://docker.mirror.hashicorp.services"
```

**Benefits:**
- Faster pulls (geographically closer)
- Reduced Docker Hub rate limiting
- Better availability

---

### Authentication Configuration

#### `docker_registries_auth`
**Type:** List  
**Default:** `[]`

**Description:** Credentials for private registry authentication.

```yaml
docker_registries_auth:
  # Docker Hub (IMPORTANT: Use full URL)
  - registry: "https://index.docker.io/v1/"
    username: "myuser"
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

**Registry URL Formats:**

| Registry | URL Format |
|----------|------------|
| Docker Hub | `https://index.docker.io/v1/` (full URL required!) |
| GHCR | `ghcr.io` |
| Quay.io | `quay.io` |
| Private | `registry.example.com` or `registry.example.com:5000` |

**⚠️ ALWAYS use Ansible Vault for passwords!**

```bash
# Create encrypted vars file
ansible-vault create vars/registry_secrets.yml

# Content:
vault_dockerhub_token: "dckr_pat_xxxxx"
vault_github_token: "ghp_xxxxx"
```

---

## Production Playbook Explained

This section dissects a complete production playbook line by line.

### Pre-Tasks: Environment Preparation

#### Time Synchronization

```yaml
pre_tasks:
  # ==========================================================================
  # TIME SYNCHRONIZATION - CRITICAL FOR GPG KEY VALIDATION
  # ==========================================================================
```

**Why it's needed:**
- GPG keys have validity dates
- If system clock is wrong, package installation fails
- RHEL 10+ is especially sensitive to clock skew

```yaml
  # --- RedHat-like (RHEL, CentOS, Rocky, AlmaLinux) ---
  - name: "[TimeSync] Ensure chrony is installed (RedHat)"
    ansible.builtin.dnf:
      name: chrony
      state: present
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
    tags: timesync

  - name: "[TimeSync] Force time synchronization (RedHat)"
    ansible.builtin.command:
      cmd: chronyc makestep
    changed_when: false
    when: ansible_os_family in ['RedHat', 'Rocky', 'AlmaLinux']
```

**Explanation:**
- `chrony` is the modern NTP client for RHEL
- `chronyc makestep` forces immediate clock adjustment

```yaml
  # --- Debian-like (Debian, Ubuntu) ---
  - name: "[TimeSync] Ensure systemd-timesyncd is installed (Debian)"
    ansible.builtin.apt:
      name: systemd-timesyncd
      state: present
      update_cache: true
      cache_valid_time: 3600
    when: ansible_os_family == 'Debian'
```

**Explanation:**
- Ubuntu/Debian use `systemd-timesyncd` by default
- Lighter than chrony, sufficient for most cases

---

#### Custom Data Directory Setup

```yaml
  - name: Create custom Docker data directory
    ansible.builtin.file:
      path: /opt/docker-data
      state: directory
      mode: '0711'
      owner: root
      group: root
```

**Why custom directory:**
- Separate from OS partition
- Can be on SSD for performance
- Easier backup/management
- `mode: '0711'` allows user traverse but not listing

---

### Role Configuration

The role is invoked with comprehensive variables:

```yaml
  vars:
    # ==========================================================================
    # STORAGE & I/O PERFORMANCE
    # ==========================================================================
    docker_daemon_config:
      # Custom directory (recommended: SSD)
      data-root: "/opt/docker-data"
      
      # Storage driver
      storage-driver: "overlay2"
```

**Performance Impact:**
- `data-root` on SSD = faster image operations
- `overlay2` = most efficient copy-on-write driver

```yaml
      # ==========================================================================
      # NETWORK PERFORMANCE
      # ==========================================================================
      bridge: "docker0"
      iptables: true
      ip-forward: true
      userland-proxy: false     # CRITICAL: +20-30% network performance
      ip-masq: true
```

**Key Setting:** `userland-proxy: false`
- Removes userland proxy layer
- Direct kernel networking
- Significant performance improvement

```yaml
      # ==========================================================================
      # CONCURRENCY & DOWNLOADS
      # ==========================================================================
      max-concurrent-downloads: 25    # High parallelism
      max-concurrent-uploads: 15       # Optimized upload
      max-download-attempts: 5         # Retry on failure
```

**Effect:**
- Downloads 25 layers simultaneously
- Reduces pull time by 200-300%
- Depends on network bandwidth

```yaml
      # ==========================================================================
      # PRODUCTION RELIABILITY
      # ==========================================================================
      live-restore: true         # Containers survive daemon restart
      init: true                 # Init process for cleanup
      shutdown-timeout: 60       # Graceful shutdown
```

**Critical for Production:**
- `live-restore: true` = Zero downtime Docker updates
- `init: true` = Proper signal handling (prevents zombie processes)
- `shutdown-timeout: 60` = Applications get time to shutdown gracefully

```yaml
      # ==========================================================================
      # MONITORING & METRICS
      # ==========================================================================
      metrics-addr: "127.0.0.1:9323"
      experimental: false
```

**Prometheus Integration:**
- Metrics available at `http://127.0.0.1:9323/metrics`
- Monitor container performance
- Track resource usage

---

### Post-Tasks: Validation

#### Basic Verification

```yaml
  post_tasks:
    - name: Verify Docker is running
      ansible.builtin.command: docker info
      register: docker_info_result
```

**Purpose:** Confirm installation succeeded before proceeding.

#### Performance Test

```yaml
    - name: Quick performance test with Alpine
      ansible.builtin.command: docker run --rm alpine:latest echo "Performance test completed"
      register: perf_test
```

**Validation:**
- `--rm`: Auto-remove container after exit
- Tests full container lifecycle
- Proves Docker is fully functional

#### Metrics Verification

```yaml
    - name: Check if metrics endpoint is responding
      ansible.builtin.uri:
        url: "http://127.0.0.1:9323/metrics"
        method: GET
      register: metrics_check
      failed_when: false
```

**Purpose:** Verify Prometheus metrics are available.

---

## Performance Optimization

### Storage Performance

#### Custom Data Directory on SSD

```yaml
docker_daemon_config:
  data-root: "/opt/docker-data"
```

**Setup Steps:**
1. Create directory: `mkdir -p /opt/docker-data`
2. Optionally mount SSD: `mount /dev/sdb1 /opt/docker-data`
3. Configure in daemon.json
4. Restart Docker

**Expected Improvement:** 30-50% faster image operations

---

#### overlay2 Driver

```yaml
docker_daemon_config:
  storage-driver: "overlay2"
```

**Why overlay2:**
- Native Linux kernel support
- Most efficient copy-on-write
- Best performance for most workloads

**Requirements:**
- Kernel 4.0+ (all modern distributions)
- ext4 or xfs filesystem

---

### Network Performance

#### Disable Userland Proxy

```yaml
docker_daemon_config:
  userland-proxy: false
```

**What it does:**
- Removes userland proxy layer
- Uses kernel-level port forwarding
- Direct iptables NAT rules

**Expected Improvement:** 20-30% network throughput increase

---

#### DNS Optimization

```yaml
docker_daemon_config:
  dns:
    - "1.1.1.1"    # Cloudflare (fastest)
    - "1.0.0.1"    # Cloudflare secondary
    - "8.8.8.8"    # Google primary
    - "8.8.4.4"    # Google secondary
```

**Benefits:**
- Faster DNS resolution
- Better availability with multiple providers
- Cloudflare has lowest latency globally

---

### Concurrency Settings

#### Parallel Downloads

```yaml
docker_daemon_config:
  max-concurrent-downloads: 25
  max-concurrent-uploads: 15
  max-download-attempts: 5
```

**Tuning Guidelines:**

| Network Speed | Downloads | Uploads |
|---------------|-----------|---------|
| 1 Gbps+ | 25 | 15 |
| 100 Mbps | 10 | 5 |
| 10 Mbps | 5 | 3 |

**Expected Improvement:** 200-300% faster image pulls

---

### Logging Optimization

#### Non-Blocking Logs

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "100m"         # Larger files = less I/O
    max-file: "5"            # More rotation files
    compress: "true"         # Save disk space
    mode: "non-blocking"     # CRITICAL: Don't block app
    max-buffer-size: "16m"   # Large buffer for high throughput
```

**Key Option:** `mode: "non-blocking"`
- Prevents application blocking on log writes
- Essential for high-throughput applications
- Uses in-memory buffer (`max-buffer-size`)

---

### BuildKit

#### Enable BuildKit

```yaml
docker_buildkit_enabled: true
```

**Or via daemon.json:**

```yaml
docker_daemon_config:
  features:
    buildkit: true
```

**BuildKit Benefits:**
- 2-3x faster builds
- Parallel build stages
- Better caching
- Smaller images
- Secret management during builds

**Usage:**
```bash
# Automatic with docker_buildkit_enabled: true
docker build .

# Or explicit
DOCKER_BUILDKIT=1 docker build .
```

---

## Security Best Practices

### 1. Always Use Ansible Vault for Credentials

```bash
# Create vault
ansible-vault create vars/secrets.yml

# Run with vault
ansible-playbook playbook.yml --ask-vault-pass
```

### 2. Limit Docker Group Membership

```yaml
# Only add TRUSTED users
docker_users:
  - deploy
  - jenkins
  # NOT: developer1, developer2, etc.
```

**⚠️ Docker group = root access!**

### 3. Use Access Tokens, Not Passwords

- Docker Hub: Use Personal Access Tokens (PATs)
- GitHub: Use PATs with minimal scope (`read:packages`)
- Quay: Use Robot Accounts

### 4. Enable Live Restore

```yaml
docker_daemon_config:
  live-restore: true
```

**Security Benefit:** Containers continue running during daemon updates (security patches).

### 5. Use Content Trust

```bash
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Now images are verified
docker pull alpine:latest  # Verified!
```

---

## Monitoring and Metrics

### Prometheus Metrics

#### Enable Metrics Endpoint

```yaml
docker_daemon_config:
  metrics-addr: "127.0.0.1:9323"
```

**Available Metrics:**
- Container count
- Image count
- Memory usage
- CPU usage
- Network I/O
- Disk I/O

#### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
```

#### Key Metrics

```promql
# Running containers
engine_daemon_container_states_containers{state="running"}

# Memory usage
container_memory_usage_bytes

# CPU usage rate
rate(container_cpu_usage_seconds_total[5m])

# Network bytes received
container_network_receive_bytes_total
```

---

## Troubleshooting

### Common Error: Permission Denied

```
Got permission denied while trying to connect to the Docker daemon socket
```

**Cause:** User not in docker group.

**Solution:**
```yaml
docker_users:
  - myuser
```

Or manually:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### Common Error: Storage Driver Issues

```
Error: devicemapper: Error running deviceCreate
```

**Cause:** Wrong storage driver for filesystem.

**Solution:**
```yaml
docker_daemon_config:
  storage-driver: "overlay2"  # Best for most systems
```

---

### Common Error: DNS Resolution Failed

```
Could not resolve 'registry-1.docker.io'
```

**Cause:** DNS configuration issues.

**Solution:**
```yaml
docker_daemon_config:
  dns:
    - "1.1.1.1"
    - "8.8.8.8"
```

---

### Common Error: Registry Authentication Failed

```
Error response from daemon: unauthorized
```

**Causes & Solutions:**

1. **Wrong registry URL for Docker Hub:**
   ```yaml
   # ❌ Wrong
   - registry: "docker.io"
   
   # ✅ Correct
   - registry: "https://index.docker.io/v1/"
   ```

2. **Expired token:**
   Generate new PAT at https://hub.docker.com/settings/security

3. **Permission file issues:**
   The role automatically fixes permissions, but manual fix:
   ```bash
   sudo chown $USER:$USER ~/.docker/config.json
   ```

---

### Common Error: Disk Space

```
no space left on device
```

**Solution:**
```bash
# Clean up unused resources
docker system prune -a --volumes

# Check disk usage
docker system df
```

**Prevention:**
```yaml
docker_daemon_config:
  log-opts:
    max-size: "100m"   # Limit log size
    max-file: "5"      # Limit log files
```

---

### Common Error: Clock Skew

```
GPG error: expired key
```

**Cause:** System clock is wrong.

**Solution:** The role handles this, but manually:
```bash
# RedHat
sudo chronyc makestep

# Debian/Ubuntu
sudo timedatectl set-ntp true
```

---

## Complete Examples

### Example 1: Development Workstation

```yaml
---
- name: Docker for Developers
  hosts: workstations
  become: true
  
  vars:
    docker_users:
      - developer
    
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "10m"
        max-file: "3"
      storage-driver: "overlay2"
    
    docker_registries_auth:
      - registry: "ghcr.io"
        username: "{{ github_user }}"
        password: "{{ vault_github_token }}"
  
  roles:
    - code3tech.devtools.docker
```

### Example 2: CI/CD Pipeline Server

```yaml
---
- name: Docker for CI/CD
  hosts: ci_servers
  become: true
  
  vars:
    docker_users:
      - jenkins
      - gitlab-runner
    
    docker_daemon_config:
      data-root: "/data/docker"
      storage-driver: "overlay2"
      max-concurrent-downloads: 25
      max-concurrent-uploads: 15
      userland-proxy: false
      live-restore: true
      log-driver: "json-file"
      log-opts:
        max-size: "100m"
        max-file: "5"
        compress: "true"
        mode: "non-blocking"
    
    docker_buildkit_enabled: true
    
    docker_registries_auth:
      - registry: "https://index.docker.io/v1/"
        username: "{{ dockerhub_user }}"
        password: "{{ vault_dockerhub_token }}"
      - registry: "registry.company.com"
        username: "ci-service"
        password: "{{ vault_company_token }}"
  
  roles:
    - code3tech.devtools.docker
```

### Example 3: Production with Full Optimization

See the complete production playbook at:
[playbooks/docker/install-docker.yml](../../playbooks/docker/install-docker.yml)

---

## See Also

- [Registry Authentication Guide](REGISTRY_AUTHENTICATION.md) - Complete registry auth documentation
- [Docker Role README](../../roles/docker/README.md) - Role reference
- [Variables Reference](../reference/VARIABLES.md) - Complete variables list
- [FAQ](../FAQ.md) - Frequently asked questions

---

## External References

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Daemon Configuration](https://docs.docker.com/engine/reference/commandline/dockerd/)
- [BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Prometheus Docker Metrics](https://docs.docker.com/config/daemon/prometheus/)

---

[← Back to User Guides](README.md)

**Performance Tip:** For maximum performance, use SSD storage, enable BuildKit, and disable userland-proxy! 🚀
