# Introduction to Podman

Understanding Podman architecture, concepts, and how it compares to Docker.

---

## 📋 Table of Contents

- [What is Podman?](#what-is-podman)
- [Podman vs Docker](#podman-vs-docker)
- [Architecture](#architecture)
- [Root vs Rootless Mode](#root-vs-rootless-mode)
- [Included Tools](#included-tools)
- [When to Use Podman](#when-to-use-podman)

---

## What is Podman?

Podman is a **daemonless container engine** developed by Red Hat as an alternative to Docker.

### Key Characteristics

- **No Daemon Required**: Unlike Docker, no background service running as root
- **OCI-Compliant**: Uses same container images and registries as Docker
- **CLI Compatible**: Most Docker commands work with Podman
- **Rootless by Design**: Built for rootless container execution
- **Pod Support**: Native Kubernetes-style pods

### The Name

**Pod** + **Man**(ager) = **Podman**

---

## Podman vs Docker

| Feature | Docker | Podman |
|---------|--------|--------|
| **Architecture** | Client-Server (daemon) | Daemonless (fork-exec) |
| **Root Required** | Yes (daemon runs as root) | No (supports rootless) |
| **Security** | Daemon is attack surface | Smaller attack surface |
| **Systemd Integration** | Limited | Native |
| **Pod Support** | Through Compose | Native pods |
| **CLI Compatibility** | - | Compatible with Docker CLI |
| **Image Format** | OCI/Docker | OCI/Docker |
| **Default Runtime** | runc | crun (faster) |

### Compatibility

Most Docker commands work unchanged:

```bash
# Docker
docker run -d nginx
docker build -t myapp .
docker push myregistry/myapp

# Podman (identical commands)
podman run -d nginx
podman build -t myapp .
podman push myregistry/myapp

# Or use an alias
alias docker=podman
```

---

## Architecture

### Docker Architecture (Client-Server)

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────┐        ┌─────────────────────────┐    │
│   │   Docker    │        │     Docker Daemon       │    │
│   │   Client    │───────▶│     (dockerd)           │    │
│   │             │  API   │                         │    │
│   └─────────────┘        │  ┌─────────┐            │    │
│                          │  │ containerd           │    │
│                          │  │  ┌─────────────┐     │    │
│                          │  │  │    runc     │     │    │
│                          │  │  │ (containers)│     │    │
│                          │  │  └─────────────┘     │    │
│                          │  └─────────┘            │    │
│                          └─────────────────────────┘    │
│                                  │                      │
│                                  ▼                      │
│                          Runs as ROOT                   │
└─────────────────────────────────────────────────────────┘
```

### Podman Architecture (Daemonless)

```
┌─────────────────────────────────────────────────────────┐
│                     Podman Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │               Podman CLI                         │   │
│   │                                                  │   │
│   │  ┌───────────────┐    ┌───────────────┐         │   │
│   │  │   conmon      │    │   conmon      │         │   │
│   │  │  (monitor)    │    │  (monitor)    │         │   │
│   │  │      │        │    │      │        │         │   │
│   │  │  ┌───────┐    │    │  ┌───────┐    │         │   │
│   │  │  │ crun  │    │    │  │ crun  │    │         │   │
│   │  │  │(cont1)│    │    │  │(cont2)│    │         │   │
│   │  │  └───────┘    │    │  └───────┘    │         │   │
│   │  └───────────────┘    └───────────────┘         │   │
│   └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│              Runs as USER (rootless)                    │
│                   OR as ROOT                            │
└─────────────────────────────────────────────────────────┘
```

### Key Differences

| Aspect | Docker | Podman |
|--------|--------|--------|
| **Process Model** | Daemon + Client | Direct fork-exec |
| **Single Point of Failure** | Yes (daemon) | No |
| **Resource Usage** | Higher (daemon always running) | Lower |
| **Startup Speed** | Fast (daemon ready) | Slightly slower (no daemon) |
| **Security** | Daemon runs as root | Each container isolated |

---

## Root vs Rootless Mode

This is the **most important concept** for Podman:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PODMAN EXECUTION MODES                        │
├─────────────────────────────────┬───────────────────────────────────┤
│         ROOT MODE               │         ROOTLESS MODE              │
├─────────────────────────────────┼───────────────────────────────────┤
│ • Runs as root user             │ • Runs as regular user             │
│ • Full system access            │ • Limited to user's permissions    │
│ • System-wide containers        │ • Per-user containers              │
│ • Can bind to ports < 1024      │ • Ports < 1024 need workaround     │
│ • Shared storage                │ • Isolated storage per user        │
│ • Higher performance            │ • Slightly lower performance       │
│ • Traditional Docker-like       │ • More secure                      │
├─────────────────────────────────┼───────────────────────────────────┤
│ USE WHEN:                       │ USE WHEN:                          │
│ • System services               │ • Developer workstations           │
│ • CI/CD pipelines (controlled)  │ • Multi-tenant environments        │
│ • Maximum performance needed    │ • Security is priority             │
│ • Legacy Docker workflows       │ • Kubernetes/OpenShift migration   │
└─────────────────────────────────┴───────────────────────────────────┘
```

### Mode Comparison

| Aspect | Root Mode | Rootless Mode |
|--------|-----------|---------------|
| **Storage Location** | `/var/lib/containers/storage` | `~/.local/share/containers/storage` |
| **Auth File** | `/root/.config/containers/auth.json` | `~/.config/containers/auth.json` |
| **Runtime Dir** | `/run/containers/storage` | `/run/user/<UID>/containers` |
| **Network** | Full access (iptables) | slirp4netns (user-space) |
| **Privileged Ports** | Yes (< 1024) | No (without workaround) |
| **Performance** | Higher | Slightly lower |
| **Security** | Lower (root access) | Higher (user namespace isolation) |

---

## Included Tools

The Podman role installs a complete container toolchain:

### Podman

Main container engine for running containers.

```bash
podman run -d -p 8080:80 nginx
podman ps
podman logs mycontainer
podman stop mycontainer
```

### Buildah

Build OCI container images without a daemon.

```bash
buildah from alpine
buildah run alpine-working-container apk add nginx
buildah commit alpine-working-container mynginx
```

### Skopeo

Copy and inspect container images.

```bash
# Copy between registries
skopeo copy docker://docker.io/alpine docker://myregistry.com/alpine

# Inspect image
skopeo inspect docker://docker.io/alpine

# Sync repositories
skopeo sync --src docker --dest docker docker.io/library/alpine myregistry.com/alpine
```

### crun

High-performance OCI runtime (20-30% faster than runc).

```bash
# Verify crun is being used
podman info | grep -i runtime
```

---

## When to Use Podman

### ✅ Use Podman When

- **Security is priority**: Rootless mode provides better isolation
- **Multi-user environments**: Each user has isolated containers
- **Migrating to Kubernetes**: Similar security model
- **No daemon preferred**: Less resource usage, no single point of failure
- **Red Hat ecosystem**: Native integration with RHEL, OpenShift
- **Developer workstations**: Safer for daily development

### ✅ Use Docker When

- **Existing Docker workflows**: Mature ecosystem, more documentation
- **Docker Compose heavy usage**: Better Compose support (though podman-compose exists)
- **Third-party integrations**: Some tools only support Docker
- **Maximum compatibility**: Slightly more compatible with older images

### 🔄 Hybrid Approach

Many organizations use both:

```yaml
# CI/CD servers: Docker (performance, compatibility)
# Developer machines: Podman (security, isolation)
# Production Kubernetes: Either (OCI images work with both)
```

---

## Example: Docker to Podman Migration

### Before (Docker)

```bash
# Running as root (Docker daemon)
sudo docker run -d nginx
sudo docker build -t myapp .
sudo docker push myregistry/myapp
```

### After (Podman - Rootless)

```bash
# Running as regular user (no sudo)
podman run -d nginx
podman build -t myapp .
podman push myregistry/myapp
```

### Alias for Compatibility

```bash
# Add to ~/.bashrc or ~/.zshrc
alias docker=podman

# Now Docker commands work
docker run -d nginx  # Actually runs podman
```

---

## Next Steps

- **[Prerequisites](02-prerequisites.md)** - System requirements
- **[Basic Installation](03-basic-installation.md)** - First installation
- **[Rootless Configuration](05-rootless-config.md)** - Configure rootless mode

---

[← Back to Podman Documentation](README.md) | [Next: Prerequisites →](02-prerequisites.md)
