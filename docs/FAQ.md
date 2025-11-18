# Frequently Asked Questions (FAQ)

Common questions about using the `kode3tech.devtools` Ansible Collection.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Docker Questions](#docker-questions)
- [Podman Questions](#podman-questions)
- [asdf Questions](#asdf-questions)
- [Performance & Optimization](#performance--optimization)
- [Troubleshooting](#troubleshooting)
- [Migration & Upgrades](#migration--upgrades)

---

## General Questions

### What is this collection for?

The `kode3tech.devtools` collection automates the installation and configuration of essential DevOps tools (Docker, Podman, asdf) across Ubuntu, Debian, and RHEL-based systems with production-ready optimizations.

### Which distributions are supported?

- **Ubuntu**: 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- **Debian**: 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- **RHEL/CentOS/Rocky/AlmaLinux**: 9, 10

### What Ansible version is required?

Ansible >= 2.15 (ansible-core >= 2.15)

### Is this collection production-ready?

Yes! All roles include:
- ✅ Production-ready optimizations
- ✅ Comprehensive testing (Molecule + Pytest)
- ✅ Multi-platform support
- ✅ Security best practices

---

## Installation & Setup

### How do I install the collection?

```bash
# From Ansible Galaxy (when published)
ansible-galaxy collection install kode3tech.devtools

# From source
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools
source activate.sh
ansible-galaxy collection build
ansible-galaxy collection install kode3tech-devtools-*.tar.gz
```

### Do I need to install dependencies?

Yes! Install the required collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

This installs:
- `community.docker` >= 3.4.0 (for Docker registry authentication)
- `containers.podman` >= 1.10.0 (for Podman registry authentication)

### Why do I need to activate a virtual environment?

The collection uses specific versions of Ansible, Molecule, and testing tools. The virtual environment ensures consistency:

```bash
source activate.sh
```

Always activate before running Ansible commands!

---

## Docker Questions

### How do I update Docker installed by this role?

The role installs Docker from official repositories. To update:

**Option 1: Re-run the playbook** (safest)
```bash
ansible-playbook -i inventory playbooks/docker/install-docker.yml
```

**Option 2: Manual update**
```bash
# On target hosts
sudo apt update && sudo apt upgrade docker-ce docker-ce-cli containerd.io
# or
sudo dnf update docker-ce docker-ce-cli containerd.io
```

### Can I customize Docker daemon configuration?

Yes! Use the `docker_daemon_config` variable:

```yaml
docker_daemon_config:
  log-driver: "json-file"
  log-opts:
    max-size: "20m"
    max-file: "5"
  storage-driver: "overlay2"
  # Add any valid daemon.json configuration
```

The role merges your settings with performance defaults.

### How do I add users to the docker group?

Use the `docker_users` variable:

```yaml
docker_users:
  - myuser
  - jenkins
  - ci-user
```

**Note:** Users must log out and back in for group changes to take effect.

### Does the role install Docker Compose?

Yes! Docker Compose is installed automatically as part of the `docker-ce` package (Compose V2, integrated with Docker CLI).

### What performance optimizations are included?

See the [Performance Tuning](../roles/docker/README.md#performance-tuning) section. Key optimizations:
- overlay2 storage driver (+15-30% I/O)
- BuildKit enabled (+50-200% faster builds)
- Parallel downloads (+200-300% faster pulls)
- Compressed logs (-70% disk space)
- crun runtime (+20-30% faster startup)

---

## Podman Questions

### Can I use Docker and Podman on the same host?

Yes! Docker and Podman can coexist. They use different:
- Storage paths: `/var/lib/docker` vs `/var/lib/containers`
- Sockets: `/var/run/docker.sock` vs Podman uses no daemon
- Configuration: `/etc/docker/` vs `/etc/containers/`

However, be aware of:
- Port conflicts if both try to use the same ports
- Resource competition (CPU, memory, disk I/O)

### How does rootless Podman work?

When `podman_enable_rootless: true`:
- Each user has their own container storage
- No daemon required
- Uses user namespaces and subuid/subgid
- Storage in `~/.local/share/containers/storage`

Configure with:
```yaml
podman_enable_rootless: true
podman_rootless_users:
  - myuser
  - developer
```

### How do I authenticate to private registries with Podman?

Use `podman_registries_auth`:

```yaml
podman_registries_auth:
  - registry_url: "quay.io"
    username: "myuser"
    password: "{{ vault_password }}"
```

For rootless mode, authentication is per-user (stored in `~/.local/share/containers/auth.json`).

### What is crun and why use it?

`crun` is a lightweight, fast OCI runtime written in C (vs Go for runc):
- 20-30% faster container startup
- 30-50% lower memory footprint
- Better performance in LXC containers

The role installs and configures crun automatically.

### I get "XDG_RUNTIME_DIR not found" - how do I fix it?

The role automatically fixes this! It configures systemd-tmpfiles to create `/run/user/0` for root Podman.

If you still see issues, check the [Podman XDG Runtime Fix](../roles/podman/docs/PODMAN_XDG_RUNTIME_FIX.md) guide.

---

## asdf Questions

### What is asdf?

asdf is an extendable version manager that lets you manage multiple runtime versions for Node.js, Python, Ruby, Golang, and 300+ other tools - all with a single CLI.

### How is asdf installed?

The role uses **binary installation** (v0.16.0+):
- Downloads official release from GitHub
- Fast (~10-20 seconds)
- No git clone required
- System-wide installation in `/opt/asdf`

### Which plugins should I install?

**For testing/CI (fast ~10-30s):**
- direnv, jq, yq, kubectl, helm

**For development (slow ~2-30min):**
- nodejs, python, ruby, golang, rust

See [Plugin Recommendations](../roles/asdf/README.md#plugin-recommendations).

### How do I install Node.js with asdf?

```yaml
asdf_users:
  - name: "myuser"
    shell: "bash"
    plugins:
      - name: "nodejs"
        versions:
          - "20.11.0"
          - "18.19.0"
        global: "20.11.0"
```

### Can I use asdf for multiple users?

Yes! Each user can have different plugins and versions:

```yaml
asdf_users:
  - name: "frontend"
    plugins:
      - name: "nodejs"
        versions: ["20.11.0"]
        global: "20.11.0"
  
  - name: "backend"
    plugins:
      - name: "python"
        versions: ["3.12.1"]
        global: "3.12.1"
```

### Where are asdf plugins installed?

- **asdf installation**: `/opt/asdf`
- **User plugins**: `~/.asdf/` (per user)
- **Global versions**: `~/.tool-versions`

### How do I update asdf?

Re-run the playbook with a newer version:

```yaml
asdf_version: "v0.18.0"  # or "latest"
```

---

## Performance & Optimization

### What performance gains can I expect?

**Docker:**
- Build speed: +50-200%
- I/O performance: +15-30%
- Pull speed: +200-300%
- Container startup: +20-30% (with crun)

**Podman:**
- I/O performance: +30-50%
- Container startup: +20-30% (with crun)
- Pull speed: +200-300%

**Note:** Gains are for production hosts. Molecule tests (DinD) show different performance.

### Why don't I see these performance gains in Molecule tests?

Molecule runs Docker/Podman inside Docker (DinD), which has limitations:
- Uses `vfs` storage driver instead of `overlay2`
- Significant overhead
- ~30-40% of native performance

**Molecule validates configuration**, not performance. Test performance on real hosts!

### Can I use these roles in LXC containers?

Yes! But requires LXC configuration:

```
# /etc/pve/lxc/XXX.conf
features: nesting=1
lxc.apparmor.profile: unconfined
```

See [LXC Troubleshooting](troubleshooting/TROUBLESHOOTING_LXC.md) for details.

### What is the recommended storage driver?

- **Docker**: `overlay2` (configured by default)
- **Podman**: `overlay` with `metacopy=on` (configured by default)

Both provide the best I/O performance on modern kernels.

---

## Troubleshooting

### Docker/Podman won't start in LXC - what's wrong?

**Symptoms:**
```
Error: socket: permission denied
Error: failed to create shim task
```

**Solution:**
Add to LXC config and restart:
```
features: nesting=1
lxc.apparmor.profile: unconfined
```

See [LXC Troubleshooting](troubleshooting/TROUBLESHOOTING_LXC.md).

### I get "apt-key is deprecated" warnings on Debian/Ubuntu

This is expected! The role uses modern GPG key management:
- Keys stored in `/etc/apt/keyrings/`
- No more `apt-key` usage
- Fully compatible with Debian 12+

See [APT Key Deprecation](troubleshooting/APT_KEY_DEPRECATION.md).

### Podman shows DNS errors on Ubuntu 24.04

Known issue with AppArmor. Workarounds:
1. Use rootless mode
2. Configure manually: `sudo podman login`
3. Disable AppArmor for Podman (not recommended for production)

See [Known Issues](troubleshooting/KNOWN_ISSUES.md#podman-registry-login---ubuntu-2404-dns-permission-issue).

### How do I debug role execution?

**Increase verbosity:**
```bash
ansible-playbook -vvv playbook.yml
```

**Check logs:**
```bash
# Docker
sudo journalctl -u docker -n 50

# Podman
journalctl --user -u podman -n 50
```

**Validate configuration:**
```bash
# Docker
docker info
cat /etc/docker/daemon.json | jq

# Podman
podman info
cat /etc/containers/storage.conf
```

---

## Migration & Upgrades

### Can I migrate from manual Docker installation to this role?

Yes! The role is idempotent:
1. Detects existing installation
2. Updates configuration
3. Preserves containers and images

**Recommendation:** Backup first!

```bash
# Backup containers
docker export container_name > backup.tar

# Or use commit
docker commit container_name backup_image
```

### How do I migrate from Docker to Podman?

Migration requires planning:

1. **Rootless vs root:** Decide on Podman mode
2. **Images:** Pull images to Podman (`podman pull`)
3. **Volumes:** Migrate data manually
4. **Systemd units:** Convert docker.service to podman.service
5. **Docker Compose:** Use `podman-compose` or Kubernetes YAML

No automated migration tool yet. Consider running both during transition.

### How do I rollback if something breaks?

**Docker:**
```bash
# Remove Docker packages
sudo apt remove docker-ce docker-ce-cli containerd.io

# Or downgrade
sudo apt install docker-ce=<old-version>
```

**Podman:**
```bash
# Remove Podman
sudo apt remove podman buildah skopeo
```

**Important:** Containers and images are preserved in `/var/lib/docker` or `/var/lib/containers`.

### How do I upgrade between collection versions?

1. Check [CHANGELOG.md](../CHANGELOG.md) for breaking changes
2. Read [Upgrade Guide](maintenance/UPGRADE_GUIDE.md)
3. Update in `requirements.yml`:
   ```yaml
   collections:
     - name: kode3tech.devtools
       version: ">=1.1.0"
   ```
4. Reinstall:
   ```bash
   ansible-galaxy collection install -r requirements.yml --force
   ```

---

## Still Have Questions?

- 📖 Check the [User Guides](user-guides/)
- 🔧 Check [Troubleshooting](troubleshooting/)
- 🐛 Search [GitHub Issues](https://github.com/kode3tech/ansible-devtools/issues)
- 💬 Open a [Discussion](https://github.com/kode3tech/ansible-devtools/discussions)
- 📧 Email: suporte@kode3.tech

---

[← Back to Documentation Index](README.md)
