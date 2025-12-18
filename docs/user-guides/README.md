# 📘 User Guides

Guides for using the code3tech.devtools collection effectively.

## 📋 Available Guides

### [GitLab CI Runners Complete Guide](gitlab-ci-runners/) ⭐ NEW
The **comprehensive guide** to GitLab CI self-hosted runners with the code3tech.devtools collection.
- **Multi-Runner Architecture** - Deploy N runners per host with isolated configs
- **Three Runner Types** - Instance, Group, and Project runners
- **API-First Management** - Create, update, and delete runners via GitLab API
- **Dynamic Tag Management** - Update tags without re-registration
- **Advanced Features** - run_untagged, locked, access_level configuration
- Production deployment with performance tuning
- Security best practices with token protection
- Troubleshooting common issues

### [GitHub Actions Runners Complete Guide](github-actions-runners/) ⭐ NEW
The **comprehensive guide** to GitHub Actions self-hosted runners with the code3tech.devtools collection.
- **Multi-Runner Architecture** - Deploy N runners per host with isolation
- **Three Scopes** - Organization, Repository, and Enterprise runners
- **Runner Groups** - Create groups and manage access control
- **Label Management** - Automatic label assignment via REST API
- **Ephemeral Runners** - Single-use runners for maximum security
- Production deployment with complete examples
- Security best practices with token protection
- Troubleshooting common issues

### [Azure DevOps Agents Complete Guide](azure-devops-agents/) ⭐ NEW
The **comprehensive guide** to Azure DevOps self-hosted agents with the code3tech.devtools collection.
- **Multi-Agent Architecture** - Deploy N agents per host with isolation
- **Three Agent Types** - Self-hosted, Deployment Group, and Environment agents
- **Auto-Create Resources** - Automatically create Deployment Groups and Environments
- **Open Access** - Configure pipeline permissions for environments
- Production deployment with inventory examples
- Security best practices with PAT management
- Troubleshooting common issues
- Complete variable reference

### [Docker Complete Guide](docker/) ⭐ NEW
The **comprehensive guide** to Docker with the code3tech.devtools collection.
- **Docker Architecture** - Understanding the client-server model
- Complete variable reference with detailed explanations
- Production playbook walkthrough with line-by-line explanations
- Performance optimization (overlay2, BuildKit, concurrent downloads)
- Monitoring with Prometheus metrics
- Troubleshooting common issues
- Real-world examples for development, CI/CD, and production

### [Podman Complete Guide](podman/) ⭐ NEW
The **comprehensive guide** to Podman with the code3tech.devtools collection.
- **Root vs Rootless Mode** - Understanding the key difference
- Complete variable reference with detailed explanations
- Production playbook walkthrough with line-by-line explanations
- Performance optimization (crun, metacopy, parallel downloads)
- Troubleshooting common issues
- Real-world examples for development, CI/CD, and production

### [asdf Complete Guide](asdf/) ⭐ NEW
The **comprehensive guide** to asdf version manager with the code3tech.devtools collection.
- **Centralized Group-Based Architecture** - Multi-user support without conflicts
- **Plugin Categories** - Lightweight (binary) vs Heavy (compiled) plugins
- **Multi-User Configuration** - Group-based permissions for team environments
- Production deployment with complete examples
- Performance optimization and security best practices
- Troubleshooting common issues
- Complete variable reference
- 📂 8-part modular documentation for video tutorials

---

## 🎯 Common Use Cases

### GitHub Actions Runner Deployment
See [GitHub Actions Runners Guide - Basic Installation](github-actions-runners/03-basic-installation.md)

### GitHub Actions Multi-Runner Setup
See [GitHub Actions Runners Guide - Multi-Runner Deployment](github-actions-runners/06-advanced-features.md#multi-runner-deployment)

### GitHub Actions Runner Groups
See [GitHub Actions Runners Guide - Labels & Runner Groups](github-actions-runners/05-labels-and-groups.md)

### GitHub Actions Security Best Practices
See [GitHub Actions Runners Guide - Security](github-actions-runners/07-security.md)

### Azure DevOps Agent Deployment
See [Azure DevOps Agents Guide - Production Deployment](azure-devops-agents/06-production-deployment.md)

### Azure DevOps Multi-Agent Setup
See [Azure DevOps Agents Guide - Introduction & Architecture](azure-devops-agents/01-introduction.md)

### Docker Performance Optimization
See [Docker Guide - Performance & Security](docker/07-performance-security.md)

### Docker Production Deployment
See [Docker Guide - Production Deployment](docker/06-production-deployment.md)

### Understanding Podman Root vs Rootless
See [Podman Guide - Introduction](podman/01-introduction.md#root-mode-vs-rootless-mode)

### Configuring Rootless Users
See [Podman Guide - Rootless Configuration](podman/05-rootless-config.md)

### Podman Performance Optimization
See [Podman Guide - Performance & Security](podman/07-performance-security.md)

### Authenticating to Docker Hub
See [Docker Guide - Registry Authentication](docker/04-registry-auth.md#docker-hub)

### Authenticating to Private Registries
See [Docker Guide - Registry Authentication](docker/04-registry-auth.md#private-registries)

### Using Ansible Vault for Credentials
See [Docker Guide - Registry Authentication](docker/04-registry-auth.md#security-best-practices)

### Troubleshooting Docker Issues
See [Docker Guide - Troubleshooting](docker/08-troubleshooting.md)

### Troubleshooting Podman Issues
See [Podman Guide - Troubleshooting](podman/08-troubleshooting.md)

### Understanding asdf Architecture
See [asdf Complete Guide - Introduction](asdf/01-introduction.md)

### Configuring asdf Plugins
See [asdf Complete Guide - Plugin Management](asdf/04-plugin-management.md)

### Multi-User asdf Configuration
See [asdf Complete Guide - Multi-User Configuration](asdf/05-multi-user-config.md)

### Troubleshooting asdf Issues
See [asdf Complete Guide - Troubleshooting](asdf/08-troubleshooting.md)

---

[← Back to Documentation Index](../README.md)
