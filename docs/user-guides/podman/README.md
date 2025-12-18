# Podman Documentation

Complete documentation for the Podman role with rootless container support.

---

## 📚 Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Introduction](01-introduction.md) | Podman concepts, architecture, comparison with Docker |
| 2 | [Prerequisites](02-prerequisites.md) | System requirements, collection installation |
| 3 | [Basic Installation](03-basic-installation.md) | Minimal installation, default configuration |
| 4 | [Registry Authentication](04-registry-auth.md) | Private registries, authentication per user |
| 5 | [Rootless Configuration](05-rootless-config.md) | Rootless mode, subuid/subgid, XDG_RUNTIME_DIR |
| 6 | [Production Deployment](06-production-deployment.md) | Complete playbooks, pre/post tasks |
| 7 | [Performance & Security](07-performance-security.md) | crun runtime, storage optimization, security |
| 8 | [Troubleshooting](08-troubleshooting.md) | Common errors, diagnostics, FAQ |
| ⚠️ | [Upgrade Guide v1.0→v1.1](upgrade-v1.0-to-v1.1.md) | **Breaking changes** - Configuration separation and storage reset |

---

## 🚀 Quick Start

### 5-Minute Installation

```yaml
---
- name: Install Podman
  hosts: all
  become: true
  roles:
    - code3tech.devtools.podman
```

### With Rootless Users

```yaml
---
- name: Install Podman with Rootless Users
  hosts: all
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
      - jenkins
  roles:
    - code3tech.devtools.podman
```

### With Registry Authentication

```yaml
---
- name: Install Podman with Registry Auth
  hosts: all
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
    podman_registries_auth:
      - registry: "docker.io"
        username: "myuser"
        password: "{{ vault_dockerhub_token }}"
  roles:
    - code3tech.devtools.podman
```

---

## 🎯 Learning Paths

### New to Podman

1. [Introduction](01-introduction.md) - Understand Podman concepts
2. [Prerequisites](02-prerequisites.md) - Prepare your environment
3. [Basic Installation](03-basic-installation.md) - First installation
4. [Rootless Configuration](05-rootless-config.md) - Configure rootless mode

### Production Deployment

1. [Prerequisites](02-prerequisites.md) - System requirements
2. [Registry Authentication](04-registry-auth.md) - Configure private registries
3. [Performance & Security](07-performance-security.md) - Optimization
4. [Production Deployment](06-production-deployment.md) - Complete playbook

### Migrating from Docker

1. [Introduction](01-introduction.md) - Docker vs Podman comparison
2. [Basic Installation](03-basic-installation.md) - Install Podman
3. [Registry Authentication](04-registry-auth.md) - Same registries, different tool
4. [Troubleshooting](08-troubleshooting.md) - Migration issues

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Daemonless** | No background service required |
| **Rootless** | Run containers as non-root user |
| **OCI-Compliant** | Same images as Docker |
| **Docker Compatible** | `alias docker=podman` works |
| **Multi-User** | Isolated containers per user |
| **Buildah Included** | Build OCI images |
| **Skopeo Included** | Copy/inspect images |
| **crun Runtime** | 20-30% faster than runc |

---

## 📋 Supported Platforms

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/Rocky/Alma** | 9, 10 |

---

## 🔗 Quick Links

- [Role README](../../../roles/podman/README.md) - Complete variable reference
- [Example Playbooks](../../../playbooks/podman/)
- [FAQ](../../FAQ.md)

---

## 📖 Related Documentation

- **[Docker Documentation](../docker/)** - For Docker Engine installation
- **[asdf Documentation](../asdf/)** - For version manager setup
- **[Azure DevOps Agents](../azure-devops-agents/)** - CI/CD agent deployment
- **[GitHub Actions Runners](../github-actions-runners/)** - Self-hosted runners

---

[← Back to User Guides](../README.md)
