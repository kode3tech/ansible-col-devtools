# Ansible Collection: kode3tech.devtools

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Ansible](https://img.shields.io/badge/ansible-2.15%2B-blue.svg)](https://www.ansible.com/)
[![CI](https://github.com/kode3tech/ansible-col-devtools/workflows/CI/badge.svg)](https://github.com/kode3tech/ansible-col-devtools/actions)

Ansible Collection for DevOps tools installation and configuration. This collection provides roles for managing containerization and development tools across Ubuntu, Debian, and RHEL-based systems.

## 📦 Included Roles

### 🐳 Docker
Complete Docker Engine installation and configuration with Docker Compose support.
- Multi-platform support (Ubuntu, Debian, RHEL/CentOS/Rocky)
- Automatic repository configuration
- User permissions management
- Docker Compose installation
- Comprehensive testing

### 🦭 Podman
Podman installation with rootless container support.
- Daemonless container engine
- Rootless containers by default
- Buildah and Skopeo included
- OCI-compliant
- Compatible with Docker commands

## 🚀 Installation

### Prerequisites - Virtual Environment

**⚠️ ALWAYS activate the virtual environment before running any Ansible commands:**

```bash
# Activate virtual environment (creates if needed)
source activate.sh

# Verify Ansible version
ansible --version
```

### From Ansible Galaxy (when published)
```bash
# After activating venv:
ansible-galaxy collection install kode3tech.devtools
```

### From Source
```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# IMPORTANT: Activate venv first!
source activate.sh

ansible-galaxy collection build
ansible-galaxy collection install kode3tech-devtools-*.tar.gz
```

## 📋 Requirements

- Ansible >= 2.15
- Python >= 3.9
- Target systems: Ubuntu 22.04+, Debian 11+, RHEL 9+
- Root or sudo privileges on target hosts

### Required Collections

Install collection dependencies before using the roles:

```bash
ansible-galaxy collection install -r requirements.yml
```

The `requirements.yml` includes:
- `community.docker` >= 3.4.0 (for Docker registry authentication)
- `containers.podman` >= 1.10.0 (for Podman registry authentication)

### Supported Distributions

- **Ubuntu**: 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- **Debian**: 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- **RHEL/CentOS/Rocky/AlmaLinux**: 9, 10

## 🎯 Quick Start

> **⚠️ Remember**: Always run `source activate.sh` before executing any Ansible commands!

### Using Collection in Playbook
```yaml
---
- name: Setup development environment
  hosts: all
  become: true
  
  collections:
    - kode3tech.devtools
  
  roles:
    - docker
    - podman
```

### Using Specific Role
```yaml
---
- name: Install Docker only
  hosts: all
  become: true
  
  collections:
    - kode3tech.devtools
  
  vars:
    docker_users:
      - devuser
      - jenkins
  
  roles:
    - docker
```

### Using requirements.yml
```yaml
---
collections:
  - name: kode3tech.devtools
    version: ">=1.0.0"
```

```bash
ansible-galaxy collection install -r requirements.yml
```

## 🔌 Installing Collection Dependencies

**IMPORTANT**: Before using the roles, install the required collections:

```bash
# 1. ALWAYS activate venv first!
source activate.sh

# 2. Install collection dependencies (required for registry authentication)
ansible-galaxy collection install -r requirements.yml
```

This will install:
- `community.docker` >= 3.4.0 (required by docker role for registry login)
- `containers.podman` >= 1.10.0 (required by podman role for registry login)

Alternatively, install individually:
```bash
# After activating venv:
ansible-galaxy collection install community.docker
ansible-galaxy collection install containers.podman
```

##  Example Playbooks

The collection includes ready-to-use example playbooks in the `playbooks/` directory:

- `setup-dev-environment.yml` - Complete development setup (Docker + Podman)
- `install-docker.yml` - Docker installation only
- `install-podman.yml` - Podman installation only
- `setup-registry-auth.yml` - Private registry authentication setup

### Running Examples

**Complete workflow:**

```bash
# 1. Activate virtual environment
source activate.sh

# 2. Install collection dependencies
ansible-galaxy collection install -r requirements.yml

# 3. Run playbook
ansible-playbook playbooks/setup-dev-environment.yml -i inventory
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- asdf (for version management)
- Git

### Setup Checklist

✅ **Step-by-step setup:**

```bash
# 1. Clone repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# 2. Activate virtual environment (creates if needed)
source activate.sh

# 3. Install collection dependencies
ansible-galaxy collection install -r requirements.yml

# 4. Verify installation
ansible --version
ansible-galaxy collection list

# 5. Run tests (optional)
cd roles/docker
molecule test
```

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# Install Python with asdf (if using asdf)
asdf install

# Create and activate virtual environment
source activate.sh
# or manually:
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
ansible --version
molecule --version
ansible-lint --version
```

### Installed Development Tools
- **Ansible Core**: Latest stable version
- **Molecule**: Testing framework for roles
- **Ansible Lint**: Code quality and best practices checker
- **pytest**: Python testing framework
- **yamllint**: YAML syntax validator

## 🧪 Testing

Each role includes comprehensive Molecule tests with support for multiple platforms.

### Test Individual Role
```bash
# Test Docker role
cd roles/docker
molecule test

# Test Podman role
cd roles/podman
molecule test
```

### Test All Roles
```bash
make test-all
```

### Lint All Files
```bash
# Ansible lint
ansible-lint

# YAML lint
yamllint .
```

## 📚 Role Documentation

Detailed documentation for each role is available in their respective README files:

- [Docker Role Documentation](roles/docker/README.md)
- [Podman Role Documentation](roles/podman/README.md)

## 🏗️ Collection Structure

```
kode3tech.devtools/
├── galaxy.yml                      # Collection metadata
├── README.md                       # This file
├── CHANGELOG.md                    # Version history
├── META.md                         # Additional metadata
├── roles/
│   ├── docker/                     # Docker role
│   │   ├── defaults/
│   │   ├── tasks/
│   │   ├── handlers/
│   │   ├── templates/
│   │   ├── molecule/
│   │   └── README.md
│   └── podman/                     # Podman role
│       ├── defaults/
│       ├── tasks/
│       ├── templates/
│       ├── molecule/
│       └── README.md
├── plugins/
│   ├── modules/                    # Custom modules (future)
│   └── filter/                     # Custom filters (future)
├── playbooks/                      # Example playbooks
│   ├── setup-dev-environment.yml
│   ├── install-docker.yml
│   └── install-podman.yml
└── docs/                           # Additional documentation
```

## 🔄 Version Compatibility

| Collection Version | Ansible Version | Python Version |
|-------------------|-----------------|----------------|
| 1.x               | >= 2.15         | >= 3.9         |

## 🔨 Makefile Commands

The project includes a Makefile with useful commands:

```bash
make help                 # Show all available commands
make install              # Install dependencies
make version              # Show installed versions
make lint                 # Run all linters
make test-docker          # Test Docker role
make test-podman          # Test Podman role
make test-all             # Test all roles
make build                # Build collection tarball
make install-collection   # Install collection locally
make clean                # Clean build artifacts
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass (`make test-all`)
- Ensure linting passes (`make lint`)
- Use conventional commits format

## � License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

**Kode3Tech DevOps Team**
- GitHub: [@kode3tech](https://github.com/kode3tech)
- Email: suporte@kode3.tech

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Documentation**: [GitHub Wiki](https://github.com/kode3tech/ansible-col-devtools/wiki)

## � Links

- [Ansible Galaxy](https://galaxy.ansible.com/kode3tech/devtools) (when published)
- [GitHub Repository](https://github.com/kode3tech/ansible-col-devtools)
- [Documentation](https://github.com/kode3tech/ansible-col-devtools/blob/main/README.md)
- [Changelog](CHANGELOG.md)

## ⭐ Acknowledgments

- Ansible Community for the amazing automation platform
- Docker Team for containerization technology
- Podman Team for daemonless container engine
- All contributors to this project

---

**Made with ❤️ by Kode3Tech DevOps Team**
