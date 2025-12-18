# Ansible Collection: code3tech.devtools

[![CI](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/ci.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/ci.yml)
[![Sanity](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/sanity.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/sanity.yml)
[![Release](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/release.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/release.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-code3tech.devtools-blue.svg)](https://galaxy.ansible.com/ui/repo/published/code3tech/devtools/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Ansible](https://img.shields.io/badge/ansible-2.15%2B-blue.svg)](https://www.ansible.com/)

Ansible Collection for DevOps tools installation and configuration. This collection provides production-ready roles for managing containerization and development tools across Ubuntu, Debian, and RHEL-based systems.

## 📋 Table of Contents

- [Included Roles](#-included-roles)
- [Quick Start](#-quick-start)
- [Requirements](#-requirements)
- [Example Playbooks](#-example-playbooks)
- [Role Documentation](#-role-documentation)
- [Development](#-development)
- [Contributing](#-contributing)

---

## 📦 Included Roles

### ☁️ Azure DevOps Agents
Deploy and manage Azure DevOps self-hosted agents on Linux servers.
- Multi-agent support: N agents per host with isolated directories
- Three agent types: Self-hosted, Deployment Group, Environment
- Auto-create resources: Automatically create Deployment Groups and Environments
- Open access: Configure pipeline permissions for environments
- Service verification: Ensures all services are enabled and running
- Agent removal: Clean unregistration and removal

### 🐙 GitHub Actions Runners ⭐ NEW
Deploy and manage GitHub Actions self-hosted runners on Linux servers.
- Multi-runner support: N runners per host with isolated directories
- Three scopes: Organization, Repository, Enterprise
- Label management: Automatic label assignment and updates via REST API
- Runner groups: Create and assign runners to groups
- Ephemeral runners: Support for single-use runners
- Service verification: Ensures all services are enabled and running

### 🦊 GitLab CI Runners ⭐ NEW
Deploy and manage GitLab CI self-hosted runners on Linux servers.
- Multi-runner support: N runners per host with isolated directories
- Three runner types: Instance, Group, Project runners
- API-based management: Create, update, and delete runners via GitLab API
- Tag management: Dynamic tag updates without re-registration
- Advanced features: run_untagged, locked, access_level configuration
- Service verification: Ensures all services are enabled and running

### 🐳 Docker
Complete Docker Engine installation and configuration with Docker Compose support.
- Multi-platform: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
- Registry authentication with automatic permission handling
- BuildKit enabled by default for faster builds
- Optimized logging and storage configuration

### 🦭 Podman
Podman installation with rootless container support.
- Daemonless container engine (no Docker daemon required)
- Enhanced rootless support with per-user authentication
- Complete toolchain: Buildah and Skopeo included
- OCI-compliant and Docker command compatible

### 🔧 asdf
asdf version manager with centralized group-based architecture.
- Centralized plugin management for all users
- Group-based permissions with `asdf` group
- 300+ plugins: Node.js, Python, Ruby, Golang, Terraform, and more
- Shell integration for bash, zsh, and fish

---

## 🚀 Quick Start

### Installation from Ansible Galaxy

```bash
# Install the collection
ansible-galaxy collection install code3tech.devtools

# Install required dependencies
ansible-galaxy collection install community.docker containers.podman
```

### Installation from Source

```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment
source activate.sh

# Build and install locally
make install-collection
```

### Your First Playbook

Create a playbook `setup.yml`:

```yaml
---
- name: Setup container environment
  hosts: all
  become: true

  collections:
    - code3tech.devtools

  vars:
    docker_users:
      - myuser

  roles:
    - docker
```

Run it:

```bash
ansible-playbook setup.yml -i your_inventory
```

---

## 📋 Requirements

| Requirement | Version |
|-------------|---------|
| Ansible | >= 2.15 |
| Python | >= 3.9 |
| Target OS | Ubuntu 22.04+, Debian 11+, RHEL 9+ |

### Required Collections

```bash
ansible-galaxy collection install -r requirements.yml
```

Dependencies:
- `community.docker` >= 3.4.0 (Docker registry authentication)
- `containers.podman` >= 1.10.0 (Podman registry authentication)

### Supported Distributions

| Distribution | Versions |
|--------------|----------|
| **Ubuntu** | 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky) |
| **Debian** | 11 (Bullseye), 12 (Bookworm), 13 (Trixie) |
| **RHEL/Rocky/Alma** | 9, 10 |

---

## 📖 Example Playbooks

The collection includes ready-to-use example playbooks in the `playbooks/` directory:

### Azure DevOps Agents

| Playbook | Description |
|----------|-------------|
| [install-production.yml](playbooks/azure_devops_agents/install-production.yml) | ⭐ Production deployment with validation |
| [install-single-agent.yml](playbooks/azure_devops_agents/install-single-agent.yml) | Basic single agent installation |
| [install-multi-agent.yml](playbooks/azure_devops_agents/install-multi-agent.yml) | Multiple agents per host |

### GitHub Actions Runners

| Playbook | Description |
|----------|-------------|
| [install-production.yml](playbooks/github_actions_runners/install-production.yml) | ⭐ Production deployment with validation |
| [install-single-runner.yml](playbooks/github_actions_runners/install-single-runner.yml) | Basic single runner installation |
| [install-multi-runner.yml](playbooks/github_actions_runners/install-multi-runner.yml) | Multiple runners per host |

### GitLab CI Runners

| Playbook | Description |
|----------|-------------|
| [install-production.yml](playbooks/gitlab_ci_runners/install-production.yml) | ⭐ Production deployment with all features and comprehensive validation |

### Docker

| Playbook | Description |
|----------|-------------|
| [install-docker.yml](playbooks/docker/install-docker.yml) | Production Docker installation with optimizations |

### Podman

| Playbook | Description |
|----------|-------------|
| [install-podman.yml](playbooks/podman/install-podman.yml) | Production Podman installation with rootless support |

### asdf

| Playbook | Description |
|----------|-------------|
| [install-asdf-basic.yml](playbooks/asdf/install-asdf-basic.yml) | Quick install with lightweight plugins (direnv, jq) |
| [install-asdf-full.yml](playbooks/asdf/install-asdf-full.yml) | Full installation with Node.js and Python |
| [setup-multi-user.yml](playbooks/asdf/setup-multi-user.yml) | Multi-user configuration |

### Running Examples

```bash
# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Run a playbook
ansible-playbook playbooks/docker/install-docker.yml -i your_inventory
```

See [playbooks/README.md](playbooks/README.md) for complete documentation.

---

## 📚 Role Documentation

| Role | README | Complete Guide |
|------|--------|----------------|
| **Azure DevOps Agents** | [roles/azure_devops_agents/README.md](roles/azure_devops_agents/README.md) | [Azure DevOps Agents Guide](docs/user-guides/azure-devops-agents/) |
| **GitHub Actions Runners** | [roles/github_actions_runners/README.md](roles/github_actions_runners/README.md) | [GitHub Actions Runners Guide](docs/user-guides/github-actions-runners/) |
| **GitLab CI Runners** | [roles/gitlab_ci_runners/README.md](roles/gitlab_ci_runners/README.md) | [GitLab CI Runners Guide](docs/user-guides/gitlab-ci-runners/) |
| **Docker** | [roles/docker/README.md](roles/docker/README.md) | [Docker Complete Guide](docs/user-guides/docker/) |
| **Podman** | [roles/podman/README.md](roles/podman/README.md) | [Podman Complete Guide](docs/user-guides/podman/) |
| **asdf** | [roles/asdf/README.md](roles/asdf/README.md) | [asdf Complete Guide](docs/user-guides/asdf/) |

### Additional Resources

- [Variables Reference](docs/reference/VARIABLES.md) - All role variables
- [FAQ](docs/FAQ.md) - Frequently asked questions

---

## 🛠️ Development

### Setup Environment

```bash
# Clone the repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Activate virtual environment (creates if needed)
source activate.sh

# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Verify installation
ansible --version
molecule --version
```

### Testing

```bash
# Test a specific role
cd roles/docker
molecule test

# Test all roles
make test

# Run linters
make lint
```

### Makefile Commands

```bash
make help              # Show available commands
make install           # Install dependencies
make lint              # Run yamllint and ansible-lint
make test              # Test all roles with Molecule
make build             # Build collection tarball
make install-collection # Install collection locally
make clean             # Clean build artifacts
```

---

## 🏗️ Collection Structure

```
code3tech.devtools/
├── galaxy.yml                    # Collection metadata
├── README.md                     # This file
├── CHANGELOG.md                  # Version history
├── requirements.yml              # Collection dependencies
├── roles/
│   ├── azure_devops_agents/      # Azure DevOps Agents role
│   ├── docker/                   # Docker role
│   ├── podman/                   # Podman role
│   └── asdf/                     # asdf role
├── playbooks/                    # Example playbooks
│   ├── azure_devops_agents/
│   ├── docker/
│   ├── podman/
│   └── asdf/
├── plugins/
│   └── shared_tasks/             # Reusable tasks
└── docs/                         # Documentation
    ├── user-guides/
    ├── reference/
    └── FAQ.md
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines

- Follow existing code style and use FQCN for all modules
- Add tests for new features
- Update documentation
- Ensure all tests pass (`make test`)
- Ensure linting passes (`make lint`)
- Use [conventional commits](https://www.conventionalcommits.org/) format

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

**Code3Tech DevOps Team**
- GitHub: [@kode3tech](https://github.com/kode3tech)
- Email: suporte@code3.tech

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)

## 🔗 Links

- [GitHub Repository](https://github.com/kode3tech/ansible-col-devtools)
- [Changelog](CHANGELOG.md)

---

**Made with ❤️ by Code3Tech DevOps Team**
