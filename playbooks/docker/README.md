# Docker Role - Example Playbooks

Example playbooks demonstrating Docker role usage.

## 📋 Available Examples

### [install-docker.yml](install-docker.yml)
**Purpose:** Basic Docker installation with minimal configuration.

**What it does:**
- Installs Docker Engine
- Configures Docker daemon
- Adds user to docker group
- Starts Docker service

**Usage:**
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory
```

---

### [setup-registry-auth.yml](setup-registry-auth.yml)
**Purpose:** Configure Docker with private registry authentication.

**What it does:**
- Installs Docker
- Configures authentication for private registries
- Supports multiple registries (Docker Hub, custom registries)
- Uses Ansible Vault for secure credential management

**Usage:**
```bash
ansible-playbook playbooks/docker/setup-registry-auth.yml -i inventory
```

**Variables required:**
```yaml
docker_registries_auth:
  - registry_url: "https://registry.example.com"
    username: "myuser"
    password: "{{ vault_password }}"  # Use Ansible Vault!
```

---

### [setup-insecure-registry.yml](setup-insecure-registry.yml)
**Purpose:** Configure Docker to work with insecure registries (HTTP or self-signed certificates).

**What it does:**
- Installs Docker
- Configures insecure registries in daemon.json
- Restarts Docker service
- Verifies configuration

**Usage:**
```bash
ansible-playbook playbooks/docker/setup-insecure-registry.yml -i inventory
```

**Variables required:**
```yaml
docker_insecure_registries:
  - "registry.internal.company.com:5000"
  - "localhost:5000"
```

**⚠️ Warning:** Only use insecure registries for trusted internal networks!

---

## 🎯 Quick Start

1. **Choose an example** that matches your needs
2. **Copy the playbook** and customize variables
3. **Run the playbook:**
   ```bash
   ansible-playbook playbooks/docker/<example>.yml -i inventory
   ```

## 📚 Related Documentation

- [Docker Role README](../../roles/docker/README.md)
- [Registry Authentication Guide](../../docs/user-guides/REGISTRY_AUTHENTICATION.md)
- [Troubleshooting](../../docs/troubleshooting/)

---

[← Back to Playbooks](../README.md)
