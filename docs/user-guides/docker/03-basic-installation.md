# Basic Installation

Step-by-step guide to your first Docker deployment using the code3tech.devtools Ansible collection.

---

## 📋 Table of Contents

- [Minimal Installation](#minimal-installation)
- [Installation with Users](#installation-with-users)
- [What Gets Installed](#what-gets-installed)
- [Verification Steps](#verification-steps)
- [Default Configuration](#default-configuration)

---

## Minimal Installation

The simplest playbook to install Docker on your servers:

### Create the Playbook

Create `install-docker-minimal.yml`:

```yaml
---
- name: Docker Minimal Installation
  hosts: all
  become: true
  
  roles:
    - code3tech.devtools.docker
```

### Run the Playbook

```bash
# Run with inventory
ansible-playbook install-docker-minimal.yml -i inventory.ini

# With verbose output
ansible-playbook install-docker-minimal.yml -i inventory.ini -v
```

### What This Does

The minimal installation performs these steps:

1. **Configures Docker repository** - Adds official Docker apt/dnf repository
2. **Installs packages** - docker-ce, docker-ce-cli, containerd.io, plugins
3. **Configures daemon** - overlay2 storage, log rotation
4. **Enables BuildKit** - Modern build engine
5. **Starts Docker service** - systemd enabled and started

### Expected Output

```
TASK [code3tech.devtools.docker : Install Docker packages] ********************
changed: [server1]

TASK [code3tech.devtools.docker : Configure Docker daemon] ********************
changed: [server1]

TASK [code3tech.devtools.docker : Start Docker service] ***********************
changed: [server1]

PLAY RECAP *********************************************************************
server1 : ok=12  changed=6  unreachable=0  failed=0  skipped=3  rescued=0  ignored=0
```

---

## Installation with Users

Add users to the Docker group for passwordless access:

### Playbook with Users

Create `install-docker-with-users.yml`:

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

### What This Does

Beyond the minimal installation, this also:

1. **Adds users to docker group** - Each user can run `docker` without sudo
2. **Handles permissions** - No permission denied errors

### Security Warning

**⚠️ Docker group = root-equivalent access!**

Users in the `docker` group can:
- Mount any file from the host
- Run containers with `--privileged`
- Escalate to root privileges

**Only add trusted users to this group!**

### Run and Verify

```bash
# Run the playbook
ansible-playbook install-docker-with-users.yml -i inventory.ini

# SSH to server
ssh server1

# Verify as a configured user
su - developer
docker run hello-world
```

---

## What Gets Installed

### Packages

| Package | Description | Version |
|---------|-------------|---------|
| `docker-ce` | Docker Engine | Latest stable |
| `docker-ce-cli` | Command-line interface | Latest stable |
| `containerd.io` | Container runtime | Latest stable |
| `docker-buildx-plugin` | Extended build capabilities | Latest stable |
| `docker-compose-plugin` | Multi-container orchestration | Latest stable |

### Systemd Services

```
● docker.service - Docker Application Container Engine
     Loaded: loaded (/lib/systemd/system/docker.service; enabled)
     Active: active (running)
   
● containerd.service - containerd container runtime
     Loaded: loaded (/lib/systemd/system/containerd.service; enabled)
     Active: active (running)
```

### Configuration Files

| File | Purpose |
|------|---------|
| `/etc/docker/daemon.json` | Docker daemon configuration |
| `/etc/profile.d/docker-buildkit.sh` | BuildKit environment (if enabled) |

### Directory Structure

```
/var/lib/docker/           # Default data directory
├── containers/            # Container data
├── image/                 # Image storage
├── network/               # Network configuration
├── overlay2/              # Storage driver layers
├── plugins/               # Plugin data
├── tmp/                   # Temporary files
└── volumes/               # Volume data
```

---

## Verification Steps

After installation, verify everything works:

### 1. Check Docker Version

```bash
docker --version
# Expected: Docker version 27.x.x, build xxxxxxx

docker version
# Shows client and server versions
```

### 2. Check Docker Info

```bash
docker info
# Shows detailed configuration including:
# - Server Version
# - Storage Driver
# - Cgroup Driver
# - Plugins
```

### 3. Test Container Execution

```bash
# Quick test
docker run --rm hello-world

# Performance test
docker run --rm alpine:latest echo "Docker is working!"
```

### 4. Verify User Access (if configured)

```bash
# As a configured user (without sudo)
docker ps
# Should work without permission errors

# Check group membership
groups
# Should include: docker
```

### 5. Check Service Status

```bash
# Docker service
systemctl status docker

# Containerd service
systemctl status containerd
```

### 6. Verify BuildKit

```bash
# Check BuildKit environment
echo $DOCKER_BUILDKIT
# Expected: 1

# Or test build
echo "FROM alpine" | docker build -
```

---

## Default Configuration

### Daemon Configuration

The role applies sensible defaults:

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

This creates `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
```

### Default Values Explained

| Setting | Value | Purpose |
|---------|-------|---------|
| `log-driver: json-file` | JSON format | Standard Docker logging |
| `log-opts.max-size: 10m` | 10 MB | Prevents log files from growing too large |
| `log-opts.max-file: 3` | 3 files | Rotates logs, keeps 3 files |
| `storage-driver: overlay2` | overlay2 | Best performance for modern kernels |

### BuildKit Configuration

```yaml
docker_buildkit_enabled: true  # Default
```

Creates `/etc/profile.d/docker-buildkit.sh`:

```bash
export DOCKER_BUILDKIT=1
```

### Service Configuration

```yaml
docker_service_enabled: true   # Start on boot
docker_service_state: started  # Currently running
```

---

## Common Variations

### With Custom Log Settings

```yaml
vars:
  docker_daemon_config:
    log-driver: "json-file"
    log-opts:
      max-size: "50m"    # Larger logs
      max-file: "5"      # More rotation
      compress: "true"   # Compress old logs
    storage-driver: "overlay2"
```

### With Custom Data Directory

```yaml
vars:
  docker_daemon_config:
    data-root: "/data/docker"  # SSD mount point
    storage-driver: "overlay2"
    log-driver: "json-file"
    log-opts:
      max-size: "10m"
      max-file: "3"
```

### With Insecure Registry

```yaml
vars:
  docker_insecure_registries:
    - "registry.internal.company.com:5000"
```

---

## Troubleshooting Installation

### Permission Denied

```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:** Add user to docker group:
```yaml
docker_users:
  - myuser
```

Or manually:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Service Failed to Start

Check logs:
```bash
journalctl -u docker.service --no-pager -n 50
```

Common causes:
- Invalid daemon.json syntax
- Conflicting configuration
- Storage driver issues

### Repository Not Found

If package installation fails:
```bash
# Check if repository was added
cat /etc/apt/sources.list.d/docker.list  # Debian/Ubuntu
cat /etc/yum.repos.d/docker-ce.repo      # RHEL-based
```

---

## Next Steps

- **[Registry Authentication](04-registry-auth.md)** - Configure private registry access
- **[Daemon Configuration](05-daemon-config.md)** - Advanced daemon settings
- **[Production Deployment](06-production-deployment.md)** - Complete production playbooks

---

[← Back to Docker Documentation](README.md) | [Previous: Prerequisites](02-prerequisites.md) | [Next: Registry Authentication →](04-registry-auth.md)
