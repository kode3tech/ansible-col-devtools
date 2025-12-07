# Collection Meta Information

This file provides additional metadata about the `code3tech.devtools` collection.

## Collection Information

- **Namespace**: code3tech
- **Name**: devtools
- **Description**: Ansible Collection for DevOps tools installation and configuration
- **License**: MIT
- **Repository**: https://github.com/kode3tech/ansible-col-devtools

## Roles Included

### azure_devops_agents
Deploy and manage Azure DevOps self-hosted agents on Linux servers.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Multi-agent support with isolated directories
- Three agent types: Self-hosted, Deployment Group, Environment
- Automatic resource creation via REST API
- Service verification and management
- Clean agent removal

### github_actions_runners
Deploy and manage GitHub Actions self-hosted runners on Linux servers.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Multi-runner support with isolated directories
- Three scopes: Organization, Repository, Enterprise
- Label management via REST API
- Runner groups support
- Ephemeral runners for security
- Service verification and management

### docker
Docker Engine installation and configuration with Docker Compose support.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Automatic repository configuration
- Docker Compose installation
- User group management
- Service configuration

### podman
Podman installation with rootless container support.

**Supported Platforms:**
- Ubuntu 22.04, 24.04, 25.04
- Debian 11, 12, 13
- RHEL/CentOS/Rocky Linux 9, 10

**Main Features:**
- Daemonless container engine
- Rootless mode configuration
- Buildah and Skopeo included
- OCI-compliant runtime

### asdf
asdf version manager for managing multiple runtime versions with binary installation.

**Supported Platforms:**
- Ubuntu 22.04 (Jammy), 24.04 (Noble), 25.04 (Plucky)
- Debian 11 (Bullseye), 12 (Bookworm), 13 (Trixie)
- RHEL/CentOS/Rocky/AlmaLinux 9, 10

**Main Features:**
- **Binary installation** (asdf v0.16.0+): Fast, reliable installation from official releases
- **Multi-distribution support**: Ubuntu, Debian, RHEL/Rocky with specific optimizations
- **Plugin management**: Automatic installation of 300+ available plugins
- **Version management**: Install and manage multiple versions of runtime tools
- **Global version configuration**: Set default versions per user
- **Shell integration**: Automatic configuration for bash, zsh, and fish
- **Automatic home detection**: Uses getent for user home directory detection
- **Internet connectivity check**: Graceful handling of offline environments
- **RedHat optimizations**: curl-minimal replacement, DNF cache management, PATH config
- **Performance**: Lightweight plugins (direnv, jq) for fast testing (~15s)
- **Idempotency**: Full idempotent operations with version checking
- **PATH integration**: System-wide asdf availability via /usr/local/bin symlink

**Supported Plugin Categories:**
- Lightweight plugins (testing/CI): direnv, jq, yq, kubectl, helm (~3-10s)
- Heavy plugins (production): nodejs, python, ruby, golang, rust (~2-30min)

**Installation Time:**
- asdf binary only: ~10-20 seconds
- + lightweight plugins: ~15-30 seconds
- + nodejs (1 version): ~3-8 minutes
- + python (1 version): ~2-7 minutes
- Full stack (nodejs + python): ~5-15 minutes

## Dependencies

### Runtime Dependencies
- ansible-core >= 2.15
- Python >= 3.9

### Development Dependencies
See `requirements.txt` for complete list:
- molecule[docker]
- ansible-lint
- yamllint
- pytest
- testinfra

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/kode3tech/ansible-col-devtools/issues
- Documentation: https://github.com/kode3tech/ansible-col-devtools

## Maintainers

- Code3Tech DevOps Team
