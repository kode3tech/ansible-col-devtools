# Basic Installation

Minimal Podman installation with sensible defaults.

---

## 📋 Table of Contents

- [Minimal Installation](#minimal-installation)
- [What Gets Installed](#what-gets-installed)
- [Default Configuration](#default-configuration)
- [Verification](#verification)
- [Quick Examples](#quick-examples)

---

## Minimal Installation

### 5-Minute Playbook

```yaml
---
- name: Install Podman
  hosts: all
  become: true
  roles:
    - code3tech.devtools.podman
```

**This single playbook:**
- Installs Podman, Buildah, Skopeo, crun
- Configures default registries (docker.io, quay.io)
- Enables rootless mode support
- Applies performance-optimized defaults

### Run It

```bash
ansible-playbook install-podman.yml -i inventory.ini
```

---

## What Gets Installed

### Default Packages

```yaml
podman_packages:
  - podman      # Container engine
  - buildah     # Image builder
  - skopeo      # Image transfer tool
  - crun        # Fast OCI runtime
```

| Package | Description |
|---------|-------------|
| `podman` | Main container engine |
| `buildah` | Build OCI images without daemon |
| `skopeo` | Copy/inspect container images |
| `crun` | High-performance runtime (20-30% faster) |

### Additional Packages (Optional)

```yaml
podman_packages:
  - podman
  - buildah
  - skopeo
  - crun
  - podman-compose   # Docker Compose compatibility
  - udica            # SELinux policy generator (RHEL)
```

---

## Default Configuration

### Registries

Default registry search order:

```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io   # Docker Hub
    - quay.io     # Quay.io
```

When you run:
```bash
podman pull alpine
```

Podman searches: `docker.io/library/alpine`, then `quay.io/alpine`

### Storage

Default storage configuration:

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

### What Each Setting Does

| Setting | Value | Purpose |
|---------|-------|---------|
| `driver: overlay` | Storage driver | Best for most systems |
| `metacopy=on` | Mount option | 30-50% I/O reduction |
| `runtime: crun` | Container runtime | 20-30% faster startup |
| `events_logger: file` | Logging | Lower overhead |
| `cgroup_manager: systemd` | Resource management | Better integration |
| `image_parallel_copies: 10` | Parallel downloads | Faster pulls |

---

## Verification

### Check Installation

```bash
# Podman version
podman --version

# Full system info
podman info

# Check runtime
podman info | grep -i runtime
```

### Test Container

```bash
# Pull and run test container
podman run --rm hello-world

# Run Alpine
podman run --rm alpine echo "Podman works!"
```

### Verify Storage Driver

```bash
podman info --format '{{.Store.GraphDriverName}}'
# Expected: overlay
```

### Verify Runtime

```bash
podman info --format '{{.Host.OCIRuntime.Name}}'
# Expected: crun
```

---

## Quick Examples

### Run Nginx

```bash
# Root mode
sudo podman run -d -p 80:80 nginx

# Rootless mode (port > 1024)
podman run -d -p 8080:80 nginx
```

### Build Image

```bash
# From Dockerfile
podman build -t myapp:latest .

# Using Buildah
buildah from alpine
buildah run alpine-working-container apk add nginx
buildah commit alpine-working-container mynginx:latest
```

### Copy Images

```bash
# Between registries
skopeo copy docker://docker.io/alpine:latest docker://myregistry.com/alpine:latest

# Inspect remote image
skopeo inspect docker://docker.io/alpine:latest
```

---

## Playbook Variations

### With Specific Users

```yaml
---
- name: Install Podman with Rootless Users
  hosts: all
  become: true
  vars:
    podman_rootless_users:
      - developer
      - jenkins
  roles:
    - code3tech.devtools.podman
```

### With Custom Storage

```yaml
---
- name: Install Podman with Custom Storage
  hosts: all
  become: true
  vars:
    podman_storage_conf:
      storage:
        driver: "overlay"
        graphroot: "/data/podman/storage"
        runroot: "/run/containers/storage"
        options:
          overlay:
            mountopt: "nodev,metacopy=on"
      engine:
        runtime: "crun"
  roles:
    - code3tech.devtools.podman
```

### With Private Registry

```yaml
---
- name: Install Podman with Registry Auth
  hosts: all
  become: true
  vars_files:
    - vars/secrets.yml
  vars:
    podman_registries_auth:
      - registry: "docker.io"
        username: "myuser"
        password: "{{ vault_dockerhub_token }}"
  roles:
    - code3tech.devtools.podman
```

---

## Post-Installation

### Verify Rootless Support

```bash
# As regular user (no sudo)
podman info | grep rootless
# Expected: rootless: true
```

### Check Subuid/Subgid

```bash
cat /etc/subuid
cat /etc/subgid
```

### Storage Location

| Mode | Location |
|------|----------|
| Root | `/var/lib/containers/storage` |
| Rootless | `~/.local/share/containers/storage` |

---

## Troubleshooting

### Permission Denied

```
Error: permission denied
```

**Solution:** Ensure user is in `podman_rootless_users`:
```yaml
podman_rootless_users:
  - myuser
```

### Storage Driver Error

```
Error: cannot find graphroot
```

**Solution:** Create directory with proper permissions:
```bash
sudo mkdir -p /var/lib/containers/storage
sudo chmod 711 /var/lib/containers/storage
```

### Registry Connection Failed

```
Error: name resolution failed
```

**Solution:** Check network connectivity:
```bash
ping docker.io
curl -I https://registry-1.docker.io/v2/
```

---

## Next Steps

- **[Registry Authentication](04-registry-auth.md)** - Private registries
- **[Rootless Configuration](05-rootless-config.md)** - Per-user setup
- **[Production Deployment](06-production-deployment.md)** - Complete playbooks

---

[← Back to Podman Documentation](README.md) | [Previous: Prerequisites](02-prerequisites.md) | [Next: Registry Authentication →](04-registry-auth.md)
