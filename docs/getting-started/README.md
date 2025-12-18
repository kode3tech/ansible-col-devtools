# Getting Started

Welcome to the **code3tech.devtools** collection! This guide will take you from installation to production-ready deployments.

## 📚 Documentation

Follow these guides in order for the best learning experience:

| Guide | Description | You'll Learn |
|-------|-------------|--------------|
| **[1. Installation](01-installation.md)** | Install collection and dependencies | How to get the collection on your system |
| **[2. First Playbook](02-first-playbook.md)** | Run your first deployment | Deploy Docker, Podman, or CI runners |
| **[3. Inventory Basics](03-inventory-basics.md)** | Organize your infrastructure | Manage hosts, groups, and variables |
| **[4. Using Roles](04-using-roles.md)** | Explore all collection roles | Docker, Podman, CI runners, asdf |
| **[5. Common Patterns](05-common-patterns.md)** | Production-ready patterns | Multi-env, vault, tags, templates |
| **[6. Troubleshooting](06-troubleshooting.md)** | Fix common issues | Debug and resolve execution problems |

## 🎯 Recommended Path

### New to this collection? Start here:

1. ✅ **Install the collection** - [Installation Guide](01-installation.md)
2. ✅ **Deploy something** - [First Playbook](02-first-playbook.md)
3. ✅ **Organize hosts** - [Inventory Basics](03-inventory-basics.md)
4. ✅ **Explore all roles** - [Using Roles](04-using-roles.md)

### Ready for production?

5. ✅ **Learn patterns** - [Common Patterns](05-common-patterns.md)
6. ✅ **Debug issues** - [Troubleshooting](06-troubleshooting.md)

## 🚀 Quick Start

**Want to jump right in?** Install and deploy in 5 minutes:

```bash
# 1. Install collection
ansible-galaxy collection install code3tech.devtools

# 2. Create inventory
cat > inventory.yml <<EOF
all:
  hosts:
    server1:
      ansible_host: 192.168.1.100
EOF

# 3. Create playbook
cat > docker.yml <<EOF
- hosts: all
  become: true
  roles:
    - code3tech.devtools.docker
EOF

# 4. Deploy!
ansible-playbook docker.yml -i inventory.yml
```

**[Continue with First Playbook →](02-first-playbook.md)**

## 🔗 Additional Resources

- **[Main Documentation](../README.md)** - Collection overview
- **[User Guides](../user-guides/README.md)** - Deep dives into specific roles
- **[Variables Reference](../reference/VARIABLES.md)** - Complete variable documentation
- **[FAQ](../FAQ.md)** - Frequently asked questions

## 📞 Need Help?

- **Issues**: Can't connect? Check [Troubleshooting](06-troubleshooting.md)
- **Questions**: See our [FAQ](../FAQ.md)
- **Bugs**: Report on [GitHub Issues](https://github.com/kode3tech/ansible-col-devtools/issues)

---

[← Back to Documentation](../README.md)
