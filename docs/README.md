# 📚 Documentation

Welcome to the **code3tech.devtools** Ansible Collection documentation!

## 📖 Documentation Structure

Our documentation is organized into the following categories:

### 🚀 [Getting Started](getting-started/)
Start here if you're new to this collection.
- [Installation](getting-started/01-installation.md) - Install collection and verify dependencies
- [First Playbook](getting-started/02-first-playbook.md) - Deploy your first role (Docker, Podman, or CI runner)
- [Inventory Basics](getting-started/03-inventory-basics.md) - Organize infrastructure and manage hosts
- [Using Roles](getting-started/04-using-roles.md) - Explore all 6 collection roles
- [Common Patterns](getting-started/05-common-patterns.md) - Production-ready patterns (multi-env, vault, tags)
- [Troubleshooting](getting-started/06-troubleshooting.md) - Fix common execution issues

### 📘 [User Guides](user-guides/)
Learn how to use the collection effectively.
- [Docker Complete Guide](user-guides/docker/) ⭐ - 8-part modular guide to production deployment, performance, and troubleshooting
- [Podman Complete Guide](user-guides/podman/) ⭐ - 8-part modular guide to Root vs Rootless mode, variables, and performance
- [Azure DevOps Agents Guide](user-guides/azure-devops-agents/) - Multi-agent deployment and management
- [GitHub Actions Runners Guide](user-guides/github-actions-runners/) - Self-hosted runner deployment
- [GitLab CI Runners Guide](user-guides/gitlab-ci-runners/) ⭐ - API-based runner management
- [asdf Version Manager Guide](user-guides/asdf/) - Multi-language version management

### ❓ [FAQ](FAQ.md)
Frequently asked questions about installation, usage, and performance.

### 👨‍💻 [Development](development/)
Contributing to the project.
- [Role Structure](development/ROLE_STRUCTURE.md) - How roles are organized
- [Testing Guide](development/testing/) - Comprehensive testing documentation
- [Setup Documentation](development/SETUP.md) - Development environment setup (venv, asdf, molecule)

### 🔄 [Maintenance](maintenance/)
Keeping your installation up to date.
- [Upgrade Guide](maintenance/UPGRADE_GUIDE.md) - Upgrading between versions
- [Version Information](maintenance/VERSIONS.md) - Tool versions reference

---

## 🗂️ Role-Specific Documentation

Each role maintains its own documentation:

- **[Docker Role](../roles/docker/README.md)** - Docker Engine installation and configuration
- **[Podman Role](../roles/podman/README.md)** - Podman with rootless container support
- **[Azure DevOps Agents Role](../roles/azure_devops_agents/README.md)** - Azure Pipelines self-hosted agents
- **[GitHub Actions Runners Role](../roles/github_actions_runners/README.md)** - GitHub Actions self-hosted runners
- **[GitLab CI Runners Role](../roles/gitlab_ci_runners/README.md)** - GitLab CI self-hosted runners with API management
- **[asdf Role](../roles/asdf/README.md)** - asdf version manager for multi-language development

---

## 🆘 Need Help?

- 📖 Check the [User Guides](user-guides/)
- 📖 Check the [FAQ](FAQ.md)
- 🐛 Report bugs in [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)
- 💬 Ask questions in [GitHub Discussions](https://github.com/kode3tech/ansible-col-devtools/discussions)
- 📧 Email: suporte@kode3.tech

---

## 📚 Quick Links

### For New Users
1. [Installation](getting-started/01-installation.md)
2. [First Playbook](getting-started/02-first-playbook.md)
3. [Inventory Basics](getting-started/03-inventory-basics.md)
4. [Using Roles](getting-started/04-using-roles.md)
5. [FAQ](FAQ.md)

### For Developers
1. [Contributing Guide](../CONTRIBUTING.md)
2. [Role Structure](development/ROLE_STRUCTURE.md)
3. [Testing Guide](development/testing/)
4. [Setup Documentation](development/SETUP.md)

### For Reference
1. [Version Information](maintenance/VERSIONS.md)
2. [Upgrade Guide](maintenance/UPGRADE_GUIDE.md)
3. [Variables Reference](reference/VARIABLES.md)

---

**Last updated:** December 18, 2025
