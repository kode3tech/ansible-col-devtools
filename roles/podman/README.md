# Ansible Role: Podman

Ansible role for installing and configuring Podman on Linux servers.

> 📖 **Complete Guide**: For a comprehensive understanding of Podman with this role, including Root vs Rootless mode, detailed variable explanations, production playbooks, and troubleshooting, see the **[Podman Complete Guide](../../docs/user-guides/podman/)**.

## 📋 Table of Contents

- [Requirements](#requirements)
- [Role Variables](#role-variables)
- [Performance Tuning](#performance-tuning)
- [Dependencies](#dependencies)
- [Example Playbook](#example-playbook)
- [Testing](#testing)
- [License](#license)
- [Author Information](#author-information)

## Requirements

- Ansible >= 2.15
- Target system: Ubuntu 22.04+, Debian 11+, or RHEL 9+
- Root or sudo privileges on target hosts
- **Collection**: `containers.podman` >= 1.10.0 (required for registry authentication)

### Supported Distributions

- **Ubuntu**: 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- **Debian**: 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- **RHEL/CentOS/Rocky/AlmaLinux**: 9, 10

### RHEL-Specific Features

This role includes enhanced support for RHEL-based systems:

- ✅ **Automatic permission fixes** for user Podman config files
- ✅ **Enhanced rootless authentication** with proper file ownership
- ✅ **SELinux context restoration** for container directories
- ✅ **Multi-user support** with isolated authentication
- ✅ **XDG_RUNTIME_DIR fixes** for proper rootless operation
- ✅ **Storage driver conflict resolution** for database graph driver mismatches

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Podman packages to install
podman_packages:
  - podman
  - buildah
  - skopeo
  - crun  # High-performance OCI runtime

# Configure Podman repository
podman_configure_repo: true

# Podman registries configuration
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io

# Podman storage configuration
podman_storage_conf:
  storage:
    driver: overlay
    runroot: /run/containers/storage
    graphroot: /var/lib/containers/storage
    options:
      overlay:
        mountopt: nodev,metacopy=on

# Enable rootless Podman
podman_enable_rootless: true

# Users to configure for rootless Podman
podman_rootless_users: []

# Subuid and subgid ranges for rootless users
podman_subuid_start: 100000
podman_subuid_count: 65536
podman_subgid_start: 100000
podman_subgid_count: 65536

# Insecure registries (HTTP or self-signed certificates)
# WARNING: Only use for trusted internal registries!
podman_insecure_registries: []

# Private registry authentication (optional)
# See: docs/user-guides/podman/04-registry-auth.md
podman_registries_auth: []

# Clean up existing credentials before re-authentication
podman_clean_credentials: false
```

For complete documentation on variables, see [Variables Reference](../../docs/reference/VARIABLES.md).

### Registry Authentication

This role supports **comprehensive** authentication to private container registries with **automatic permission handling**.

**Quick example:**
```yaml
podman_registries_auth:
  - registry: "quay.io"
    username: "myuser"
    password: "{{ vault_quay_password }}"
```

**⚠️ Security:** Always use Ansible Vault for passwords!

**✅ Features:**
- **Multiple registry support** (Docker Hub, Quay.io, GHCR, private registries)
- **Automatic permission fixes** for user config files on all supported systems
- **Per-user authentication** for rootless mode (isolated credentials)
- **SELinux context restoration** on RHEL/CentOS systems
- **Non-interactive authentication** (perfect for CI/CD)

**Rootless mode:** Authentication is performed per-user with proper file ownership.

### Podman Permission Handling

**Problem**: On Linux systems, Podman login may create authentication files with incorrect ownership when using sudo/become, causing permission denied errors.

**Solution**: This role **automatically fixes** file ownership and permissions when `podman_registries_auth` is configured:

```bash
# Before (❌ - permission denied)
-rw-------. 1 root    root    245 /run/user/1000/containers/auth.json

# After (✅ - automatic fix)
-rw-------. 1 user    user    245 /run/user/1000/containers/auth.json
```

**How it works:**
1. Login tasks authenticate to registries (may create files as root)
2. Permission fix tasks run **automatically after login**
3. Files get correct `user:user` ownership in user's XDG_RUNTIME_DIR
4. SELinux contexts restored if enabled (RHEL/CentOS only)
5. Each user has isolated, properly-owned authentication

**Applies to:** All supported distributions (Ubuntu, Debian, RHEL, CentOS, Rocky Linux, AlmaLinux)

📖 **Complete guide:** [Podman Registry Authentication](../../docs/user-guides/podman/04-registry-auth.md)

## Time Synchronization (Compatibility Fixes)

The role includes **targeted time synchronization fixes** to ensure proper repository access and package validation on specific distributions.

### Ubuntu/Debian Specific Handling

**Problem**: Ubuntu 25+ and newer Debian versions may have time synchronization issues that cause repository release files to be considered "invalid" (from the future).

**Solution**: The role automatically handles time synchronization for newer Ubuntu/Debian systems:

```yaml
# Ubuntu 25+ / Debian 13+: Restart systemd-timesyncd for immediate sync
systemctl restart systemd-timesyncd
timedatectl set-ntp true
wait 15 seconds
```

## Configuration Examples

### Performance Optimization (Optional)

You can configure performance optimizations by overriding the `podman_storage_conf` variable. These are **not enabled by default**, but recommended for high-performance environments:

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    runroot: "/run/containers/storage"
    graphroot: "/var/lib/containers/storage"
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

### crun vs runc

The role installs `crun` if available, but uses the system default unless configured otherwise.

**crun advantages:**
- 20-30% faster container startup
- 30-50% lower memory footprint  
- Written in C (vs Go for runc)
- Better performance in LXC containers
- Full OCI runtime compatibility

### XDG_RUNTIME_DIR Configuration

The role automatically configures `systemd-tmpfiles` to create `/run/user/0` for root Podman:

- ✅ Eliminates "XDG_RUNTIME_DIR not found" warnings
- ✅ Persists across reboots
- ✅ Proper permissions (0700)
- ✅ Works in LXC unprivileged containers

### LXC Container Support

Podman can run inside LXC containers (Proxmox, LXD) with proper configuration.

**Required LXC configuration:**
```
features: nesting=1
lxc.apparmor.profile: unconfined
```

**Note:** These settings enable container nesting and disable AppArmor restrictions which are necessary for Podman to function properly inside LXC.

### Custom Configuration

You can override any default values in your playbook:

```yaml
- hosts: servers
  become: true
  vars:
    podman_storage_conf:
      # Keep defaults and override specific values
      engine:
        image_parallel_copies: 20  # Even more parallel downloads
        num_locks: 4096            # More concurrent operations
  roles:
    - kode3tech.podman
```

To disable optimizations and use Podman defaults:

```yaml
podman_storage_conf: {}  # Empty dict = use system defaults
```

## Dependencies

None.

## Example Playbook

Basic installation:

```yaml
- hosts: servers
  become: true
  roles:
    - kode3tech.podman
```

Installation with rootless configuration:

```yaml
- hosts: servers
  become: true
  vars:
    podman_rootless_users:
      - devuser
      - jenkins
  roles:
    - kode3tech.podman
```

Custom registries configuration:

```yaml
- hosts: servers
  become: true
  vars:
    podman_registries_conf:
      unqualified-search-registries:
        - docker.io
        - quay.io
        - registry.mycompany.com
  roles:
    - kode3tech.podman
```

With private registry authentication (rootless):

```yaml
- hosts: servers
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - devuser
      - jenkins
    podman_registries_auth:
      - registry: "https://registry.company.com"
        username: "ci-user"
        password: "{{ vault_registry_password }}"
      - registry: "quay.io"
        username: "quay-user"
        password: "{{ vault_quay_token }}"
  roles:
    - kode3tech.podman
```

With insecure registry (HTTP or self-signed certificate):

```yaml
- hosts: servers
  become: true
  vars:
    podman_insecure_registries:
      - "registry.internal.company.com:5000"
      - "192.168.1.100:5000"
    podman_registries_auth:
      - registry: "registry.internal.company.com:5000"
        username: "admin"
        password: "{{ vault_internal_registry_password }}"
  roles:
    - kode3tech.podman
```

**Note**: Insecure registries allow HTTP and disable certificate verification. Only use for trusted internal networks!

With credential cleanup (when changing passwords or troubleshooting):

```yaml
- hosts: servers
  become: true
  vars:
    # Enable credential cleanup to remove old/invalid credentials
    podman_clean_credentials: true
    podman_registries_auth:
      - registry: "docker.io"
        username: "myuser"
        password: "{{ vault_new_password }}"  # Updated password
  roles:
    - kode3tech.podman
```

**Use case**: When you've changed your registry password and need to re-authenticate, or when troubleshooting "Existing credentials are invalid" errors.

## Testing

This role uses Molecule for testing. To run tests:

```bash
cd podman
molecule test
```

## Features

- ✅ Multi-platform support (Ubuntu, Debian, RHEL/CentOS/Rocky)
- ✅ Automatic repository configuration
- ✅ Podman, Buildah, and Skopeo installation
- ✅ Rootless Podman configuration with subuid/subgid
- ✅ **XDG_RUNTIME_DIR automatic setup** (fixes authentication warnings)
- ✅ Registries configuration
- ✅ Insecure registry support (HTTP/self-signed certificates)
- ✅ Storage configuration
- ✅ Private registry authentication (root and rootless modes)
- ✅ Idempotent operations
- ✅ Comprehensive Molecule tests

## Important Notes

### XDG_RUNTIME_DIR Configuration

This role automatically configures the `XDG_RUNTIME_DIR` directory structure required by Podman:

- **For root**: Creates `/run/user/0` and `/root/.config/containers`
- **For rootless users**: Creates `/run/user/<UID>` and `~/.config/containers`

This prevents the following warning when using `podman login`:
```
WARN[0000] "/run/user/0" directory set by $XDG_RUNTIME_DIR does not exist.
```

**Why this is needed**:
- Podman uses the XDG Base Directory Specification
- The `systemd-logind` service doesn't always create runtime directories for root or service accounts
- Without these directories, Podman cannot store authentication credentials properly

For more details, see: [PODMAN_XDG_RUNTIME_FIX.md](docs/PODMAN_XDG_RUNTIME_FIX.md)

### Registry Authentication

When authenticating with registries:
- Root mode: Credentials stored in `/root/.config/containers/auth.json`
- Rootless mode: Credentials stored in `~/.config/containers/auth.json`
- Automatic fallback to shell command if module fails (Ubuntu 24.04 AppArmor compatibility)

## Podman vs Docker

Podman is a daemonless container engine that:
- Doesn't require a background daemon (more secure)
- Runs containers as non-root by default (rootless mode)
- Is compatible with Docker CLI commands
- Is OCI-compliant
- Uses same container images as Docker

## License

MIT

## Author Information

This role was created by [Kode3Tech DevOps Team](https://github.com/kode3tech).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

Report issues at: https://github.com/kode3tech/ansible-docker/issues
