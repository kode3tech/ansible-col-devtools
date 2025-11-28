# Ansible Collection: code3tech.devtools

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Ansible](https://img.shields.io/badge/ansible-2.15%2B-blue.svg)](https://www.ansible.com/)

Ansible Collection for DevOps tools installation and configuration. This collection provides roles for managing containerization and development tools across Ubuntu, Debian, and RHEL-based systems.

## 📦 Included Roles

### 🐳 Docker
Complete Docker Engine installation and configuration with Docker Compose support.
- **Multi-platform support**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 8+
- **All systems**: Automatic permission fixes for user Docker config files
- **RHEL enhancements**: Time sync, SELinux support
- **Registry authentication**: Multi-registry support with automatic permission handling
- **User permissions management**: Automated Docker group configuration
- **Comprehensive testing**: Multi-distribution Molecule tests

### 🤭 Podman
Podman installation with rootless container support.
- **Daemonless container engine**: No Docker daemon required
- **Enhanced rootless support**: Per-user authentication with automatic permission fixes
- **Multi-platform support**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 8+
- **All systems**: Automatic permission fixes for user Podman auth files
- **RHEL enhancements**: SELinux support, XDG runtime fixes
- **Storage conflict resolution**: Automatic detection and reset of database graph driver mismatches
- **Improved authentication reliability**: Automatic storage reset prevents authentication failures
- **Complete toolchain**: Buildah and Skopeo included
- **OCI-compliant**: Compatible with Docker commands

### 🔧 asdf
asdf version manager with centralized group-based architecture.
- **Centralized plugin management**: Configure once, applies to all users
- **Group-based permissions**: Multi-user support with `asdf` group
- **System-wide installation**: Plugins installed in `/opt/asdf`
- **Multi-language support**: Node.js, Python, Ruby, Golang, and 300+ plugins
- **Shell integration**: Automatic configuration for bash, zsh, fish
- **User validation**: Ensures users exist before configuration

## 🚀 Installation

### Prerequisites - Virtual Environment

**⚠️ ALWAYS activate the virtual environment before running any Ansible commands:**

```bash
# Activate virtual environment (creates if needed)
source activate.sh

# Verify Ansible version
ansible --version
```

### From Source (Recommended)
```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# IMPORTANT: Activate venv first!
source activate.sh

# Build and install locally
make install-collection
```

### From Source
```bash
git clone https://github.com/kode3tech/ansible-col-devtools.git
cd ansible-col-devtools

# IMPORTANT: Activate venv first!
source activate.sh

ansible-galaxy collection build
ansible-galaxy collection install code3tech-devtools-*.tar.gz
```

## 📋 Requirements

- Ansible >= 2.15
- Python >= 3.9
- Target systems: Ubuntu 22.04+, Debian 11+, RHEL 8+
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
- **RHEL/CentOS/Rocky/AlmaLinux**: 8, 9, 10

### Enhanced Multi-Distribution Support

This collection includes **comprehensive support** for all distributions with automatic fixes for common container issues:

- ✅ **Universal permission management**: Automatic fixes for Docker/Podman config files on all distributions
- ✅ **RHEL-specific time synchronization**: Handles chronyd for GPG validation (RHEL 10)
- ✅ **RHEL SELinux compatibility**: Proper context restoration for container directories
- ✅ **Multi-user authentication**: Isolated credentials with proper ownership across all systems
- ✅ **Distribution-specific optimizations**: Tailored for Ubuntu, Debian, and RHEL family
- ✅ **Storage conflict resolution**: Automatic detection and reset of Podman database graph driver mismatches

## 🎯 Quick Start

> **⚠️ Remember**: Always run `source activate.sh` before executing any Ansible commands!

### Using Collection in Playbook
```yaml
---
- name: Setup development environment
  hosts: all
  become: true
  
  collections:
    - code3tech.devtools
  
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
    - code3tech.devtools
  
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
  - name: code3tech.devtools
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

## 📋 Example Playbooks

The collection includes ready-to-use example playbooks organized by role in the `playbooks/` directory:

### Docker Examples
- **[playbooks/docker/install-docker.yml](playbooks/docker/install-docker.yml)** - Basic Docker installation
- **[playbooks/docker/setup-registry-auth.yml](playbooks/docker/setup-registry-auth.yml)** - Private registry authentication
- **[playbooks/docker/setup-insecure-registry.yml](playbooks/docker/setup-insecure-registry.yml)** - Insecure registry configuration

### Podman Examples
- **[playbooks/podman/install-podman.yml](playbooks/podman/install-podman.yml)** - Production Podman installation with performance optimizations

### asdf Examples
- **[playbooks/asdf/install-asdf-basic.yml](playbooks/asdf/install-asdf-basic.yml)** - Quick testing with lightweight plugins
- **[playbooks/asdf/install-asdf-full.yml](playbooks/asdf/install-asdf-full.yml)** - Full installation with Node.js and Python
- **[playbooks/asdf/setup-multi-user.yml](playbooks/asdf/setup-multi-user.yml)** - Multi-user configuration

See [playbooks/README.md](playbooks/README.md) for complete documentation of all available examples.

### Running Examples

**Complete workflow:**

```bash
# 1. Activate virtual environment
source activate.sh

# 2. Install collection dependencies
ansible-galaxy collection install -r requirements.yml

# 3. Run playbook
ansible-playbook playbooks/docker/install-docker.yml -i inventory
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
code3tech.devtools/
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

The project includes a Makefile with useful commands for CI/CD:

```bash
make help                 # Show all available commands
make install              # Install dependencies
make version              # Show installed versions
make lint                 # Run all linters (yamllint + ansible-lint)
make lint-yaml            # Run yamllint only
make lint-ansible         # Run ansible-lint only
make test                 # Test all roles with Molecule
make build                # Build collection tarball
make install-collection   # Install collection locally
make publish              # Publish to Galaxy (requires GALAXY_API_KEY)
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
- Ensure all tests pass (`make test`)
- Ensure linting passes (`make lint`)
- Use conventional commits format

## � License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

**Code3Tech DevOps Team**
- GitHub: [@code3tech](https://github.com/code3tech)
- Email: suporte@code3.tech

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- **Documentation**: [GitHub Wiki](https://github.com/kode3tech/ansible-col-devtools/wiki)

## � Links

- [Ansible Galaxy](https://galaxy.ansible.com/code3tech/devtools)
- [GitHub Repository](https://github.com/kode3tech/ansible-col-devtools)
- [Documentation](https://github.com/kode3tech/ansible-col-devtools/blob/main/README.md)
- [Changelog](CHANGELOG.md)

## ⭐ Acknowledgments

- Ansible Community for the amazing automation platform
- Docker Team for containerization technology
- Podman Team for daemonless container engine
- All contributors to this project

---

**Made with ❤️ by Code3Tech DevOps Team**
