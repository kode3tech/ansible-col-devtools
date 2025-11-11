# Example Playbooks

This directory contains example playbooks demonstrating how to use the roles in this collection.

## 📁 Structure

Playbooks are organized by role:

```
playbooks/
├── docker/                           # Docker role examples
│   ├── install-docker.yml           # Basic Docker installation
│   ├── setup-registry-auth.yml      # Private registry authentication
│   └── setup-insecure-registry.yml  # Insecure registry configuration
└── podman/                           # Podman role examples
    ├── install-podman.yml           # Basic Podman installation
    └── test-podman-auth.yml         # Podman authentication testing
```

## 🎯 Organization Principle

- **Role-specific playbooks** → `playbooks/{role}/` - Examples using a single role

## 📚 Available Examples

### 🐳 Docker Examples (`docker/`)

#### [install-docker.yml](docker/install-docker.yml)
Basic Docker installation with minimal configuration.

**Usage:**
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory
```

#### [setup-registry-auth.yml](docker/setup-registry-auth.yml)
Configure Docker with private registry authentication.

**Usage:**
```bash
ansible-playbook playbooks/docker/setup-registry-auth.yml -i inventory
```

#### [setup-insecure-registry.yml](docker/setup-insecure-registry.yml)
Configure Docker with insecure registries (HTTP or self-signed certificates).

**Usage:**
```bash
ansible-playbook playbooks/docker/setup-insecure-registry.yml -i inventory
```

### 🦭 Podman Examples (`podman/`)

#### [install-podman.yml](podman/install-podman.yml)
Basic Podman installation with rootless support.

**Usage:**
```bash
ansible-playbook playbooks/podman/install-podman.yml -i inventory
```

#### [test-podman-auth.yml](podman/test-podman-auth.yml)
Test Podman registry authentication and troubleshoot issues.

**Usage:**
```bash
ansible-playbook playbooks/podman/test-podman-auth.yml -i inventory
```

## 🔧 Prerequisites

Before running playbooks:

1. **Activate virtual environment:**
   ```bash
   source activate.sh
   ```

2. **Install collection dependencies:**
   ```bash
   ansible-galaxy collection install -r requirements.yml
   ```

3. **Create inventory file:**
   ```bash
   cp inventory.example inventory
   # Edit inventory with your hosts
   ```

## 📖 Usage Tips

### Running a specific playbook
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory
```

### Dry-run (check mode)
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory --check
```

### Run with specific tags
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory --tags docker
```

### Verbose output
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory -v
```

## 🎓 Learning Path

1. **Start here:** [docker/install-docker.yml](docker/install-docker.yml) - Basic Docker setup
2. **Then try:** [podman/install-podman.yml](podman/install-podman.yml) - Basic Podman setup
3. **Advanced:** [docker/setup-registry-auth.yml](docker/setup-registry-auth.yml) - Private registries

## 📝 Creating Your Own Playbooks

When creating new example playbooks:

- **Single role examples** → Place in `playbooks/{role}/`
- **Always include:**
  - Clear comments explaining the example
  - Variable examples with descriptions
  - Tags for selective execution
  - Proper error handling

## 🔗 Related Documentation

- [Docker Role README](../roles/docker/README.md)
- [Podman Role README](../roles/podman/README.md)
- [Registry Authentication Guide](../docs/user-guides/REGISTRY_AUTHENTICATION.md)
- [Collection README](../README.md)

---

**Need help?** Check the [troubleshooting guide](../docs/troubleshooting/) or [open an issue](https://github.com/kode3tech/ansible-col-devtools/issues).
