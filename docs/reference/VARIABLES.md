# Variables Reference

Complete reference of all variables available in the `code3tech.devtools` collection roles.

## 📋 Table of Contents

- [Docker Role Variables](#docker-role-variables)
- [Podman Role Variables](#podman-role-variables)
- [asdf Role Variables](#asdf-role-variables)

---

## Docker Role Variables

### Basic Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `docker_edition` | string | No | `"ce"` | Docker edition to install (ce = Community Edition) |
| `docker_packages` | list | No | See below | List of Docker packages to install |
| `docker_users` | list | No | `[]` | Users to add to docker group |
| `docker_service_enabled` | boolean | No | `true` | Enable Docker service on boot |
| `docker_service_state` | string | No | `"started"` | Docker service state (started/stopped) |
| `docker_configure_repo` | boolean | No | `true` | Configure Docker official repository |

**Default `docker_packages`:**
```yaml
docker_packages:
  - docker-{{ docker_edition }}
  - docker-{{ docker_edition }}-cli
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin
```

### Daemon Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `docker_daemon_config` | dict | No | See below | Docker daemon.json configuration |

**Default `docker_daemon_config` (with performance optimizations):**
```yaml
docker_daemon_config:
  # Storage optimization
  storage-driver: "overlay2"
  storage-opts:
    - "overlay2.override_kernel_check=true"
  
  # Logging optimization
  log-driver: "json-file"
  log-opts:
    max-size: "10m"
    max-file: "3"
    compress: "true"
    mode: "non-blocking"
    max-buffer-size: "4m"
  
  # Network optimization
  userland-proxy: false
  iptables: true
  
  # Build optimization
  features:
    buildkit: true
  
  # Download optimization
  max-concurrent-downloads: 10
  max-concurrent-uploads: 10
  max-download-attempts: 3
  
  # Runtime configuration
  default-runtime: "runc"
  runtimes:
    runc:
      path: "/usr/bin/runc"
  
  # Resource limits
  default-ulimits:
    nofile:
      Name: "nofile"
      Hard: 65536
      Soft: 65536
    nproc:
      Name: "nproc"
      Hard: 32768
      Soft: 16384
  
  default-shm-size: "64M"
```

### Registry Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `docker_insecure_registries` | list | No | `[]` | Insecure registries (HTTP or self-signed certs) |
| `docker_registries_auth` | list | No | `[]` | Private registry authentication credentials |

**Example `docker_insecure_registries`:**
```yaml
docker_insecure_registries:
  - "registry.internal.company.com:5000"
  - "192.168.1.100:5000"
  - "localhost:5000"
```

**Example `docker_registries_auth`:**
```yaml
docker_registries_auth:
  - registry: "https://index.docker.io/v1/"
    username: "dockerhub-user"
    password: "{{ vault_dockerhub_token }}"
    email: "user@example.com"  # Optional
  
  - registry: "ghcr.io"
    username: "github-user"
    password: "{{ vault_github_token }}"
  
  - registry: "registry.company.com"
    username: "ci-user"
    password: "{{ vault_registry_password }}"
```

### Registry Authentication Object Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry URL (Docker Hub: `https://index.docker.io/v1/`, others: hostname) |
| `username` | string | Yes | Registry username |
| `password` | string | Yes | User password or access token |
| `email` | string | No | User email (legacy, rarely needed) |

**⚠️ Security Note**: Always use Ansible Vault to encrypt passwords. Never store plain-text credentials.

**🔧 RHEL Enhancement**: The Docker role automatically fixes file ownership for `~/.docker/config.json` on RHEL systems, ensuring users can access Docker without permission denied errors.

---

## Podman Role Variables

> 📖 **Complete Guide**: For detailed explanations of each variable with examples and use cases, see the **[Podman Complete Guide](../user-guides/PODMAN_COMPLETE_GUIDE.md)**.

### Basic Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `podman_packages` | list | No | See below | Podman packages to install |
| `podman_configure_repo` | boolean | No | `true` | Configure Podman repository |

**Default `podman_packages`:**
```yaml
podman_packages:
  - podman
  - buildah
  - skopeo
  - crun  # High-performance OCI runtime (20-30% faster than runc)
```

### Rootless Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `podman_enable_rootless` | boolean | No | `true` | Enable rootless Podman support |
| `podman_rootless_users` | list | No | `[]` | Users to configure for rootless Podman |
| `podman_subuid_start` | integer | No | `100000` | Starting UID for subuid ranges |
| `podman_subuid_count` | integer | No | `65536` | Number of UIDs in subuid range |
| `podman_subgid_start` | integer | No | `100000` | Starting GID for subgid ranges |
| `podman_subgid_count` | integer | No | `65536` | Number of GIDs in subgid range |

**Example `podman_rootless_users`:**
```yaml
podman_rootless_users:
  - "myuser"
  - "developer"
  - "ci-user"
```

### Registries Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `podman_registries_conf` | dict | No | See below | Podman registries.conf configuration |

**Default `podman_registries_conf`:**
```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io
```

### Storage Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `podman_storage_conf` | dict | No | See below | Podman storage.conf configuration |

**Default `podman_storage_conf` (with performance optimizations):**
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

### Registry Authentication

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `podman_insecure_registries` | list | No | `[]` | Insecure registries (HTTP or self-signed certs) |
| `podman_registries_auth` | list | No | `[]` | Private registry authentication credentials |
| `podman_clean_credentials` | boolean | No | `false` | Clean old credentials before re-authentication |

**Storage Driver Conflict Detection:**
The role automatically detects and resolves storage driver conflicts before authentication. When `podman_registries_auth` is configured, the role will:
1. Test storage consistency with `podman info`
2. Automatically reset storage if conflicts are detected
3. Clean storage directories to ensure reliable authentication
4. Proceed with fresh registry authentication

⚠️ **Important:** Storage reset removes ALL containers and images but ensures reliable operation.

**Example `podman_insecure_registries`:**
```yaml
podman_insecure_registries:
  - "registry.internal.company.com:5000"
  - "192.168.1.100:5000"
```

**Example `podman_registries_auth`:**
```yaml
podman_registries_auth:
  - registry: "quay.io"
    username: "myuser"
    password: "{{ vault_quay_password }}"
  
  - registry: "registry.company.com"
    username: "ci-user"
    password: "{{ vault_company_password }}"
```

### Registry Authentication Object Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `registry` | string | Yes | Registry hostname (Docker Hub: `docker.io`, others: hostname) |
| `username` | string | Yes | Registry username |
| `password` | string | Yes | User password or access token |

**⚠️ Security Note**: Always use Ansible Vault to encrypt passwords. Never store plain-text credentials.

**🔧 RHEL Enhancement**: The Podman role automatically fixes file ownership for authentication files in user's `XDG_RUNTIME_DIR` on RHEL systems, ensuring proper per-user authentication with correct permissions.

---

## asdf Role Variables

### Basic Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `asdf_version` | string | No | `"latest"` | asdf version to install (e.g., "v0.18.0" or "latest") |
| `asdf_install_dir` | string | No | `"/opt/asdf"` | asdf installation directory |
| `asdf_data_dir` | string | No | `""` | Custom data directory (defaults to asdf_install_dir) |
| `asdf_install_dependencies` | boolean | No | `true` | Install system dependencies required by asdf plugins |
| `asdf_configure_shell` | boolean | No | `true` | Configure shell profiles automatically |

### User Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `asdf_users` | list | No | `[]` | Users who should have asdf configured |

**Example `asdf_users`:**
```yaml
asdf_users:
  - name: "myuser"
    shell: "bash"  # Optional: bash (default), zsh, or fish
    plugins:
      - name: "nodejs"
        versions:
          - "20.11.0"
          - "18.19.0"
        global: "20.11.0"
      - name: "python"
        versions:
          - "3.12.1"
        global: "3.12.1"
```

### User Object Properties

| Property | Type | Required | Default | Description |
|----------|------|----------|----------|-------------|
| `name` | string | Yes | - | Username (home directory auto-detected) |
| `shell` | string | No | `"bash"` | User's shell (bash, zsh, or fish) |
| `plugins` | list | No | `[]` | List of asdf plugins to install |

### Plugin Object Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Plugin name (e.g., "nodejs", "python", "ruby") |
| `versions` | list | No | List of versions to install |
| `global` | string | No | Default global version |

### Advanced Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `asdf_binary_url` | string | No | GitHub releases | asdf binary download base URL |
| `asdf_shell_profiles` | dict | No | See below | Shell profile files by shell type |

**Default `asdf_shell_profiles`:**
```yaml
asdf_shell_profiles:
  bash: ".bashrc"
  zsh: ".zshrc"
  fish: ".config/fish/config.fish"
```

---

## Variable Usage Examples

### Minimal Docker Installation

```yaml
- hosts: servers
  become: true
  roles:
    - kode3tech.devtools.docker
```

### Docker with Custom Configuration

```yaml
- hosts: servers
  become: true
  vars:
    docker_users:
      - deploy
      - jenkins
    
    docker_daemon_config:
      log-driver: "json-file"
      log-opts:
        max-size: "20m"
        max-file: "5"
      storage-driver: "overlay2"
    
    docker_registries_auth:
      - registry: "registry.company.com"
        username: "ci-user"
        password: "{{ vault_registry_password }}"
  
  roles:
    - kode3tech.devtools.docker
```

### Podman with Rootless Users

```yaml
- hosts: servers
  become: true
  vars:
    podman_enable_rootless: true
    podman_rootless_users:
      - developer
      - tester
    
    podman_registries_auth:
      - registry: "quay.io"
        username: "myuser"
        password: "{{ vault_quay_password }}"
  
  roles:
    - code3tech.devtools.podman
```

### asdf with Multiple Plugins

```yaml
- hosts: servers
  become: true
  vars:
    asdf_users:
      - name: "frontend"
        shell: "zsh"
        plugins:
          - name: "nodejs"
            versions: ["20.11.0", "18.19.0"]
            global: "20.11.0"
      
      - name: "backend"
        shell: "bash"
        plugins:
          - name: "python"
            versions: ["3.12.1", "3.11.7"]
            global: "3.12.1"
          - name: "golang"
            versions: ["1.21.5"]
            global: "1.21.5"
  
  roles:
    - code3tech.devtools.asdf
```

---

## Security Recommendations

### Always Use Ansible Vault for Sensitive Data

**Never commit plain-text passwords!**

```bash
# Create vault file
ansible-vault create vars/secrets.yml

# Add encrypted variables
vault_dockerhub_token: "your-secret-token"
vault_github_token: "ghp_your_token"
vault_registry_password: "your-password"
```

Reference in playbooks:
```yaml
vars_files:
  - vars/secrets.yml

vars:
  docker_registries_auth:
    - registry: "ghcr.io"
      username: "myuser"
      password: "{{ vault_github_token }}"  # ✅ Secure!
```

Run with vault password:
```bash
ansible-playbook playbook.yml --ask-vault-pass
```

---

## See Also

- [Docker Role README](../../roles/docker/README.md)
- [Podman Role README](../../roles/podman/README.md)
- [asdf Role README](../../roles/asdf/README.md)
- [Registry Authentication Guide](../user-guides/REGISTRY_AUTHENTICATION.md)
- [FAQ](../FAQ.md)

---

[← Back to Documentation Index](../README.md)
