# Troubleshooting

Common issues, solutions, and diagnostic procedures for Podman deployments.

---

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Common Errors](#common-errors)
  - [XDG_RUNTIME_DIR Issues](#xdg_runtime_dir-issues)
  - [Storage Driver Errors](#storage-driver-errors)
  - [Permission Denied](#permission-denied)
  - [Subuid/Subgid Problems](#subuidsubgid-problems)
  - [Registry Authentication Errors](#registry-authentication-errors)
  - [Container Runtime Errors](#container-runtime-errors)
- [Variables Reference](#variables-reference)
- [Diagnostic Commands](#diagnostic-commands)
- [FAQ](#faq)
- [External Resources](#external-resources)

---

## Quick Diagnostics

Run this script for quick health check:

```bash
#!/bin/bash
echo "=== Podman Diagnostics ==="

echo -e "\n1. Podman Version:"
podman --version || echo "ERROR: Podman not installed"

echo -e "\n2. Info:"
podman info 2>&1 | head -20

echo -e "\n3. User Namespaces:"
cat /etc/subuid | grep $(whoami) || echo "ERROR: No subuid mapping"
cat /etc/subgid | grep $(whoami) || echo "ERROR: No subgid mapping"

echo -e "\n4. XDG_RUNTIME_DIR:"
echo "Value: $XDG_RUNTIME_DIR"
ls -la $XDG_RUNTIME_DIR 2>/dev/null || echo "ERROR: Dir not accessible"

echo -e "\n5. Storage:"
podman info --format '{{.Store.GraphDriverName}}' 2>&1

echo -e "\n6. Runtime:"
podman info --format '{{.Host.OCIRuntime.Name}}' 2>&1

echo -e "\n7. Test Container:"
podman run --rm alpine echo "Hello from Podman" 2>&1
```

---

## Common Errors

### XDG_RUNTIME_DIR Issues

#### Error: XDG_RUNTIME_DIR Not Set

```
ERRO[0000] XDG_RUNTIME_DIR directory "/run/user/0" is not owned by the current user
```

**Cause:** Variable not set or wrong owner.

**Solution:**

```bash
# Check current value
echo $XDG_RUNTIME_DIR

# Set correctly
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Verify ownership
ls -la $XDG_RUNTIME_DIR
# Should show: drwx------ 10 youruser youruser
```

**Permanent fix in shell profile:**

```bash
# Add to ~/.bashrc or ~/.zshrc
if [ -z "$XDG_RUNTIME_DIR" ]; then
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi
```

**Ansible fix:**

```yaml
podman_fix_xdg_runtime_dir: true  # Default: true
```

---

#### Error: Directory Has Wrong Owner

```
ERRO[0000] XDG_RUNTIME_DIR directory "/run/user/1000" is not owned by the current user
```

**Cause:** Directory created by root or different user.

**Solution:**

```bash
# Check owner
ls -la /run/user/$(id -u)

# Fix ownership (as root)
sudo chown -R $(id -u):$(id -g) /run/user/$(id -u)
```

---

### Storage Driver Errors

#### Error: Database Graph Driver Mismatch

```
Error: database configuration mismatch:
option "graphdriver" has value "overlay" from database "overlay2" from containers.conf
```

**Cause:** Storage driver changed after containers created.

**Solution:**

```bash
# CAUTION: This removes all containers and images!
podman system reset --force

# Or remove storage manually
rm -rf ~/.local/share/containers/storage

# Then run Ansible role again
```

---

#### Error: overlay: mount program /usr/bin/fuse-overlayfs not found

```
Error: mount /home/user/.local/share/containers/storage/overlay:/home/user/.local/share/containers/storage/overlay, flags: 0x1000: overlay: mount program /usr/bin/fuse-overlayfs not found
```

**Cause:** fuse-overlayfs not installed for rootless mode.

**Solution:**

```bash
# Ubuntu/Debian
sudo apt install fuse-overlayfs

# RHEL/CentOS
sudo dnf install fuse-overlayfs
```

**Ansible auto-installs this package** - ensure role completed successfully.

---

#### Error: Invalid graphroot

```
Error: invalid graphroot path "/data/containers/storage"
```

**Cause:** Custom storage path doesn't exist or wrong permissions.

**Solution:**

```bash
# Create directory
sudo mkdir -p /data/containers/storage

# For rootless users
mkdir -p ~/.local/share/containers/storage
```

---

### Permission Denied

#### Error: Permission Denied on Auth File

```
Error: writing auth file: open /run/user/1000/containers/auth.json: permission denied
```

**Cause:** Auth directory/file has wrong owner.

**Solution:**

```bash
# Check ownership
ls -la /run/user/$(id -u)/containers/

# Fix ownership
sudo chown -R $(id -u):$(id -g) /run/user/$(id -u)/containers/
```

**The role includes automatic permission fixes.**

---

#### Error: Permission Denied Reading Image

```
Error: reading image: permission denied
```

**Cause:** Storage directories have wrong permissions.

**Solution:**

```bash
# Reset storage permissions
podman system reset --force

# Or fix manually
chmod -R 700 ~/.local/share/containers/storage
```

---

### Subuid/Subgid Problems

#### Error: Cannot Find mappings

```
Error: cannot find mappings for user myuser: No subuid ranges found for user "myuser" in /etc/subuid
```

**Cause:** User not configured in subuid/subgid.

**Solution:**

```bash
# Check current mappings
cat /etc/subuid
cat /etc/subgid

# Add mapping (as root)
echo "myuser:100000:65536" | sudo tee -a /etc/subuid
echo "myuser:100000:65536" | sudo tee -a /etc/subgid

# Or use usermod
sudo usermod --add-subuids 100000-165535 myuser
sudo usermod --add-subgids 100000-165535 myuser
```

**Ansible configuration:**

```yaml
podman_rootless_users:
  - myuser  # Role auto-configures subuid/subgid
```

---

#### Error: UID/GID Range Too Small

```
Error: there might not be enough IDs available in the namespace
```

**Cause:** Subuid/subgid range too small.

**Solution:**

```bash
# Check current range
grep myuser /etc/subuid
# Example: myuser:100000:1000 (too small!)

# Edit to increase (need 65536)
sudo vi /etc/subuid
# Change: myuser:100000:65536

sudo vi /etc/subgid
# Change: myuser:100000:65536
```

---

### Registry Authentication Errors

#### Error: Unauthorized

```
Error: authenticating creds for "docker.io": unauthorized: incorrect username or password
```

**Cause:** Wrong credentials.

**Solution:**

1. Verify credentials manually:
   ```bash
   podman login docker.io -u username
   # Enter password when prompted
   ```

2. Check Vault encryption:
   ```bash
   ansible-vault view vars/secrets.yml
   ```

3. Use token instead of password (recommended):
   - Docker Hub: Create access token at hub.docker.com/settings/security
   - GitHub: Create PAT at github.com/settings/tokens

---

#### Error: Registry URL Format

```
Error: authenticating creds for "https://docker.io/v1/": 404 Not Found
```

**Cause:** Wrong registry URL format for Podman.

**Solution:**

Podman uses **hostname only**, not full URLs:

| Registry | Wrong | Correct |
|----------|-------|---------|
| Docker Hub | `https://index.docker.io/v1/` | `docker.io` |
| GHCR | `https://ghcr.io` | `ghcr.io` |
| Quay | `https://quay.io/v2/` | `quay.io` |

```yaml
# Correct format for Podman
podman_registries_auth:
  - registry: "docker.io"  # Not https://index.docker.io/v1/
    username: "user"
    password: "{{ vault_token }}"
```

---

#### Error: Certificate Error

```
Error: pinging container registry registry.example.com: Get "https://registry.example.com/v2/": x509: certificate signed by unknown authority
```

**Cause:** Self-signed or invalid certificate.

**Solution:**

```yaml
# Add to insecure registries
podman_insecure_registries:
  - "registry.example.com:5000"
```

⚠️ Only use for trusted internal networks!

---

### Container Runtime Errors

#### Error: crun Not Found

```
Error: OCI runtime error: exec: "crun": executable file not found in $PATH
```

**Cause:** crun not installed.

**Solution:**

```bash
# Ubuntu/Debian
sudo apt install crun

# RHEL/CentOS  
sudo dnf install crun
```

**Ansible auto-installs crun** - ensure role completed.

---

#### Error: Container Already Exists

```
Error: container name "mycontainer" is already in use
```

**Solution:**

```bash
# Remove existing container
podman rm mycontainer

# Or remove forcefully
podman rm -f mycontainer
```

---

#### Error: Port Already in Use

```
Error: rootlessport cannot expose privileged port 80, you can add 'net.ipv4.ip_unprivileged_port_start=80' to /etc/sysctl.conf
```

**Cause:** Rootless cannot bind to ports < 1024 by default.

**Solution:**

```bash
# Option 1: Use higher port
podman run -p 8080:80 nginx

# Option 2: Enable unprivileged ports (system-wide)
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**Ansible configuration:**

```yaml
podman_allow_unprivileged_ports: true
podman_unprivileged_port_start: 80
```

---

## Variables Reference

### Complete Variable List

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `podman_edition` | string | `""` | Podman edition (empty for standard) |
| `podman_packages` | list | `[podman, buildah, skopeo, crun, fuse-overlayfs]` | Packages to install |
| `podman_enable_rootless` | bool | `true` | Enable rootless configuration |
| `podman_rootless_users` | list | `[]` | Users for rootless Podman |
| `podman_configure_storage` | bool | `true` | Apply storage configuration |
| `podman_insecure_registries` | list | `[]` | HTTP/self-signed registries |
| `podman_registries_auth` | list | `[]` | Registry authentication |
| `podman_allow_unprivileged_ports` | bool | `false` | Allow ports < 1024 |
| `podman_unprivileged_port_start` | int | `1024` | Lowest unprivileged port |
| `podman_fix_xdg_runtime_dir` | bool | `true` | Auto-fix XDG_RUNTIME_DIR |
| `podman_clean_credentials` | bool | `false` | Remove old auth before login |

### podman_storage_conf

Storage and engine configuration:

```yaml
podman_storage_conf:
  storage:
    driver: "overlay"
    graphroot: ""  # Default system location
    runroot: ""    # Default system location
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

### podman_registries_conf

Registry search and configuration:

```yaml
podman_registries_conf:
  unqualified-search-registries:
    - docker.io
    - quay.io
    - ghcr.io
```

### podman_registries_auth

Registry authentication format:

```yaml
podman_registries_auth:
  - registry: "docker.io"      # Hostname only
    username: "user"
    password: "{{ vault_password }}"
  
  - registry: "ghcr.io"
    username: "github-user"
    password: "{{ vault_github_token }}"
```

---

## Diagnostic Commands

### System Information

```bash
# Podman version and details
podman version

# Complete system info
podman info

# Storage driver
podman info --format '{{.Store.GraphDriverName}}'

# Runtime
podman info --format '{{.Host.OCIRuntime.Name}}'
```

### Storage

```bash
# Disk usage
podman system df

# Detailed disk usage
podman system df -v

# Storage location
podman info --format '{{.Store.GraphRoot}}'
```

### Containers

```bash
# All containers
podman ps -a

# Container details
podman inspect <container>

# Container logs
podman logs <container>
```

### Images

```bash
# List images
podman images

# Image details
podman inspect <image>

# Pull test
podman pull alpine
```

### User Namespaces

```bash
# Check subuid
cat /etc/subuid | grep $(whoami)

# Check subgid
cat /etc/subgid | grep $(whoami)

# Check user namespace
podman unshare cat /proc/self/uid_map
```

### Network

```bash
# List networks
podman network ls

# Network details
podman network inspect podman
```

### Cleanup

```bash
# Remove unused data
podman system prune -af

# Full reset (CAUTION: removes everything!)
podman system reset --force
```

---

## FAQ

### General

**Q: Podman vs Docker - can I use both?**
A: Yes! They use different storage. Run `docker` and `podman` commands independently.

**Q: Is Podman compatible with Docker Compose?**
A: Yes! Use `podman-compose` or `podman compose` (v4+).

**Q: Can I use Docker images with Podman?**
A: Yes, Podman pulls from Docker Hub by default. Use `podman pull docker.io/nginx`.

### Rootless

**Q: Why can't I bind to port 80?**
A: Ports < 1024 require root. Use `podman_allow_unprivileged_ports: true` or use port 8080.

**Q: Rootless containers are slow?**
A: Check if `fuse-overlayfs` is installed and `metacopy=on` is enabled.

**Q: How many containers per user?**
A: Depends on subuid/subgid range. Default 65536 allows thousands of containers.

### Storage

**Q: Where are images stored?**
A: Rootless: `~/.local/share/containers/storage/`. Root: `/var/lib/containers/storage/`.

**Q: How to use SSD for storage?**
A: Set `podman_storage_conf.storage.graphroot: "/ssd/podman/storage"`.

**Q: "No space left on device" but disk has space?**
A: Check inodes: `df -i`. Overlay driver creates many files.

### Troubleshooting

**Q: "permission denied" everywhere?**
A: Run `podman system reset --force` and re-run the Ansible role.

**Q: Login works but pull fails?**
A: Check registry URL format. Podman uses hostname only (`docker.io`), not full URL.

**Q: Changes not taking effect?**
A: Restart user session or run `systemctl --user daemon-reload`.

---

## External Resources

### Official Documentation

- [Podman Official Docs](https://docs.podman.io/)
- [Podman Troubleshooting](https://github.com/containers/podman/blob/main/troubleshooting.md)
- [Rootless Podman Guide](https://github.com/containers/podman/blob/main/rootless.md)

### Collections

- [containers.podman Collection](https://docs.ansible.com/ansible/latest/collections/containers/podman/index.html)
- [podman_login Module](https://docs.ansible.com/ansible/latest/collections/containers/podman/podman_login_module.html)

### Community

- [Podman GitHub Issues](https://github.com/containers/podman/issues)
- [Podman Discussions](https://github.com/containers/podman/discussions)
- [Buildah](https://buildah.io/)
- [Skopeo](https://github.com/containers/skopeo)

---

## Getting Help

If you encounter issues not covered here:

1. **Check logs:** `journalctl --user -xe`
2. **Run diagnostics:** See [Quick Diagnostics](#quick-diagnostics)
3. **Search issues:** [Podman GitHub Issues](https://github.com/containers/podman/issues)
4. **Open issue:** [ansible-col-devtools Issues](https://github.com/kode3tech/ansible-col-devtools/issues)

---

[← Back to Podman Documentation](README.md) | [Previous: Performance & Security](07-performance-security.md)
