# code3tech.devtools

### Production-Ready Ansible Collection for CI/CD Infrastructure

[![Version](https://img.shields.io/badge/version-1.5.0-blue.svg)](https://github.com/kode3tech/ansible-col-devtools/blob/main/CHANGELOG.md)
[![CI](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/ci.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/ci.yml)
[![Sanity](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/sanity.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/sanity.yml)
[![Release](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/release.yml/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions/workflows/release.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-code3tech.devtools-blue.svg)](https://galaxy.ansible.com/ui/repo/published/code3tech/devtools/)
[![Downloads](https://img.shields.io/ansible/collection/d/code3tech/devtools)](https://galaxy.ansible.com/ui/repo/published/code3tech/devtools/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kode3tech/ansible-col-devtools/blob/main/LICENSE)
[![Ansible](https://img.shields.io/badge/ansible-2.15%2B-blue.svg)](https://www.ansible.com/)

Automate your complete CI/CD infrastructure—from self-hosted runners to container platforms and version management—with unified Ansible configuration across multiple providers.

**Multi-Provider CI/CD** | **Container Platforms** | **Version Management** | **Production-Grade**

[Quick Start](#quick-start) • [Documentation](#documentation) • [Support](https://github.com/kode3tech/ansible-col-devtools/issues)

---

## Table of Contents

- [Built For](#built-for)
- [CI/CD Strategy Building Blocks](#cicd-strategy-building-blocks)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Included Roles](#included-roles)
- [Usage Guide](#usage-guide)
- [Requirements](#requirements)
- [Documentation](#documentation)
- [Example Playbooks](#example-playbooks)
- [Development](#development)
- [Contributing](#contributing)
- [License & Support](#license--support)

---

## Built For

**Platform Engineers** building self-service CI/CD infrastructure  
**DevOps Teams** managing multi-provider environments  
**Site Reliability Engineers** maintaining production-grade runner fleets

### The Challenge

Managing self-hosted CI/CD infrastructure across different providers requires learning provider-specific APIs, maintaining separate deployment scripts for each platform, ensuring consistency across heterogeneous environments, and scaling infrastructure while keeping configuration manageable.

### The Solution

A unified Ansible Collection that provides consistent configuration across all CI/CD providers, API-driven automation for lifecycle management, production-tested patterns ready for enterprise deployment, and an extensible architecture for future provider additions.

---

## CI/CD Strategy Building Blocks

Every modern CI/CD strategy requires these core components. This collection provides all of them with a unified approach.

### Self-Hosted Runners & Agents

**Purpose**: Cost control, security compliance, custom hardware requirements

**Capabilities**:
- Multi-provider support: GitHub Actions, GitLab CI, Azure DevOps
- API-driven lifecycle management (create, update, delete)
- Multi-runner deployment per host with isolated directories
- Service verification and automated monitoring
- Extensible architecture for additional providers

### Container Platforms

**Purpose**: Consistent build environments, reproducible deployments

**Capabilities**:
- Docker: Industry-standard container platform with BuildKit optimization
- Podman: Daemonless, rootless alternative for enhanced security
- Automatic registry authentication handling
- Production-optimized configurations
- Multi-platform support (Ubuntu, Debian, RHEL)

### Version Management

**Purpose**: Runtime consistency across teams and environments

**Capabilities**:
- asdf version manager with 300+ plugin ecosystem
- Centralized group-based architecture
- Binary installation for reliability
- Shell integration (bash, zsh, fish)
- Multi-language support (Node.js, Python, Ruby, Go, and more)

### The Unified Approach

All components use the same Ansible configuration pattern: consistent variable structure, unified authentication methods, standardized error handling, and common service management.

**Result**: Learn once, deploy everywhere.

---

## Key Features

| Automation | Security | Production |
|------------|----------|------------|
| API-driven management | Ansible Vault integration | Battle-tested patterns |
| Zero-touch deployment | Automatic permission fixes | Multi-distribution testing |
| Idempotent operations | SELinux/AppArmor support | Service verification |

| Lifecycle Management | Multi-Platform | Documentation |
|---------------------|----------------|---------------|
| Create, update, delete | Ubuntu/Debian/RHEL | Comprehensive guides |
| Service management | x86_64 + ARM64 | Real-world examples |
| Clean unregistration | Container support | Troubleshooting resources |

---

## Included Roles

### CI/CD Runners & Agents

#### Azure DevOps Agents
Deploy and manage Azure DevOps self-hosted agents on Linux servers.

**Key Capabilities**:
- Multi-agent support with isolated directories per host
- Three agent types: Self-hosted, Deployment Group, Environment
- Automatic resource creation via Azure DevOps REST API
- Pipeline permission configuration for environments
- Service verification and lifecycle management
- Clean agent unregistration and removal

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/azure_devops_agents/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/)

---

#### GitHub Actions Runners
Deploy and manage GitHub Actions self-hosted runners on Linux servers.

**Key Capabilities**:
- Multi-runner support with isolated directories per host
- Three deployment scopes: Organization, Repository, Enterprise
- Label management and updates via GitHub REST API
- Runner group creation and assignment
- Ephemeral runner support for enhanced security
- Service verification and lifecycle management

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/github_actions_runners/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/)

---

#### GitLab CI Runners
Deploy and manage GitLab CI self-hosted runners on Linux servers.

**Key Capabilities**:
- Multi-runner support with isolated directories per host
- Three runner types: Instance, Group, Project runners
- API-based management: Create, update, delete via GitLab REST API
- Tag management without re-registration
- Advanced configuration: run_untagged, locked, access_level
- Service verification and lifecycle management

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/gitlab_ci_runners/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/)

---

### Container Platforms

#### Docker
Complete Docker Engine installation and configuration with Docker Compose support.

**Key Capabilities**:
- Multi-platform support: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
- Registry authentication with automatic permission handling
- BuildKit enabled by default for faster builds
- Optimized logging and storage configuration
- User group management with security controls

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/docker/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/)

---

#### Podman
Podman installation with rootless container support.

**Key Capabilities**:
- Daemonless container engine (no Docker daemon required)
- Enhanced rootless support with per-user authentication
- Complete toolchain: Buildah and Skopeo included
- OCI-compliant and Docker command compatible
- Multi-platform support across all major distributions

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/podman/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/)

---

### Version Management

#### asdf
asdf version manager with centralized group-based architecture.

**Key Capabilities**:
- Centralized plugin management for all users
- Group-based permissions with `asdf` group
- 300+ plugins: Node.js, Python, Ruby, Golang, Terraform, and more
- Shell integration for bash, zsh, and fish
- Binary installation for reliability and performance

[Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/asdf/README.md) | [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/asdf/)

---

## Quick Start

### Installation

**Step 1**: Install the collection from Ansible Galaxy

```bash
ansible-galaxy collection install code3tech.devtools
```

**Step 2**: Install required dependencies

```bash
ansible-galaxy collection install -r requirements.yml
```

### Your First Deployment

Choose your use case and create a playbook:

**Option A: Deploy CI/CD Runners**

```yaml
---
- name: Deploy GitHub Actions runners
  hosts: runner_hosts
  become: true
  
  roles:
    - role: code3tech.devtools.github_actions_runners
      vars:
        github_api_token: "{{ vault_github_token }}"
        github_runners_list:
          - name: "runner-01"
            state: "started"
            labels: ["linux", "x64"]
```

**Option B: Deploy Container Platform**

```yaml
---
- name: Deploy Docker
  hosts: docker_hosts
  become: true
  
  roles:
    - role: code3tech.devtools.docker
      vars:
        docker_users: ["{{ ansible_user }}"]
```

**Step 3**: Run your playbook

```bash
ansible-playbook setup.yml -i inventory
```

**Next Steps**:
- [Complete Usage Guide](#usage-guide) - Detailed setup procedures
- [Role Documentation](#documentation) - Role-specific configuration
- [Example Playbooks](#example-playbooks) - Ready-to-use examples

---

## Usage Guide

### CI/CD Runners Setup

#### Prerequisites

Before deploying runners or agents, ensure you have:

1. **API Tokens**: Personal access tokens or runner registration tokens
   - Store securely in Ansible Vault (never commit tokens to version control)
   - [Token Setup Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/)

2. **Target Hosts**: Prepared Linux servers
   - Supported: Ubuntu 22.04+, Debian 11+, RHEL 9+
   - Requirements: 2GB RAM, 10GB disk space, sudo access

3. **Network Access**: Connectivity to provider APIs
   - GitHub: `https://api.github.com`
   - GitLab: `https://gitlab.com/api` or your GitLab instance
   - Azure: `https://dev.azure.com`

#### Basic Runner Deployment

**1. Create inventory**:
```ini
[github_runners]
runner-host-01 ansible_host=192.168.1.10

[gitlab_runners]
runner-host-02 ansible_host=192.168.1.11

[azure_agents]
agent-host-01 ansible_host=192.168.1.12
```

**2. Store tokens securely**:
```bash
# Create encrypted vault file
ansible-vault create vars/vault.yml

# Add tokens:
vault_github_token: "ghp_xxxxxxxxxxxx"
vault_gitlab_token: "glpat-xxxxxxxxxxxx"
vault_azure_pat: "xxxxxxxxxxxx"
```

**3. Create playbook**:
```yaml
---
- name: Deploy CI/CD Runners
  hosts: github_runners
  become: true
  vars_files:
    - vars/vault.yml
  
  roles:
    - role: code3tech.devtools.github_actions_runners
      vars:
        github_api_token: "{{ vault_github_token }}"
        github_runners_list:
          - name: "runner-01"
            state: "started"
            labels: ["linux", "production"]
```

**4. Deploy**:
```bash
ansible-playbook deploy-runners.yml -i inventory --ask-vault-pass
```

**Detailed Guides**:
- [GitHub Actions Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/02-prerequisites.md)
- [GitLab CI Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/02-prerequisites.md)
- [Azure DevOps Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/02-prerequisites.md)

---

### Container Platform Setup

#### Docker Deployment

Deploy Docker with user access and registry authentication:

```yaml
---
- name: Setup Docker
  hosts: docker_hosts
  become: true
  vars_files:
    - vars/vault.yml
  
  roles:
    - role: code3tech.devtools.docker
      vars:
        docker_users:
          - "{{ ansible_user }}"
        docker_registries_auth:
          - registry: "ghcr.io"
            username: "myuser"
            password: "{{ vault_github_token }}"
```

[Docker Complete Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/03-basic-usage.md)

---

#### Podman Deployment

Deploy Podman with rootless support:

```yaml
---
- name: Setup Podman
  hosts: podman_hosts
  become: true
  
  roles:
    - role: code3tech.devtools.podman
      vars:
        podman_rootless_users:
          - "appuser"
```

[Podman Rootless Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/04-rootless-mode.md)

---

### Version Manager Setup

#### asdf Deployment

Deploy asdf with language runtimes for development teams:

```yaml
---
- name: Setup asdf
  hosts: dev_servers
  become: true
  
  roles:
    - role: code3tech.devtools.asdf
      vars:
        asdf_plugins:
          - name: nodejs
            versions: ["20.11.0"]
            global: "20.11.0"
          - name: python
            versions: ["3.11.7"]
            global: "3.11.7"
```

[asdf Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/asdf/03-basic-usage.md)

---

## Requirements

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

## Documentation

### Getting Started
- [Getting Started Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/getting-started/)

### CI/CD Runners

#### GitHub Actions Runners
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/github_actions_runners/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/)
  - [Prerequisites & Token Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/02-prerequisites.md)
  - [Basic Usage](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/03-basic-usage.md)
  - [Multi-Runner Deployment](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/04-multi-runner.md)
  - [Advanced Features](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/github-actions-runners/05-advanced-features.md)

#### GitLab CI Runners
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/gitlab_ci_runners/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/)
  - [Prerequisites & Token Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/02-prerequisites.md)
  - [Basic Usage](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/03-basic-usage.md)
  - [API Management](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/04-api-management.md)
  - [Security Best Practices](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/gitlab-ci-runners/07-security.md)

#### Azure DevOps Agents
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/azure_devops_agents/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/)
  - [Prerequisites & PAT Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/02-prerequisites.md)
  - [Agent Types](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/03-agent-types.md)
  - [Multi-Agent Deployment](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/azure-devops-agents/04-multi-agent.md)

### Container Platforms

#### Docker
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/docker/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/)
  - [Architecture Overview](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/01-introduction.md)
  - [Registry Authentication](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/04-registry-auth.md)
  - [Performance Optimization](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/docker/05-performance.md)

#### Podman
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/podman/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/)
  - [Rootless vs Rootful](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/02-architecture.md)
  - [Registry Authentication](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/04-registry-auth.md)
  - [Performance Tuning](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/podman/05-performance.md)

### Version Management

#### asdf
- [Role README](https://github.com/kode3tech/ansible-col-devtools/blob/main/roles/asdf/README.md)
- [Complete Guide](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/asdf/)
  - [Plugin Management](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/asdf/04-plugin-management.md)
  - [Multi-User Setup](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/user-guides/asdf/05-multi-user.md)

### Reference
- [FAQ](https://github.com/kode3tech/ansible-col-devtools/blob/main/docs/FAQ.md) - Frequently asked questions

---

## Example Playbooks

The collection includes ready-to-use example playbooks in the `playbooks/` directory:

### Azure DevOps Agents

| Playbook | Description |
|----------|-------------|
| [install-production.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/azure_devops_agents/install-production.yml) | Production deployment with validation |
| [install-single-agent.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/azure_devops_agents/install-single-agent.yml) | Basic single agent installation |
| [install-multi-agent.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/azure_devops_agents/install-multi-agent.yml) | Multiple agents per host |

### GitHub Actions Runners

| Playbook | Description |
|----------|-------------|
| [install-production.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/github_actions_runners/install-production.yml) | Production deployment with validation |
| [install-single-runner.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/github_actions_runners/install-single-runner.yml) | Basic single runner installation |
| [install-multi-runner.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/github_actions_runners/install-multi-runner.yml) | Multiple runners per host |

### GitLab CI Runners

| Playbook | Description |
|----------|-------------|
| [install-production.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/gitlab_ci_runners/install-production.yml) | Production deployment with all features and comprehensive validation |

### Docker

| Playbook | Description |
|----------|-------------|
| [install-docker.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/docker/install-docker.yml) | Production Docker installation with optimizations |

### Podman

| Playbook | Description |
|----------|-------------|
| [install-podman.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/podman/install-podman.yml) | Production Podman installation with rootless support |

### asdf

| Playbook | Description |
|----------|-------------|
| [install-asdf-basic.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/asdf/install-asdf-basic.yml) | Quick install with lightweight plugins (direnv, jq) |
| [install-asdf-full.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/asdf/install-asdf-full.yml) | Full installation with Node.js and Python |
| [setup-multi-user.yml](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/asdf/setup-multi-user.yml) | Multi-user configuration |

### Running Examples

```bash
# Install dependencies
ansible-galaxy collection install -r requirements.yml

# Run a playbook
ansible-playbook playbooks/docker/install-docker.yml -i your_inventory
```

See [playbooks/README.md](https://github.com/kode3tech/ansible-col-devtools/blob/main/playbooks/README.md) for complete documentation.

---

## Development

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

## Collection Structure

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

## Contributing

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

See [CONTRIBUTING.md](https://github.com/kode3tech/ansible-col-devtools/blob/main/CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License - see [LICENSE](https://github.com/kode3tech/ansible-col-devtools/blob/main/LICENSE) file for details.

## Authors

**Code3Tech DevOps Team**
- GitHub: [@kode3tech](https://github.com/kode3tech)
- Email: suporte@code3.tech

## Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)

## Links

- [GitHub Repository](https://github.com/kode3tech/ansible-col-devtools)
- [Changelog](https://github.com/kode3tech/ansible-col-devtools/blob/main/CHANGELOG.md)

---

**Made with ❤️ by Code3Tech DevOps Team**
