# GitLab CI Runners - Complete User Guide

Comprehensive guide for deploying and managing GitLab CI self-hosted runners using the `code3tech.devtools.gitlab_ci_runners` role.

## 📋 Guide Structure

This guide is split into 8 parts for easier learning and navigation:

| Part | Topic | Description |
|------|-------|-------------|
| **[Part 1](01-introduction.md)** | Introduction & Concepts | What are GitLab CI Runners? Why self-hosted? Multi-runner architecture |
| **[Part 2](02-prerequisites.md)** | Prerequisites & Setup | System requirements, GitLab PAT creation, Ansible setup |
| **[Part 3](03-basic-installation.md)** | Basic Installation | Deploy your first runner step-by-step |
| **[Part 4](04-runner-types.md)** | Runner Types | Instance, Group, and Project runners explained |
| **[Part 5](05-advanced-features.md)** | Advanced Features | Tag management via API, access levels, locked runners |
| **[Part 6](06-production-deployment.md)** | Production Deployment | Multi-runner setups, auto-create groups, performance tuning |
| **[Part 7](07-security.md)** | Security Best Practices | Token protection, Vault usage, runner isolation |
| **[Part 8](08-troubleshooting.md)** | Troubleshooting | Common errors, service issues, verification commands |

---

## 🎯 Quick Start

**New to GitLab CI Runners?** Start with [Part 1 - Introduction](01-introduction.md) to understand the concepts.

**Ready to deploy?** Jump to [Part 3 - Basic Installation](03-basic-installation.md).

**Need production setup?** See [Part 6 - Production Deployment](06-production-deployment.md).

---

## 🔗 Related Resources

### Role Documentation
- [Role README](../../roles/gitlab_ci_runners/README.md) - Quick reference and API documentation

### Example Playbooks
- [Production Installation](../../playbooks/gitlab_ci_runners/install-production.yml) - Complete production example

### Collection Documentation
- [Main Collection README](../../README.md) - Overview of all roles
- [Role README](../../roles/gitlab_ci_runners/README.md) - Complete variable reference
- [FAQ](../FAQ.md) - Frequently asked questions

---

## 💡 How to Use This Guide

### For Beginners
1. Read **Part 1** to understand concepts
2. Follow **Part 2** to prepare your environment
3. Complete **Part 3** to deploy your first runner
4. Explore **Parts 4-6** to expand your deployment

### For Experienced Users
- Jump directly to **Part 6** for production patterns
- Use **Part 5** for API management and advanced features
- Reference **Part 8** when troubleshooting

### For Video Tutorial Creation
- Each part is designed as a standalone video (10-15 minutes)
- Visual diagrams can be converted to animations
- Step-by-step sections translate well to screen recordings

---

[← Back to User Guides](../README.md)
