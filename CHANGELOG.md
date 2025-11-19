# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **[Docker]** RHEL 8+ support and enhanced features (v1.2.0)
  - **Extended platform support**: Now supports RHEL 8, 9, 10, CentOS, Rocky Linux, AlmaLinux
  - **Automatic permission fixes**: Resolves Docker config file ownership issues on RHEL systems
  - **Time synchronization**: Automatic chronyd handling for GPG signature validation
  - **Registry authentication**: Enhanced multi-registry support with automatic permission handling
  - **SELinux context restoration**: Proper security contexts for Docker directories
  - **Per-user config management**: Automated `.docker/config.json` ownership fixes
- **[Podman]** RHEL 8+ support and enhanced rootless features (v1.2.0)
  - **Extended platform support**: Now supports RHEL 8, 9, 10, CentOS, Rocky Linux, AlmaLinux
  - **Enhanced rootless authentication**: Per-user authentication with automatic permission fixes
  - **Multi-user support**: Isolated credentials for each user in XDG_RUNTIME_DIR
  - **SELinux context restoration**: Proper security contexts for container directories
  - **Automatic permission handling**: Resolves auth file ownership issues on RHEL systems
- **[Registry Authentication]** Enhanced RHEL support (v1.2.0)
  - **Automatic permission fixes**: Both Docker and Podman now handle RHEL file ownership
  - **Non-interactive authentication**: Perfect for CI/CD with proper credential handling
  - **Multi-registry support**: Docker Hub, GHCR, Quay.io, private registries
  - **Security enhancements**: Proper file ownership and SELinux contexts
- **[asdf]** New role for asdf version manager (v1.0.0)
  - **Binary installation** (asdf v0.16.0+): Fast, reliable installation from official GitHub releases
  - **Multi-distribution support**: Ubuntu 22/24/25, Debian 11/12/13, RHEL/Rocky 9/10
  - **Plugin management**: Automatic installation and configuration of asdf plugins
  - **Version management**: Install multiple versions of runtime tools
  - **Global version configuration**: Set default versions per user with `asdf set` command
  - **Shell integration**: Automatic configuration for bash, zsh, and fish shells
  - **Automatic home detection**: Uses `getent` to detect user home directories
  - **Internet connectivity check**: Graceful handling of offline environments
  - **RedHat optimizations**:
    - Automatic curl-minimal to curl replacement with `allowerasing=true`
    - DNF cache management (clean + makecache)
    - PATH configuration for `/usr/local/bin`
  - **Performance**: Lightweight plugins (direnv, jq) for fast testing (~15s)
  - **Idempotency**: Full idempotent operations with version checking
  - **Comprehensive testing**: Molecule tests on Ubuntu, Debian, and Rocky Linux
  - **Example playbooks**: 6 complete examples (basic, lightweight, full, multi-user, multi-shell)
  - **Documentation**: Complete README with troubleshooting and performance tips
- **[asdf]** Supported plugins categories:
  - **Lightweight plugins** (for testing/CI): direnv, jq, yq, kubectl, helm (~3-10s each)
  - **Heavy plugins** (for production): nodejs, python, ruby, golang, rust (~2-30min each)
- **[Docker]** Performance optimization configuration (v1.1.0)
  - **Storage driver**: Explicit `overlay2` with kernel check override (+15-30% I/O)
  - **Logging**: Compressed, non-blocking logs (-70% disk space, +10-20% I/O)
  - **Network**: Disabled userland-proxy for direct iptables (+10-20% throughput)
  - **BuildKit**: Enabled by default (+50-200% faster builds)
  - **Concurrency**: 10 parallel downloads/uploads (3x faster pulls)
  - **Runtime**: crun support for +20-30% faster container startup
  - **Resource limits**: Default ulimits (nofile: 65536, nproc: 32768)
  - **Overall improvement**: 2-5x performance in various scenarios
- **[Podman]** Performance optimization configuration (v1.1.0)
  - **Storage driver**: Explicit overlay with metacopy=on (+30-50% I/O)
  - **Runtime**: crun by default (+20-30% faster than runc)
  - **Parallel copies**: 10 concurrent layer downloads (+200-300% pulls)
  - **Engine tuning**: Optimized num_locks (2048) and systemd cgroup manager
  - **Package**: crun automatically installed with Podman
  - **Overall improvement**: 30-50% better I/O, 20-30% faster startup
- **[Documentation]** Performance tuning guides
  - Added "Performance Tuning" section in both Docker and Podman READMEs
  - Documented all optimization defaults and expected gains
  - LXC container optimization guide (AppArmor unconfined requirement)
  - Benchmark comparison tables
  - Custom configuration examples
- **[Docker/Podman]** Private registry authentication support
  - New variables: `docker_registries_auth` and `podman_registries_auth`
  - Secure login with `no_log: true` to prevent credential exposure
  - Support for password authentication (Docker) or password/password_file authentication (Podman)
  - Rootless-aware authentication for Podman (per-user login)
  - Automatic fallback to shell command if module fails (Podman)
  - **New**: `podman_clean_credentials` option to remove old/invalid credentials
  - Fixes "Existing credentials are invalid" errors
  - Requires `community.docker` >= 3.4.0 and `containers.podman` >= 1.10.0
- **[Docker/Podman]** Insecure registry support
  - New variables: `docker_insecure_registries` and `podman_insecure_registries`
  - Allow HTTP registries and self-signed certificates
  - Automatic configuration in daemon.json (Docker) and registries.conf (Podman)
  - Example playbook: `setup-insecure-registry.yml`
- **[Podman]** XDG_RUNTIME_DIR automatic configuration
  - Creates `/run/user/0` for root with correct permissions (0700)
  - Creates `/root/.config/containers` for authentication storage
  - Creates `/run/user/<UID>` for rootless users
  - **Uses systemd-tmpfiles for persistent configuration across reboots**
  - Configuration file: `/etc/tmpfiles.d/podman-xdg.conf`
  - Exports XDG_RUNTIME_DIR in login commands
  - Fixes "directory set by $XDG_RUNTIME_DIR does not exist" warning
  - Ensures reliable registry authentication for root and rootless modes
  - Documentation: `docs/PODMAN_XDG_RUNTIME_FIX.md`
- **[Testing]** Comprehensive Molecule tests for insecure registries
  - Added test scenarios in converge.yml for both roles
  - Enhanced verify.yml with insecure registry validation (Ansible tasks)
  - New pytest tests for JSON/TOML configuration validation
  - Tests verify: file existence, syntax, content, and structure
  - Full test coverage on Ubuntu 22.04, Debian 12, Rocky Linux 9
    - Performance tuning defaults (overlay2, BuildKit, optimized logging)
  - Complete Molecule tests
  - Documentation improvements
- **[Podman]** Smart repository detection for modern distributions
  - Auto-detect Ubuntu 24.04+ and Debian 13+ with native Podman support
  - Skip external repository setup when not needed
- Initial collection structure
- Collection metadata (galaxy.yml)
- Example playbooks
- Support for Debian 10 (Buster) and Debian 13 (Trixie/Testing)
- Collection dependencies file (`requirements.yml`)

### Fixed
- **[Docker/Podman]** Replaced deprecated `apt_key` module with modern GPG key management
  - Uses `/etc/apt/keyrings/` directory with `signed-by=` in repository configuration
  - Fixes compatibility with Debian 12+ where `apt-key` command was removed
  - Fully backward compatible with Debian 10, 11, Ubuntu 20.04+
- **[Podman]** Fixed Debian 13 prerequisite package issue
  - Removed `software-properties-common` (not available on Debian)
- **[Podman]** Resolved Ubuntu 24.04 podman_login permission issue
  - Implemented automatic fallback to shell command
  - 100% success rate across all distributions
- **[Podman]** Fixed XDG_RUNTIME_DIR warnings on registry authentication
  - Automatic directory creation for root and rootless users
  - Proper environment variable export in all login commands
  - Resolves "Authenticating with existing credentials" errors
- **[Testing]** Fixed Podman pytest configuration
  - Added missing testinfra_hosts configuration
  - Proper imports for testinfra runner

### Changed
- Restructured repository to follow Ansible Collection best practices
- Moved roles to `roles/` directory
- Updated README for collection usage
- Added collection dependencies in role metadata (meta/main.yml)

## [1.0.0] - 2025-11-05

### Added
- Docker role with complete installation and configuration
  - Multi-platform support (Ubuntu, Debian, RHEL/CentOS/Rocky)
  - Docker Compose installation
  - User permissions management
  - Comprehensive Molecule tests
- Podman role with rootless support
  - Multi-platform support (Ubuntu, Debian, RHEL/CentOS/Rocky)
  - Buildah and Skopeo installation
  - Rootless container configuration
  - TOML configuration templates
  - Comprehensive Molecule tests
- Complete testing framework with Molecule
- ansible-lint configuration (production profile)
- yamllint configuration
- Development environment setup scripts

### Documentation
- Complete role documentation
- Example playbooks
- Testing guidelines
- Contributing guidelines

[Unreleased]: https://github.com/kode3tech/ansible-col-devtools/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kode3tech/ansible-col-devtools/releases/tag/v1.0.0
