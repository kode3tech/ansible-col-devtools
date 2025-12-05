# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-05

### Added
- **[Azure DevOps Agents]** NEW ROLE - Enterprise-grade agent deployment (v1.0.0)
  - **Multi-agent support**: Deploy N agents per host with isolated directories
  - **Three agent types**: Self-hosted (pools), Deployment Group, and Environment agents
  - **Auto-create resources**: Automatically create Deployment Groups and Environments via REST API
  - **Open access**: Configure pipeline permissions for environments (YAML pipelines)
  - **Service verification**: Ensures all agent services are enabled and running at end of deployment
  - **Agent removal**: Clean unregistration with `state: absent` support
  - **Tag updates**: Update agent tags via REST API without reconfiguration
  - **Input validation**: Comprehensive validation with clear ASCII-box error messages
  - **Proxy support**: Full proxy configuration for enterprise environments
  - **Multi-platform**: Ubuntu 22+, Debian 11+, RHEL/CentOS/Rocky 9+
  - **Systemd integration**: Automatic service management for each agent
  - **Security**: Dedicated non-root `azagent` user for agent processes
  - **PAT authentication**: Unattended registration using Personal Access Tokens
- **[Azure DevOps Agents]** Complete documentation
  - **Role README**: Quick reference with all features and examples
  - **Complete Guide**: Comprehensive 800+ line guide in `docs/user-guides/`
  - **Production playbook**: Ready-to-use `install-production.yml` with vault and verification
  - **Multiple example playbooks**: Single agent, multi-agent, deployment group
- **[Azure DevOps Agents]** Advanced features
  - **Rocky Linux support**: Handles `curl-minimal` package conflict with `allowerasing: true`
  - **Download URL fix**: Uses new `download.agent.dev.azure.com` endpoint (old URLs deprecated)
  - **Hostname sanitization**: Automatically replaces dots with dashes for valid agent names
  - **svc.sh idempotency**: Checks for `.service` marker file before install
  - **Service name escaping**: Reads actual service name from `.service` file

## [Unreleased]

### Added
- **[Documentation]** Docker Complete Guide (v1.4.0)
  - **Comprehensive documentation** for Docker production deployment
  - **Docker Architecture** overview and comparison with Podman
  - **Detailed variable reference** with explanations and examples
  - **Production playbook walkthrough** with line-by-line explanations
  - **Performance optimization guide** (overlay2, BuildKit, concurrent downloads, userland-proxy)
  - **Monitoring section** with Prometheus metrics configuration
  - **Troubleshooting section** for common issues (permissions, DNS, storage)
  - **Real-world examples** for development, CI/CD, and production environments
  - Location: `docs/user-guides/DOCKER_COMPLETE_GUIDE.md`
- **[Documentation]** Podman Complete Guide (v1.3.0)
  - **Comprehensive documentation** for Podman Root vs Rootless mode
  - **Detailed variable reference** with explanations and examples
  - **Production playbook walkthrough** with line-by-line explanations
  - **Performance optimization guide** (crun, metacopy, parallel downloads)
  - **Troubleshooting section** for common issues (XDG_RUNTIME_DIR, storage conflicts)
  - **Real-world examples** for development, CI/CD, and production environments
  - Location: `docs/user-guides/PODMAN_COMPLETE_GUIDE.md`
- **[Playbooks]** Updated Docker production playbook (v1.4.0)
  - **Replaced basic install-docker.yml** with full production configuration
  - **Custom data directory** (`/opt/docker-data`) for SSD optimization
  - **High concurrency downloads** (25 parallel) for 200-300% faster pulls
  - **Non-blocking logging** with compression and 16MB buffer
  - **Live restore** enabled for zero-downtime daemon updates
  - **Prometheus metrics** endpoint at 127.0.0.1:9323
  - **DNS optimization** with Cloudflare/Google
  - **Time synchronization** pre-tasks (critical for GPG keys)
  - **Validation post-tasks** with container tests and metrics check
  - Location: `playbooks/docker/install-docker.yml`
- **[Docker]** RHEL 9+ support and enhanced features (v1.2.0)
  - **Extended platform support**: Now supports RHEL 9, 10, CentOS, Rocky Linux, AlmaLinux
  - **Automatic permission fixes**: Resolves Docker config file ownership issues on RHEL systems
  - **Time synchronization**: Automatic chronyd handling for GPG signature validation
  - **Registry authentication**: Enhanced multi-registry support with automatic permission handling
  - **SELinux context restoration**: Proper security contexts for Docker directories
  - **Per-user config management**: Automated `.docker/config.json` ownership fixes
- **[Podman]** RHEL 9+ support and enhanced rootless features (v1.2.0)
  - **Extended platform support**: Now supports RHEL 9, 10, CentOS, Rocky Linux, AlmaLinux
  - **Enhanced rootless authentication**: Per-user authentication with automatic permission fixes
  - **Multi-user support**: Isolated credentials for each user in XDG_RUNTIME_DIR
  - **SELinux context restoration**: Proper security contexts for container directories
  - **Automatic permission handling**: Resolves auth file ownership issues on RHEL systems
  - **Storage driver conflict detection**: Automatic detection and reset of database graph driver mismatches
  - **Improved authentication reliability**: Automatic storage reset prevents authentication failures
- **[Registry Authentication]** Enhanced RHEL support (v1.2.0)
  - **Automatic permission fixes**: Both Docker and Podman now handle RHEL file ownership
  - **Non-interactive authentication**: Perfect for CI/CD with proper credential handling
  - **Multi-registry support**: Docker Hub, GHCR, Quay.io, private registries
  - **Security enhancements**: Proper file ownership and SELinux contexts
- **[asdf]** MAJOR ARCHITECTURAL IMPROVEMENT - Centralized group-based approach (v2.0.0)
  - **🚀 Breaking Change**: Complete redesign from per-user to centralized architecture
  - **Centralized plugin management**: Configure plugins once, applies to all users
  - **Group-based permissions**: Uses `asdf` group for shared access (no more conflicts!)
  - **Multi-user support**: Multiple users can use same asdf installation without permission issues
  - **System-wide PATH**: Added `/etc/profile.d/asdf.sh` for global availability
  - **User validation**: Validates users exist on system before configuration
  - **Simplified variables**: Clean configuration - users as simple list, centralized plugins
  - **Improved reliability**: No more "permission denied" errors between users
- **[asdf]** Enhanced features and capabilities (v1.0.0 → v2.0.0)
  - **Binary installation** (asdf v0.16.0+): Fast, reliable installation from official GitHub releases
  - **Multi-distribution support**: Ubuntu 22/24/25, Debian 11/12/13, RHEL/Rocky 9/10
  - **Plugin management**: Automatic installation and configuration of asdf plugins
  - **Version management**: Install multiple versions of runtime tools
  - **Global version configuration**: Set default versions per user with `asdf set` command
  - **Shell integration**: Automatic configuration for bash, zsh, and fish shells
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

### Changed
- **[asdf]** ⚠️ BREAKING CHANGE: Variable structure completely redesigned (v2.0.0)
  - **Old** (v1.x): Complex per-user configuration with nested plugins
  - **New** (v2.x): Simple centralized configuration with user list
  ```yaml
  # OLD v1.x (❌ no longer supported)
  asdf_users:
    - name: "user1"
      shell: "bash"
      plugins:
        - name: "nodejs"
          versions: ["20.11.0"]
          global: "20.11.0"
  
  # NEW v2.x (✅ required format)
  asdf_plugins:
    - name: "nodejs"
      versions: ["20.11.0"]
      global: "20.11.0"
  asdf_users:
    - "user1"
  ```
  - **Migration required**: Update playbooks to use new variable structure
  - **Benefits**: Eliminates permission conflicts, simplifies management, enables multi-user
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
  - Support for password authentication (Docker) or password authentication (Podman)
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
