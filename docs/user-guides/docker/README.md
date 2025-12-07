# Docker Complete Guide

Comprehensive documentation for deploying and managing Docker Engine with the `code3tech.devtools` Ansible collection.

---

## 📚 Documentation Index

| Part | Document | Description |
|------|----------|-------------|
| 1 | [Introduction](01-introduction.md) | Docker concepts, architecture, Docker vs Podman |
| 2 | [Prerequisites](02-prerequisites.md) | System requirements, Ansible setup, vault configuration |
| 3 | [Basic Installation](03-basic-installation.md) | Minimal installation, user configuration, verification |
| 4 | [Registry Authentication](04-registry-auth.md) | Private registries, Docker Hub, GHCR, permission fixes |
| 5 | [Daemon Configuration](05-daemon-config.md) | Complete daemon.json configuration, storage, network |
| 6 | [Production Deployment](06-production-deployment.md) | Complete production playbook with pre/post tasks |
| 7 | [Performance & Security](07-performance-security.md) | Optimization, BuildKit, security best practices |
| 8 | [Troubleshooting](08-troubleshooting.md) | Common errors, diagnostics, FAQ |

---

## 🚀 Quick Start

### Minimal Installation (5 minutes)

```yaml
---
- name: Install Docker
  hosts: all
  become: true
  roles:
    - code3tech.devtools.docker
```

This will:
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

## ✨ Key Features

- 🎯 **Simple & Clean** - Focused only on Docker installation and configuration
- 🚀 **Fast Installation** - Optimized for quick deployment
- 🔐 **Registry Authentication** - Built-in support with automatic permission handling
- 🏗️ **Multi-Platform** - Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
- ⚡ **Performance Optimized** - BuildKit, overlay2, userland-proxy disabled
- 📊 **Production Ready** - Prometheus metrics, live-restore, graceful shutdown

---

## 📖 Learning Paths

### New to Docker?

1. Start with [Introduction](01-introduction.md) to understand Docker concepts
2. Follow [Prerequisites](02-prerequisites.md) to set up your environment
3. Complete [Basic Installation](03-basic-installation.md) for your first deployment

### Setting up CI/CD?

1. Read [Registry Authentication](04-registry-auth.md) for private registry access
2. Study [Production Deployment](06-production-deployment.md) for complete playbooks
3. Apply [Performance & Security](07-performance-security.md) optimizations

### Troubleshooting?

Jump directly to [Troubleshooting](08-troubleshooting.md) for common issues and solutions.

---

## 🔗 Quick Reference

### Essential Variables

```yaml
# Users to add to docker group
docker_users:
  - developer
  - jenkins

# Docker daemon configuration
docker_daemon_config:
  storage-driver: "overlay2"
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"

# Registry authentication
docker_registries_auth:
  - registry: "ghcr.io"
    username: "myuser"
    password: "{{ vault_github_token }}"
```

### Supported Distributions

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/Rocky/Alma** | 9, 10 |

---

## 📚 Additional Resources

- **[Role README](../../../roles/docker/README.md)** - Quick reference
- **[Example Playbooks](../../../playbooks/docker/)** - Production examples
- **[Variables Reference](../../reference/VARIABLES.md)** - All collection variables
- **[FAQ](../../FAQ.md)** - Frequently asked questions

---

## 🎥 Video Tutorial Structure

This documentation is organized in 8 parts, ideal for video tutorials:

| Video | Duration | Topic |
|-------|----------|-------|
| 1 | 5-10 min | Introduction & Architecture |
| 2 | 5 min | Prerequisites & Setup |
| 3 | 10 min | Basic Installation |
| 4 | 15 min | Registry Authentication |
| 5 | 15 min | Daemon Configuration |
| 6 | 20 min | Production Deployment |
| 7 | 15 min | Performance & Security |
| 8 | 10 min | Troubleshooting |

---

[← Back to User Guides](../README.md)
