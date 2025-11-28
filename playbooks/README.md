# Example Playbooks

This directory contains example playbooks demonstrating how to use the roles in this collection.

## 📁 Structure

Playbooks are organized by role:

```
playbooks/
├── docker/                           # Docker role examples
│   └── install-docker.yml           # Production Docker installation
├── podman/                           # Podman role examples
│   └── install-podman.yml           # Production Podman installation
└── asdf/                             # asdf role examples
    ├── install-asdf.yml             # Basic asdf installation
    ├── setup-nodejs-python.yml      # Node.js and Python configuration
    └── setup-multi-user.yml         # Multi-user setup
```

## 🎯 Organization Principle

- **Role-specific playbooks** → `playbooks/{role}/` - Examples using a single role

## 📚 Available Examples

### 🐳 Docker Examples (`docker/`)

#### [install-docker.yml](docker/install-docker.yml)
Production-ready Docker installation with performance optimizations and comprehensive configuration.

**Features:**
- Custom data directory (`/opt/docker-data`) for SSD optimization
- overlay2 storage driver with optimized settings
- High concurrency downloads (25 parallel)
- Non-blocking logging with compression
- Live restore for zero-downtime updates
- Prometheus metrics endpoint
- Time synchronization (critical for GPG keys)
- BuildKit enabled for faster builds
- Full validation and performance testing

**Usage:**
```bash
ansible-playbook playbooks/docker/install-docker.yml -i inventory
```

### 🦭 Podman Examples (`podman/`)

#### [install-podman.yml](podman/install-podman.yml)
Production-ready Podman installation with performance optimizations, rootless support, and comprehensive validation tests.

**Features:**
- crun runtime (20-30% faster than runc)
- Custom storage directory with metacopy optimization
- Rootless mode with unprivileged user testing
- Registry authentication support (via Ansible Vault)
- Container pull/run validation tests

**Usage:**
```bash
ansible-playbook playbooks/podman/install-podman.yml -i inventory
```

### 🔧 asdf Examples (`asdf/`)

#### [install-asdf.yml](asdf/install-asdf.yml)
Basic asdf installation without plugins.

**Usage:**
```bash
ansible-playbook playbooks/asdf/install-asdf.yml -i inventory
```

#### [setup-nodejs-python.yml](asdf/setup-nodejs-python.yml)
Install asdf with Node.js and Python plugins for development.

**Usage:**
```bash
ansible-playbook playbooks/asdf/setup-nodejs-python.yml -i inventory
```

#### [setup-multi-user.yml](asdf/setup-multi-user.yml)
Configure asdf for multiple users with different plugin requirements.

**Usage:**
```bash
ansible-playbook playbooks/asdf/setup-multi-user.yml -i inventory
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

1. **Start here:** [docker/install-docker.yml](docker/install-docker.yml) - Production Docker setup
2. **Then try:** [podman/install-podman.yml](podman/install-podman.yml) - Production Podman setup
3. **For development tools:** [asdf/install-asdf.yml](asdf/install-asdf.yml) - Version manager setup

## 📝 Creating Your Own Playbooks

When creating new example playbooks:

- **Single role examples** → Place in `playbooks/{role}/`
- **Always include:**
  - Clear comments explaining the example
  - Variable examples with descriptions
  - Tags for selective execution
  - Proper error handling

## 🔗 Related Documentation

- [Docker Complete Guide](../docs/user-guides/DOCKER_COMPLETE_GUIDE.md)
- [Podman Complete Guide](../docs/user-guides/PODMAN_COMPLETE_GUIDE.md)
- [Docker Role README](../roles/docker/README.md)
- [Podman Role README](../roles/podman/README.md)
- [Registry Authentication Guide](../docs/user-guides/REGISTRY_AUTHENTICATION.md)
- [Collection README](../README.md)

---

**Need help?** [Open an issue](https://github.com/kode3tech/ansible-col-devtools/issues) or check the [FAQ](../docs/FAQ.md).
