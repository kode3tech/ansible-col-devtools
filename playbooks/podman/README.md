# Podman Role - Example Playbooks

Example playbooks demonstrating Podman role usage.

## 📋 Available Examples

### [install-podman.yml](install-podman.yml)
**Purpose:** Basic Podman installation with rootless support.

**What it does:**
- Installs Podman, Buildah, and Skopeo
- Configures rootless mode
- Sets up user namespaces
- Configures storage and registry settings

**Usage:**
```bash
ansible-playbook playbooks/podman/install-podman.yml -i inventory
```

---

### [test-podman-auth.yml](test-podman-auth.yml)
**Purpose:** Test Podman registry authentication and troubleshoot issues.

**What it does:**
- Installs Podman
- Configures registry authentication
- Tests authentication with actual login attempts
- Verifies XDG_RUNTIME_DIR configuration
- Troubleshoots common authentication issues

**Usage:**
```bash
ansible-playbook playbooks/podman/test-podman-auth.yml -i inventory
```

**Variables required:**
```yaml
podman_registries_auth:
  - registry: "docker.io"
    username: "myuser"
    password: "{{ vault_password }}"  # Use Ansible Vault!
```

**What it tests:**
- ✅ XDG_RUNTIME_DIR exists and is writable
- ✅ Authentication credentials are stored correctly
- ✅ Login to configured registries works
- ✅ No XDG-related warnings appear

---

## 🎯 Quick Start

1. **Choose an example** that matches your needs
2. **Copy the playbook** and customize variables
3. **Run the playbook:**
   ```bash
   ansible-playbook playbooks/podman/<example>.yml -i inventory
   ```

## 🔧 Common Issues

### XDG_RUNTIME_DIR Warnings
If you see warnings about XDG_RUNTIME_DIR:
- See [Podman XDG Runtime Fix](../../roles/podman/docs/PODMAN_XDG_RUNTIME_FIX.md)
- The role automatically creates required directories

### Authentication Failures
If authentication fails:
- Verify credentials are correct
- Check [Registry Authentication Guide](../../docs/user-guides/REGISTRY_AUTHENTICATION.md)
- Use `test-podman-auth.yml` to diagnose issues

## 📚 Related Documentation

- [Podman Role README](../../roles/podman/README.md)
- [Podman XDG Runtime Fix](../../roles/podman/docs/PODMAN_XDG_RUNTIME_FIX.md)
- [Registry Authentication Guide](../../docs/user-guides/REGISTRY_AUTHENTICATION.md)
- [Troubleshooting](../../docs/troubleshooting/)

---

[← Back to Playbooks](../README.md)
