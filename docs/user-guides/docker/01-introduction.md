# Introduction

Overview of Docker, its architecture, and comparison with Podman.

---

## 📋 Table of Contents

- [What is Docker?](#what-is-docker)
- [Docker Architecture](#docker-architecture)
- [Docker Components](#docker-components)
- [Docker vs Podman](#docker-vs-podman)
- [When to Use Docker](#when-to-use-docker)

---

## What is Docker?

Docker is a **container runtime platform** that enables you to package, distribute, and run applications in isolated environments called containers.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Client-Server Architecture** | Docker daemon (dockerd) runs as a background service |
| **OCI-Compliant** | Uses industry-standard container images |
| **Ecosystem** | Largest container ecosystem with Docker Hub |
| **BuildKit** | Modern build engine for faster, more efficient builds |
| **Compose** | Multi-container application orchestration |

### Why Containers?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL vs CONTAINERS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TRADITIONAL DEPLOYMENT          CONTAINER DEPLOYMENT               │
│                                                                      │
│  ┌─────────────────────┐         ┌─────────────────────┐           │
│  │   Application A     │         │  ┌─────┐ ┌─────┐   │           │
│  ├─────────────────────┤         │  │App A│ │App B│   │           │
│  │   Application B     │         │  └──┬──┘ └──┬──┘   │           │
│  ├─────────────────────┤         │     │       │      │           │
│  │  Libraries/Deps     │         │  ┌──┴───────┴──┐   │           │
│  ├─────────────────────┤         │  │   Docker    │   │           │
│  │  Operating System   │         │  ├─────────────┤   │           │
│  ├─────────────────────┤         │  │     OS      │   │           │
│  │     Hardware        │         │  ├─────────────┤   │           │
│  └─────────────────────┘         │  │  Hardware   │   │           │
│                                  │  └─────────────┘   │           │
│  ❌ Dependency conflicts         │  ✅ Isolation      │           │
│  ❌ Environment drift            │  ✅ Reproducible   │           │
│  ❌ Hard to scale                │  ✅ Portable       │           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Container Benefits

- **Isolation** - Each application runs in its own environment
- **Reproducibility** - Same container runs identically everywhere
- **Portability** - Build once, run anywhere
- **Efficiency** - Lightweight compared to VMs
- **Scalability** - Easy to replicate and distribute

---

## Docker Architecture

Docker uses a client-server architecture:

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
│  CLIENT SIDE                     SERVER SIDE (Daemon)               │
│  ───────────                     ───────────────────                │
│  • docker CLI                    • Runs as root                     │
│  • docker-compose                • Manages containers               │
│  • REST API clients              • Handles images                   │
│  • SDKs (Python, Go)             • Networking & storage            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **Client** sends command (e.g., `docker run nginx`)
2. **REST API** transmits request to daemon
3. **Daemon** processes request
4. **containerd** manages container lifecycle
5. **runc** creates the actual container

---

## Docker Components

### Core Components

| Component | Description |
|-----------|-------------|
| **Docker Daemon (dockerd)** | Background service managing containers, images, networks |
| **Docker CLI** | Command-line interface for interacting with daemon |
| **containerd** | Container runtime managing container lifecycle |
| **runc** | Low-level container runtime (OCI spec) |

### Installed Packages

The role installs these packages:

| Package | Description |
|---------|-------------|
| `docker-ce` | Docker Engine (Community Edition) |
| `docker-ce-cli` | Command-line interface |
| `containerd.io` | Container runtime |
| `docker-buildx-plugin` | Extended build capabilities |
| `docker-compose-plugin` | Multi-container orchestration |

### Key Concepts

#### Images

```
┌─────────────────────────────────────────┐
│              DOCKER IMAGE               │
├─────────────────────────────────────────┤
│  Layer 4: Application code              │
├─────────────────────────────────────────┤
│  Layer 3: Application dependencies      │
├─────────────────────────────────────────┤
│  Layer 2: Runtime (Node, Python, etc.)  │
├─────────────────────────────────────────┤
│  Layer 1: Base OS (Alpine, Ubuntu)      │
└─────────────────────────────────────────┘

• Images are read-only templates
• Built from layers (copy-on-write)
• Stored in registries (Docker Hub, GHCR)
```

#### Containers

```
┌─────────────────────────────────────────┐
│             CONTAINER                   │
├─────────────────────────────────────────┤
│  Writable Layer (container changes)     │
├─────────────────────────────────────────┤
│  Image Layers (read-only)               │
│  ┌───────────────────────────────────┐ │
│  │ Layer 4  │ Layer 3  │ Layer 2     │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘

• Containers are running instances of images
• Each container has a writable layer
• Changes are isolated from other containers
```

#### Volumes

```
┌─────────────────────────────────────────┐
│             CONTAINER                   │
│  ┌───────────────────────────────────┐ │
│  │      Application Data              │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│                  ▼                      │
│  ┌───────────────────────────────────┐ │
│  │         VOLUME MOUNT              │ │
│  │    /var/lib/docker/volumes/       │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘

• Volumes persist data beyond container lifecycle
• Can be shared between containers
• Better performance than bind mounts
```

---

## Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| **Architecture** | Client-Server (daemon) | Daemonless (fork-exec) |
| **Root Required** | Daemon runs as root | Supports rootless |
| **Security** | Daemon is attack surface | Smaller attack surface |
| **Systemd Integration** | Limited | Native |
| **Ecosystem** | Largest | Growing |
| **CLI Compatibility** | Native | Compatible with Docker |
| **Compose** | Native | podman-compose |
| **Kubernetes Pods** | No | Native support |
| **Image Format** | OCI | OCI |

### When to Choose Docker

✅ **Choose Docker when:**
- Maximum ecosystem compatibility needed
- Using Docker Compose extensively
- Team is already familiar with Docker
- Need Docker Desktop features
- Using Docker Swarm for orchestration

### When to Choose Podman

✅ **Choose Podman when:**
- Rootless containers are required
- Security is paramount
- Native systemd integration needed
- Running on RHEL-based systems
- Kubernetes-native pod support needed

### CLI Compatibility

Most Docker commands work identically with Podman:

```bash
# Docker
docker run -d nginx
docker ps
docker build -t myimage .

# Podman (same commands!)
podman run -d nginx
podman ps
podman build -t myimage .
```

---

## When to Use Docker

### Ideal Use Cases

| Use Case | Why Docker? |
|----------|-------------|
| **CI/CD Pipelines** | Reproducible build environments |
| **Microservices** | Isolated, scalable services |
| **Development** | Consistent dev environments |
| **Application Packaging** | Portable application distribution |
| **Multi-Container Apps** | Docker Compose orchestration |

### Docker in This Collection

The `code3tech.devtools.docker` role provides:

- **Automated Installation** - Package management, repository setup
- **User Configuration** - Docker group management
- **Daemon Configuration** - Performance optimization
- **Registry Authentication** - Private registry access
- **Permission Handling** - Automatic permission fixes

---

## Next Steps

- **[Prerequisites](02-prerequisites.md)** - System requirements and setup
- **[Basic Installation](03-basic-installation.md)** - Your first Docker deployment

---

[← Back to Docker Documentation](README.md) | [Next: Prerequisites →](02-prerequisites.md)
