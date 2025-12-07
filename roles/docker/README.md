# Ansible Role: Docker

**Simple, clean, and reliable** Ansible role for installing and configuring Docker Engine on Linux servers.

## ✨ Key Features

- 🎯 **Simple & Clean**: Focused only on Docker installation and configuration
- 🚀 **Fast Installation**: Optimized for quick deployment without unnecessary complexity
- 🔐 **Registry Authentication**: Built-in support for private registries with automatic permission handling
- 🏗️ **Multi-Platform**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
- ✅ **Production Ready**: Battle-tested with comprehensive error handling

## 📋 Table of Contents

- [Ansible Role: Docker](#ansible-role-docker)
  - [✨ Key Features](#-key-features)
  - [📋 Table of Contents](#-table-of-contents)
  - [Requirements](#requirements)
    - [Supported Distributions](#supported-distributions)
    - [RHEL-Specific Features](#rhel-specific-features)
  - [Role Variables](#role-variables)
    - [Registry Authentication](#registry-authentication)
    - [Docker Permission Handling](#docker-permission-handling)
  - [Simplified Architecture](#simplified-architecture)
  - [Performance Tuning](#performance-tuning)
    - [Default Optimizations](#default-optimizations)
    - [Performance Gains](#performance-gains)
  - [Configuration Examples](#configuration-examples)
    - [Default Configuration (Included)](#default-configuration-included)
    - [Additional Performance Optimization (Optional)](#additional-performance-optimization-optional)
- [Network optimization](#network-optimization)
- [Build optimization](#build-optimization)
    - [Optional: crun Runtime](#optional-crun-runtime)
    - [LXC Container Support](#lxc-container-support)
    - [Custom Configuration](#custom-configuration)
  - [Dependencies](#dependencies)
  - [Example Playbook](#example-playbook)
  - [Testing](#testing)
  - [License](#license)
  - [Author Information](#author-information)

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- **Collection**: `community.docker` >= 3.4.0 (required for registry authentication)

### Supported Distributions

- **Ubuntu**: 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- **Debian**: 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- **RHEL/CentOS/Rocky/AlmaLinux**: 9, 10

### RHEL-Specific Features

This role includes enhanced support for RHEL-based systems:

- ✅ **Automatic permission fixes** for user Docker config files
- ✅ **SELinux context restoration** for Docker configuration directories
- ✅ **Multi-distribution compatibility** optimized for each RHEL release

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Docker edition (ce for Community Edition)
docker_edition: "ce"

# Docker packages to install
docker_packages:
  - docker-{{ docker_edition }}
  - docker-{{ docker_edition }}-cli
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin

# Users to add to docker group
docker_users: []

# Docker daemon configuration (with sensible defaults)
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"

# Enable BuildKit via environment variable
docker_buildkit_enabled: true

# Docker service configuration
docker_service_enabled: true
docker_service_state: started

# Configure Docker repository
docker_configure_repo: true

# List of insecure registries (HTTP or self-signed certificates)
docker_insecure_registries: []

# Private registry authentication (optional)
docker_registries_auth: []
```

For complete documentation on variables, see [Variables Reference](../../docs/reference/VARIABLES.md).

### Registry Authentication

This role supports **comprehensive** authentication to private container registries with **automatic permission handling**.

**Quick example:**
```yaml
docker_registries_auth:
  - registry: "ghcr.io"
    username: "myuser"
    password: "{{ vault_github_token }}"
```

**⚠️ Security:** Always use Ansible Vault for passwords!

**✅ Features:**
- **Multiple registry support** (Docker Hub, GHCR, Quay.io, private registries)
- **Automatic permission fixes** for user config files on all supported systems
- **Per-user authentication** with proper file ownership
- **SELinux context restoration** on RHEL/CentOS systems
- **Non-interactive authentication** (perfect for CI/CD)

📖 **Complete guide:** [Docker Registry Authentication](../../docs/user-guides/docker/04-registry-auth.md)

📖 **Production Deployment:** [Docker Complete Guide](../../docs/user-guides/docker/) - Comprehensive 8-part modular documentation with performance optimization, monitoring, and troubleshooting.

### Docker Permission Handling

**Problem**: On Linux systems, Docker login may create `~/.docker/config.json` as `root:root` when using sudo/become, causing permission denied errors for regular users.

**Solution**: This role **automatically fixes** file ownership and permissions when `docker_registries_auth` is configured:

```bash
# Before (❌ - permission denied)
-rw-------. 1 root    root    162 /home/user/.docker/config.json

# After (✅ - automatic fix)
-rw-------. 1 user    user    162 /home/user/.docker/config.json
```

**How it works:**
1. Login tasks create config files (may be as root)
2. Permission fix tasks run **automatically after login**
3. Files get correct `user:user` ownership
4. SELinux contexts restored if enabled (RHEL/CentOS only)
5. Users can access Docker without permission errors

**Applies to:** All supported distributions (Ubuntu, Debian, RHEL, CentOS, Rocky Linux, AlmaLinux)

## Simplified Architecture

**This role has been optimized for simplicity and reliability:**

- ❌ **No time synchronization complexity** - VMs should be properly configured
- ❌ **No debug output clutter** - Clean execution logs
- ❌ **No unnecessary retries** - Fast, direct installation
- ✅ **Focus on Docker** - Only essential Docker functionality
- ✅ **Automatic permission fixes** - Registry authentication just works

## Performance Tuning

### Default Optimizations

The role includes **sensible defaults** out of the box for optimal performance:

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

### Performance Gains

- **🚀 Fast Installation**: Streamlined tasks without unnecessary delays
- **📊 Optimized Logging**: 10MB max file size with 3 file rotation
- **💾 Efficient Storage**: overlay2 driver for best performance
- **🔧 BuildKit Enabled**: Modern Docker build engine enabled by default

## Configuration Examples

### Default Configuration (Included)

The role now includes **sensible defaults** out of the box:

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
  storage-driver: "overlay2"
```

### Additional Performance Optimization (Optional)

You can add more performance optimizations by extending the configuration:

```yaml
docker_daemon_config:
  # Keep defaults and add more
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
    compress: "true"  # Additional compression
  storage-driver: "overlay2"
  # Add network optimization
  userland-proxy: false
  iptables: true
  # Add build optimization
  max-concurrent-downloads: 10
```
    max-file: "3"
    compress: "true"
    mode: "non-blocking"
  
  # Network optimization
  userland-proxy: false
  iptables: true
  
  # Build optimization
  features:
### Optional: crun Runtime

To use `crun` (if installed):

```yaml
docker_daemon_config:
  default-runtime: "crun"
  runtimes:
    crun:
      path: "/usr/bin/crun"
```

### LXC Container Support

Docker can run inside LXC containers (Proxmox, LXD) with proper configuration.

**Required LXC configuration:**
```
features: nesting=1
lxc.apparmor.profile: unconfined
```

**Note:** These settings enable container nesting and disable AppArmor restrictions which are necessary for Docker to function properly inside LXC.

### Custom Configuration

You can override any default values in your playbook:

```yaml
- hosts: docker_hosts
  become: true
  vars:
    docker_daemon_config:
      # Keep all defaults and override specific values
      max-concurrent-downloads: 20  # Even more parallel downloads
      default-shm-size: "128M"      # Larger shared memory
  roles:
    - kode3tech.docker
```

## Dependencies

None.

## Example Playbook

Basic installation:

```yaml
- hosts: docker_hosts
  become: true
  roles:
    - code3tech.devtools.docker
```

With custom configuration:

```yaml
- hosts: docker_hosts
  become: true
  vars:
    docker_users:
      - deploy
      - jenkins
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "10m"
        max-file: "3"
  roles:
    - code3tech.devtools.docker
```

With private registry authentication:

```yaml
- hosts: docker_hosts
  become: true
  vars:
    docker_registries_auth:
      - registry: "https://registry.company.com"
        username: "ci-user"
        password: "{{ vault_registry_password }}"
      - registry: "ghcr.io"
        username: "github-user"
        password: "{{ vault_github_token }}"
  roles:
    - code3tech.devtools.docker
```

With insecure registry (HTTP or self-signed certificate):

```yaml
- hosts: docker_hosts
  become: true
  vars:
    docker_insecure_registries:
      - "registry.internal.company.com:5000"
      - "192.168.1.100:5000"
    docker_registries_auth:
      - registry: "http://registry.internal.company.com:5000"
        username: "admin"
        password: "{{ vault_internal_registry_password }}"
  roles:
    - code3tech.devtools.docker
```

**Note**: Using insecure registries disables certificate verification and allows HTTP. Only use for trusted internal networks!

## Testing

This role includes Molecule tests. To run tests:

```bash
molecule test
```

## License

MIT

## Author Information

This role was created by the **Code3Tech DevOps Team**.

- GitHub: [code3tech](https://github.com/code3tech)
- Repository: [ansible-docker](https://github.com/code3tech/ansible-docker)

**Recent Improvements (v1.0+):**
- 🧹 **Simplified codebase** - Removed unnecessary complexity and debug output
- ⚡ **Faster execution** - Eliminated retry loops and time sync delays
- 📝 **Cleaner configuration** - Reduced variables and simplified defaults
- 🎯 **Production focus** - Optimized for reliability and maintainability
