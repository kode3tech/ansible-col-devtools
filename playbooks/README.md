# Example Playbooks

This directory contains example playbooks demonstrating how to use the roles in this collection.

## 📁 Structure

Playbooks are organized by role:

```
playbooks/
├── azure_devops_agents/              # Azure DevOps agents examples
│   ├── install-production.yml       # Production deployment (recommended)
│   ├── install-single-agent.yml     # Basic single agent
│   ├── install-multi-agent.yml      # Multiple agents per host
│   └── install-deployment-group.yml # Deployment group agents
├── github_actions_runners/           # GitHub Actions runners examples
│   ├── install-production.yml       # Production deployment (recommended)
│   ├── install-single-runner.yml    # Basic single runner
│   └── install-multi-runner.yml     # Multiple runners per host
├── docker/                           # Docker role examples
│   └── install-docker.yml           # Production Docker installation
├── podman/                           # Podman role examples
│   └── install-podman.yml           # Production Podman installation
└── asdf/                             # asdf role examples
    ├── install-asdf.yml             # Basic asdf installation
    ├── install-asdf-basic.yml       # Quick testing (lightweight plugins)
    ├── install-asdf-full.yml        # Full installation (Node.js + Python)
    ├── setup-nodejs-python.yml      # Node.js and Python configuration
    ├── setup-multi-user.yml         # Multi-user setup
    └── setup-multi-shell.yml        # Multi-shell configuration
```

## 🎯 Organization Principle

- **Role-specific playbooks** → `playbooks/{role}/` - Examples using a single role

## 📚 Available Examples

### ☁️ Azure DevOps Agents Examples (`azure_devops_agents/`)

#### [install-production.yml](azure_devops_agents/install-production.yml) ⭐ **RECOMMENDED**
Production-ready Azure DevOps agent deployment with time synchronization, vault integration, and service verification.

**Features:**
- Time synchronization verification (critical for OAuth)
- Vault-based credential management
- Azure DevOps connectivity validation
- Service verification post-deployment
- Support for all agent types (self-hosted, deployment-group, environment)

**Usage:**
```bash
ansible-playbook playbooks/azure_devops_agents/install-production.yml \
  -i inventory --ask-vault-pass -e "azure_org=myorganization"
```

#### [install-single-agent.yml](azure_devops_agents/install-single-agent.yml)
Basic installation of a single self-hosted agent.

#### [install-multi-agent.yml](azure_devops_agents/install-multi-agent.yml)
Deploy multiple agents (different types) on the same host.

#### [install-deployment-group.yml](azure_devops_agents/install-deployment-group.yml)
Configure deployment group agents for Classic Release pipelines.

See [Azure DevOps Agents README](azure_devops_agents/README.md) for details.

### 🐙 GitHub Actions Runners Examples (`github_actions_runners/`)

#### [install-production.yml](github_actions_runners/install-production.yml) ⭐ **RECOMMENDED**
Production-ready GitHub Actions runner deployment with comprehensive validation, error handling, and verification.

**Features:**
- Pre-flight validation (variables, API connectivity)
- Vault-based credential management
- Service verification post-deployment
- Support for all scopes (organization, repository, enterprise)

**Usage:**
```bash
ansible-playbook playbooks/github_actions_runners/install-production.yml \
  -i inventory --ask-vault-pass
```

#### [install-single-runner.yml](github_actions_runners/install-single-runner.yml)
Basic installation of a single self-hosted runner.

#### [install-multi-runner.yml](github_actions_runners/install-multi-runner.yml)
Deploy multiple runners per host for CI/CD farms.

See [GitHub Actions Runners README](github_actions_runners/README.md) for details.

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

#### [install-asdf-basic.yml](asdf/install-asdf-basic.yml) ⚡ **RECOMMENDED FOR TESTING**
Quick installation with lightweight plugins (direnv, jq, yq) - Fast installation (~15-30 seconds).

**Features:**
- Lightweight plugins (no compilation needed)
- Fast installation for testing and CI/CD
- Centralized group-based architecture
- Full validation tests

**Usage:**
```bash
ansible-playbook playbooks/asdf/install-asdf-basic.yml -i inventory
```

#### [install-asdf-full.yml](asdf/install-asdf-full.yml)
Full installation with Node.js and Python plugins for production environments.

**Features:**
- Heavy plugins (requires compilation ~5-15 minutes)
- Multiple versions per plugin
- Full development stack

**Usage:**
```bash
ansible-playbook playbooks/asdf/install-asdf-full.yml -i inventory
```

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
Configure asdf for multiple users with same plugin configuration.

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
3. **For CI/CD agents:** [azure_devops_agents/install-production.yml](azure_devops_agents/install-production.yml) - Azure DevOps agents
4. **For development tools:** [asdf/install-asdf.yml](asdf/install-asdf.yml) - Version manager setup

## 📝 Creating Your Own Playbooks

When creating new example playbooks:

- **Single role examples** → Place in `playbooks/{role}/`
- **Always include:**
  - Clear comments explaining the example
  - Variable examples with descriptions
  - Tags for selective execution
  - Proper error handling

## 🔗 Related Documentation

- [Azure DevOps Agents Complete Guide](../docs/user-guides/azure-devops-agents/)
- [Docker Complete Guide](../docs/user-guides/docker/)
- [Podman Complete Guide](../docs/user-guides/podman/)
- [asdf Complete Guide](../docs/user-guides/asdf/)
- [Azure DevOps Agents Role README](../roles/azure_devops_agents/README.md)
- [Docker Role README](../roles/docker/README.md)
- [Podman Role README](../roles/podman/README.md)
- [asdf Role README](../roles/asdf/README.md)
- [Collection README](../README.md)

---

**Need help?** [Open an issue](https://github.com/kode3tech/ansible-col-devtools/issues) or check the [FAQ](../docs/FAQ.md).
