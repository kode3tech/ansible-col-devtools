# Podman Role - Example Playbooks

Example playbooks demonstrating Podman role usage.

> 📖 **Complete Guide**: For comprehensive Podman documentation including Root vs Rootless mode, detailed variable explanations, and production deployment, see the **[Podman Complete Guide](../../docs/user-guides/podman/)**.

## 📋 Available Examples

### [install-podman.yml](install-podman.yml) ⭐ PRODUCTION READY
**Purpose:** Complete production-ready Podman installation with performance optimizations.

**What it does:**
- Installs Podman, Buildah, Skopeo, and crun (high-performance runtime)
- Configures rootless mode with user namespace support
- Creates unprivileged test user for rootless validation
- Sets up custom storage directory (`/opt/podman-data`)
- Applies performance optimizations:
  - `crun` runtime (20-30% faster than runc)
  - `metacopy=on` storage option (+30-50% I/O performance)
  - Parallel downloads (10 concurrent layers)
- Validates installation with container pull/run tests
- Tests both privileged and unprivileged user rootless mode

**Key Features:**
- ✅ Time synchronization for GPG key validation
- ✅ Custom storage directory (SSD-ready)
- ✅ Rootless mode with unprivileged user testing
- ✅ Performance-optimized configuration
- ✅ Comprehensive validation tests
- ✅ Registry authentication support (via Ansible Vault)

**Usage:**
```bash
# Basic usage
ansible-playbook playbooks/podman/install-podman.yml -i inventory

# With custom users
ansible-playbook playbooks/podman/install-podman.yml -i inventory \
  -e '{"podman_rootless_users": ["deploy", "jenkins"]}'

# With registry authentication (using vault)
ansible-playbook playbooks/podman/install-podman.yml -i inventory \
  --ask-vault-pass
```

**Variables you can customize:**
```yaml
# Add users to rootless mode
podman_rootless_users:
  - "{{ ansible_user }}"
  - "deploy"
  - "jenkins"

# Registry authentication (use Ansible Vault!)
podman_registries_auth:
  - registry: "docker.io"
    username: "your-username"
    password: "{{ vault_dockerhub_token }}"

# Insecure registries (internal networks only)
podman_insecure_registries:
  - "registry.internal.company.com:5000"
```

---

## 🎯 Quick Start

1. **Choose an example** that matches your needs
2. **Copy the playbook** and customize variables
3. **Create vault file** for registry credentials (if needed):
   ```bash
   ansible-vault create vars/registry_secrets.yml
   # Add: vault_dockerhub_token: "your-token"
   ```
4. **Run the playbook:**
   ```bash
   ansible-playbook playbooks/podman/install-podman.yml -i inventory
   ```

## 🔧 Common Customizations

### Add Rootless Users
```yaml
podman_rootless_users:
  - developer
  - jenkins
  - ciuser
```

### Configure Registry Authentication
```yaml
# vars/registry_secrets.yml (encrypted with ansible-vault)
vault_dockerhub_token: "dckr_pat_xxxxx"
vault_github_token: "ghp_xxxxx"

# In playbook
podman_registries_auth:
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_dockerhub_token }}"
```

### Change Storage Location
```yaml
podman_storage_conf:
  storage:
    graphroot: "/data/podman/storage"  # Your custom path
```

## 🔍 Troubleshooting

### XDG_RUNTIME_DIR Warnings
If you see warnings about XDG_RUNTIME_DIR:
- See [XDG Runtime Directory Configuration](../../roles/podman/README.md#xdg-runtime-directory-configuration)
- The role automatically creates required directories

### Authentication Failures
If authentication fails:
- Verify credentials are correct
- Check [Podman Registry Authentication](../../docs/user-guides/podman/04-registry-auth.md)
- Enable `podman_clean_credentials: true` to clear old credentials

### Storage Driver Conflicts
If you see "database graph driver mismatch" errors:
- Set `podman_reset_storage_on_driver_change: true` (⚠️ deletes containers/images)
- See [Podman Guide - Troubleshooting](../../docs/user-guides/podman/08-troubleshooting.md)

## 📚 Related Documentation

- [Podman Complete Guide](../../docs/user-guides/podman/) - **Comprehensive 8-part documentation**
- [Podman Role README](../../roles/podman/README.md)
- [XDG Runtime Directory Configuration](../../roles/podman/README.md#xdg-runtime-directory-configuration)

---

[← Back to Playbooks](../README.md)
